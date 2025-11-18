"""
IMPROVED Modal inference endpoint for DNABERT-2 variant pathogenicity prediction
Now with real genomic context and gnomAD integration
"""
import modal
from typing import Dict, Optional, Tuple
from pydantic import BaseModel

app = modal.App("evomed-lightweight-inference-v2")

# Create Modal image with additional dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch>=2.0.0",
        "transformers>=4.35.0",
        "peft>=0.6.0",
        "fastapi>=0.104.0",
        "pydantic>=2.0.0",
        "requests>=2.31.0",  # For API calls
    )
    # Copy our service files
    .copy_local_file(
        "../services/genomic_sequence.py",
        "/root/genomic_sequence.py"
    )
    .copy_local_file(
        "../services/gnomad_api.py",
        "/root/gnomad_api.py"
    )
)

# Volume with trained model
model_volume = modal.Volume.from_name("evomed-trained-models", create_if_missing=True)

# Request/Response models
class VariantRequest(BaseModel):
    """Variant analysis request"""
    chromosome: str
    position: int
    ref: str
    alt: str
    apply_african_adjustment: bool = True
    use_real_genomic_context: bool = True  # New option

class VariantResponse(BaseModel):
    """Variant analysis response"""
    chromosome: str
    position: int
    ref: str
    alt: str
    prediction: str  # "Pathogenic" or "Benign"
    confidence: float  # 0-1
    raw_score: float  # Raw model output
    adjusted_score: Optional[float] = None  # After African adjustment
    african_frequency: Optional[float] = None
    gnomad_data: Optional[Dict] = None  # Full gnomAD population data
    used_real_context: bool = False  # Whether real genomic data was used
    model_version: str = "dnabert2-brca1-v2"

@app.cls(
    image=image,
    gpu="T4",  # Smaller GPU for inference
    volumes={"/models": model_volume},
    container_idle_timeout=600,  # Keep warm for 10 minutes (increased)
)
class VariantClassifier:
    """DNABERT-2 variant classifier service with real genomic context"""

    @modal.enter()
    def load_model(self):
        """Load model and initialize services on container startup"""
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        import sys

        # Add current directory to path
        sys.path.insert(0, "/root")

        # Import our services
        from genomic_sequence import GenomicSequenceFetcher
        from gnomad_api import GnomADAPI

        print("🔄 Loading DNABERT-2 model...")

        model_path = "/models/dnabert2-brca1-final"

        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(
            "zhihan1996/DNABERT-2-117M",  # Use base model if fine-tuned not available
            trust_remote_code=True
        )

        try:
            self.model = AutoModelForSequenceClassification.from_pretrained(
                model_path,
                trust_remote_code=True,
            )
            print(f"✅ Loaded fine-tuned model from {model_path}")
        except Exception as e:
            print(f"⚠️  Could not load fine-tuned model: {e}")
            print("   Loading base model for testing...")
            self.model = AutoModelForSequenceClassification.from_pretrained(
                "zhihan1996/DNABERT-2-117M",
                num_labels=2,
                trust_remote_code=True,
            )

        # Move to GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()

        # Initialize genomic services
        self.genomic_fetcher = GenomicSequenceFetcher()
        self.gnomad_api = GnomADAPI(cache_enabled=True)

        print(f"✅ Model loaded on {self.device}")
        print("✅ Genomic sequence fetcher initialized")
        print("✅ gnomAD API client initialized")

    def prepare_sequences_with_context(
        self,
        chromosome: str,
        position: int,
        ref: str,
        alt: str,
        use_real_context: bool = True,
        max_length: int = 512
    ) -> Tuple[str, str, bool]:
        """
        Prepare both REF and ALT sequences with real genomic context

        Returns:
            (ref_sequence, alt_sequence, used_real_context)
        """
        if use_real_context:
            # Try to fetch real genomic context
            ref_seq, alt_seq, metadata = self.genomic_fetcher.prepare_model_input(
                chromosome=chromosome,
                position=position,
                ref=ref,
                alt=alt,
                max_length=max_length,
                context_size=256  # 256bp on each side
            )

            if metadata['has_real_context']:
                return ref_seq, alt_seq, True

        # Fallback to simple padding
        context_size = max_length // 4
        padding = 'N' * context_size

        ref_seq = padding + ref.upper() + padding
        alt_seq = padding + alt.upper() + padding

        # Pad to max_length
        if len(ref_seq) < max_length:
            pad_needed = max_length - len(ref_seq)
            ref_seq += 'N' * pad_needed
            alt_seq += 'N' * pad_needed

        return ref_seq[:max_length], alt_seq[:max_length], False

    def get_african_frequency(
        self,
        chromosome: str,
        position: int,
        ref: str,
        alt: str
    ) -> Tuple[Optional[float], Optional[Dict]]:
        """
        Get African population frequency from gnomAD

        Returns:
            (african_frequency, full_gnomad_data)
        """
        # Get African-specific frequency
        af_afr = self.gnomad_api.get_african_frequency(
            chromosome, position, ref, alt
        )

        # Get full population summary for additional context
        gnomad_summary = self.gnomad_api.get_population_summary(
            chromosome, position, ref, alt
        )

        return af_afr, gnomad_summary

    def apply_african_adjustment(
        self,
        score: float,
        af_afr: Optional[float]
    ) -> float:
        """
        Apply African population-aware adjustment to pathogenicity score

        Uses ACMG/AMP guidelines:
        - High frequency (>5%): Strong benign evidence
        - Moderate frequency (1-5%): Moderate benign evidence
        - Low frequency (0.5-1%): Mild benign evidence
        """
        if af_afr is None:
            return score

        # Adjustment thresholds
        if af_afr > 0.05:  # > 5%
            adjustment = -0.20  # Strong benign evidence
        elif af_afr > 0.01:  # > 1%
            adjustment = -0.12  # Moderate evidence
        elif af_afr > 0.005:  # > 0.5%
            adjustment = -0.06  # Mild evidence
        else:
            adjustment = 0.0

        adjusted_score = max(0.0, min(1.0, score + adjustment))
        return adjusted_score

    @modal.method()
    def predict(self, variant: VariantRequest) -> VariantResponse:
        """
        Predict variant pathogenicity with real genomic context
        """
        import torch
        import torch.nn.functional as F

        print(f"\n🔬 Analyzing variant: chr{variant.chromosome}:{variant.position} {variant.ref}>{variant.alt}")

        # Prepare sequences with real genomic context
        ref_seq, alt_seq, used_real_context = self.prepare_sequences_with_context(
            chromosome=variant.chromosome,
            position=variant.position,
            ref=variant.ref,
            alt=variant.alt,
            use_real_context=variant.use_real_genomic_context
        )

        print(f"   Context: {'Real genomic' if used_real_context else 'N-padding fallback'}")

        # For now, we'll use the ALT sequence (can be enhanced to compare REF vs ALT)
        # TODO: Implement dual-sequence comparison for better accuracy
        sequence = alt_seq

        # Tokenize
        inputs = self.tokenizer(
            sequence,
            padding='max_length',
            truncation=True,
            max_length=512,
            return_tensors='pt',
        )

        # Move to device
        inputs = {k: v.to(self.device) for k, v in inputs.items()}

        # Inference
        with torch.no_grad():
            outputs = self.model(**inputs)
            logits = outputs.logits
            probs = F.softmax(logits, dim=-1)

            # Get pathogenic probability (class 1)
            pathogenic_prob = probs[0][1].item()

        print(f"   Raw score: {pathogenic_prob:.4f}")

        # Get African frequency (if enabled)
        af_afr = None
        gnomad_data = None
        adjusted_score = None

        if variant.apply_african_adjustment:
            af_afr, gnomad_data = self.get_african_frequency(
                variant.chromosome,
                variant.position,
                variant.ref,
                variant.alt
            )

            if af_afr is not None:
                print(f"   African frequency: {af_afr:.6f} ({af_afr * 100:.4f}%)")
                adjusted_score = self.apply_african_adjustment(pathogenic_prob, af_afr)
                print(f"   Adjusted score: {adjusted_score:.4f}")
            else:
                print("   African frequency: Not found in gnomAD")
                adjusted_score = pathogenic_prob
        else:
            adjusted_score = pathogenic_prob

        # Final score for prediction
        final_score = adjusted_score if adjusted_score is not None else pathogenic_prob

        # Classification
        prediction = "Pathogenic" if final_score > 0.5 else "Benign"
        confidence = final_score if final_score > 0.5 else (1 - final_score)

        print(f"   Prediction: {prediction} (confidence: {confidence:.4f})")

        return VariantResponse(
            chromosome=variant.chromosome,
            position=variant.position,
            ref=variant.ref,
            alt=variant.alt,
            prediction=prediction,
            confidence=confidence,
            raw_score=pathogenic_prob,
            adjusted_score=adjusted_score,
            african_frequency=af_afr,
            gnomad_data=gnomad_data,
            used_real_context=used_real_context,
        )

@app.function(image=image)
@modal.web_endpoint(method="POST")
def predict_variant(variant: VariantRequest) -> VariantResponse:
    """
    Web endpoint for variant prediction
    """
    classifier = VariantClassifier()
    return classifier.predict.remote(variant)

@app.local_entrypoint()
def test_inference():
    """Test the improved inference endpoint"""
    print("=" * 70)
    print("🧪 Testing IMPROVED DNABERT-2 Inference")
    print("=" * 70)

    # Test variants
    test_variants = [
        {
            "name": "BRCA1 Known Pathogenic",
            "chromosome": "17",
            "position": 43045677,
            "ref": "G",
            "alt": "A",
        },
        {
            "name": "BRCA1 Common Benign",
            "chromosome": "17",
            "position": 43044295,
            "ref": "G",
            "alt": "A",
        }
    ]

    classifier = VariantClassifier()

    for test_var in test_variants:
        print(f"\n{'=' * 70}")
        print(f"Test: {test_var['name']}")
        print(f"Variant: chr{test_var['chromosome']}:{test_var['position']} {test_var['ref']}>{test_var['alt']}")
        print("=" * 70)

        variant_request = VariantRequest(
            chromosome=test_var["chromosome"],
            position=test_var["position"],
            ref=test_var["ref"],
            alt=test_var["alt"],
            apply_african_adjustment=True,
            use_real_genomic_context=True,
        )

        result = classifier.predict.remote(variant_request)

        print(f"\n📊 Results:")
        print(f"   Prediction: {result.prediction}")
        print(f"   Confidence: {result.confidence:.4f}")
        print(f"   Raw Score: {result.raw_score:.4f}")
        if result.adjusted_score is not None:
            print(f"   Adjusted Score: {result.adjusted_score:.4f}")
        if result.african_frequency is not None:
            print(f"   African Frequency: {result.african_frequency:.6f}")
        print(f"   Used Real Context: {result.used_real_context}")

        if result.gnomad_data and result.gnomad_data.get("found"):
            print(f"\n🌍 Population Frequencies:")
            print(f"   Global: {result.gnomad_data['global']['af']:.6f}" if result.gnomad_data['global']['af'] else "   Global: N/A")
            print(f"   African: {result.gnomad_data['african']:.6f}" if result.gnomad_data['african'] else "   African: N/A")

    print("\n" + "=" * 70)
    print("✅ Improved inference test complete!")
    print("=" * 70)

if __name__ == "__main__":
    test_inference()
