"""
Modal inference endpoint for DNABERT-2 variant pathogenicity prediction
"""
import modal
from typing import Dict, Optional
from pydantic import BaseModel

app = modal.App("evomed-lightweight-inference")

# Create Modal image
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "torch>=2.0.0",
        "transformers>=4.35.0",
        "peft>=0.6.0",
        "fastapi>=0.104.0",
        "pydantic>=2.0.0",
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
    model_version: str = "dnabert2-brca1-v1"

@app.cls(
    image=image,
    gpu="T4",  # Smaller GPU for inference
    volumes={"/models": model_volume},
    container_idle_timeout=300,  # Keep warm for 5 minutes
)
class VariantClassifier:
    """DNABERT-2 variant classifier service"""

    @modal.enter()
    def load_model(self):
        """Load model on container startup"""
        import torch
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        from peft import PeftModel
        import os

        print("🔄 Loading DNABERT-2 model...")

        model_path = "/models/dnabert2-brca1-final"

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found at {model_path}. "
                "Please train the model first using train_modal.py"
            )

        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, trust_remote_code=True)
        self.model = AutoModelForSequenceClassification.from_pretrained(
            model_path,
            trust_remote_code=True,
        )

        # Move to GPU if available
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()

        print(f"✅ Model loaded on {self.device}")

    def prepare_sequence(self, ref: str, alt: str, max_length: int = 512) -> str:
        """
        Prepare DNA sequence for the model
        This is a simplified version - in production, fetch actual genomic context
        """
        # Pad with N's to create context
        context_size = max_length // 4
        padding = 'N' * context_size

        # Alternate sequence
        sequence = padding + alt + padding

        return sequence

    def get_african_frequency(self, chromosome: str, position: int, alt: str) -> Optional[float]:
        """
        Get African population frequency from gnomAD
        This is a stub - implement actual gnomAD API call
        """
        # TODO: Implement gnomAD API integration
        # For now, return None
        return None

    def apply_african_adjustment(self, score: float, af_afr: Optional[float]) -> float:
        """
        Apply African population-aware adjustment to pathogenicity score
        Similar to the existing EvoMed approach
        """
        if af_afr is None:
            return score

        # Adjustment thresholds (from config)
        if af_afr > 0.05:  # > 5%
            adjustment = -0.15  # Strong benign evidence
        elif af_afr > 0.01:  # > 1%
            adjustment = -0.10  # Moderate evidence
        elif af_afr > 0.005:  # > 0.5%
            adjustment = -0.05  # Mild evidence
        else:
            adjustment = 0.0

        adjusted_score = max(0.0, min(1.0, score + adjustment))
        return adjusted_score

    @modal.method()
    def predict(self, variant: VariantRequest) -> VariantResponse:
        """
        Predict variant pathogenicity
        """
        import torch
        import torch.nn.functional as F

        # Prepare sequence
        sequence = self.prepare_sequence(variant.ref, variant.alt)

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

        # Get African frequency (if available)
        af_afr = None
        adjusted_score = None

        if variant.apply_african_adjustment:
            af_afr = self.get_african_frequency(
                variant.chromosome,
                variant.position,
                variant.alt
            )
            if af_afr is not None:
                adjusted_score = self.apply_african_adjustment(pathogenic_prob, af_afr)
            else:
                adjusted_score = pathogenic_prob
        else:
            adjusted_score = pathogenic_prob

        # Final score for prediction
        final_score = adjusted_score if adjusted_score is not None else pathogenic_prob

        # Classification
        prediction = "Pathogenic" if final_score > 0.5 else "Benign"
        confidence = final_score if final_score > 0.5 else (1 - final_score)

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
    """Test the inference endpoint locally"""
    print("🧪 Testing DNABERT-2 inference...")

    # Test variant
    test_variant = VariantRequest(
        chromosome="17",
        position=43045677,
        ref="G",
        alt="A",
        apply_african_adjustment=True,
    )

    print(f"\nTest variant: chr{test_variant.chromosome}:{test_variant.position} {test_variant.ref}>{test_variant.alt}")

    # Get prediction
    classifier = VariantClassifier()
    result = classifier.predict.remote(test_variant)

    print(f"\n📊 Results:")
    print(f"   Prediction: {result.prediction}")
    print(f"   Confidence: {result.confidence:.4f}")
    print(f"   Raw Score: {result.raw_score:.4f}")
    if result.adjusted_score is not None:
        print(f"   Adjusted Score: {result.adjusted_score:.4f}")
    if result.african_frequency is not None:
        print(f"   African Frequency: {result.african_frequency:.6f}")

    print("\n✅ Inference test complete!")

    return result

if __name__ == "__main__":
    test_inference()
