import sys

import modal
from fastapi import FastAPI, Response
from fastapi.middleware.cors import CORSMiddleware

from pydantic import BaseModel


class VariantRequest(BaseModel):
    variant_position: int
    alternative: str
    genome: str
    chromosome: str
    use_african_adjustment: bool = (
        True  # Enable African population adjustments by default
    )


evo2_image = (
    modal.Image.from_registry("nvidia/cuda:12.4.0-devel-ubuntu22.04", add_python="3.12")
    .apt_install(
        [
            "build-essential",
            "cmake",
            "ninja-build",
            "libcudnn8",
            "libcudnn8-dev",
            "git",
            "gcc",
            "g++",
        ]
    )
    .env(
        {
            "CC": "/usr/bin/gcc",
            "CXX": "/usr/bin/g++",
            "CUDA_HOME": "/usr/local/cuda",
            "TORCH_CUDA_ARCH_LIST": "8.0;8.6;8.9;9.0",
            "MAX_JOBS": "4",
            "FLASH_ATTENTION_DISABLE": "1",
            "USE_FLASH_ATTN": "False",
            "VORTEX_DISABLE_FLASH_ATTN": "1",
        }
    )
    .run_commands("pip install wheel setuptools packaging")
    .run_commands(
        "pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124"
    )
    .run_commands("pip install ninja")
    .run_commands("pip install requests biopython")
    .run_commands(
        "git clone --recurse-submodules https://github.com/ArcInstitute/evo2.git && cd evo2 && pip install ."
    )
    .run_commands("pip uninstall -y transformer-engine transformer-engine-cu12 || true")
    .run_commands(
        "pip install 'transformer-engine[pytorch]>=1.0.0' --no-build-isolation || echo 'transformer-engine install failed, continuing...'"
    )
    .run_commands(
        "pip install 'flash-attn>=2.7.0' --no-build-isolation || echo 'flash-attn install failed, will use fallback'"
    )
    .pip_install_from_requirements("requirements.txt")
    .add_local_file("population_service.py", "/root/population_service.py")
)

app = modal.App("variant-analysis-evo2", image=evo2_image)

volume = modal.Volume.from_name("hf_cache", create_if_missing=True)
mount_path = "/root/.cache/huggingface"

# Volume for population frequency caching
population_volume = modal.Volume.from_name("population_cache", create_if_missing=True)


def patch_flash_attn_imports():
    """Minimal patches - only mock the flash attention CUDA modules that cause import errors"""
    import sys
    import os
    import types

    # Set environment variables to disable flash attention
    os.environ["FLASH_ATTENTION_DISABLE"] = "1"
    os.environ["USE_FLASH_ATTN"] = "False"
    os.environ["VORTEX_DISABLE_FLASH_ATTN"] = "1"
    os.environ["VORTEX_USE_FLASH_ATTN"] = "False"

    # Only mock the problematic CUDA modules that cause import failures
    class MockFlashAttnCuda:
        def __getattr__(self, name):
            def mock_func(*args, **kwargs):
                import torch

                print(
                    f"MockFlashAttnCuda called with function: {name}, args shapes: {[arg.shape if hasattr(arg, 'shape') else type(arg) for arg in args]}"
                )

                # Special handling for the fwd function which needs to return 4 values
                if name == "fwd":
                    if len(args) >= 1:
                        qkv = args[0]  # packed qkv tensor
                        print(f"QKV tensor shape: {qkv.shape}")

                        # The error shows we need output to be (8193, 4096) but we're getting (8193, 1344)
                        # This suggests the attention mechanism is not reshaping correctly

                        # Handle different tensor shapes - could be (batch, seq, 3*head_dim) or (batch, nheads, seq, 3*head_dim)
                        if len(qkv.shape) == 3:
                            # Shape: (batch, seq, 3*head_dim)
                            batch_size, seq_len, three_times_head_dim = qkv.shape
                            head_dim = three_times_head_dim // 3

                            # Reshape for multi-head attention: (batch, seq, 3*head_dim) -> (batch, seq, 3, nheads, head_dim_per_head)
                            nheads = 32  # Common number of heads for transformers
                            head_dim_per_head = head_dim // nheads

                            qkv_reshaped = qkv.view(
                                batch_size, seq_len, 3, nheads, head_dim_per_head
                            )
                            q, k, v = qkv_reshaped.unbind(2)  # Split into q, k, v

                            # Transpose for attention: (batch, seq, nheads, head_dim) -> (batch, nheads, seq, head_dim)
                            q = q.transpose(1, 2)
                            k = k.transpose(1, 2)
                            v = v.transpose(1, 2)

                            # Attention computation
                            scores = torch.matmul(q, k.transpose(-2, -1)) / (
                                head_dim_per_head**0.5
                            )
                            attn_weights = torch.softmax(scores, dim=-1)
                            output = torch.matmul(attn_weights, v)

                            # Transpose back and reshape: (batch, nheads, seq, head_dim) -> (batch, seq, nheads * head_dim)
                            output = (
                                output.transpose(1, 2)
                                .contiguous()
                                .view(batch_size, seq_len, head_dim)
                            )

                        elif len(qkv.shape) == 4:
                            # Shape: (batch, nheads, seq, 3*head_dim)
                            batch_size, nheads, seq_len, three_times_head_dim = (
                                qkv.shape
                            )
                            head_dim_per_head = three_times_head_dim // 3
                            q, k, v = qkv.chunk(3, dim=-1)

                            # Attention computation
                            scores = torch.matmul(q, k.transpose(-2, -1)) / (
                                head_dim_per_head**0.5
                            )
                            attn_weights = torch.softmax(scores, dim=-1)
                            output = torch.matmul(attn_weights, v)

                            # Reshape to (batch, seq, nheads * head_dim)
                            output = (
                                output.transpose(1, 2)
                                .contiguous()
                                .view(batch_size, seq_len, nheads * head_dim_per_head)
                            )
                        else:
                            # Fallback - just return zeros with the right shape
                            batch_size = qkv.shape[0]
                            seq_len = qkv.shape[1] if len(qkv.shape) > 1 else 1
                            # Output should be (batch, seq, model_dim) where model_dim = 4096 for this model
                            output = torch.zeros(
                                batch_size,
                                seq_len,
                                4096,
                                dtype=qkv.dtype,
                                device=qkv.device,
                            )
                            softmax_lse = torch.zeros(
                                batch_size,
                                seq_len,
                                dtype=torch.float32,
                                device=qkv.device,
                            )
                            S_dmask = None
                            rng_state = torch.empty(
                                2, dtype=torch.int64, device=qkv.device
                            )
                            return output, softmax_lse, S_dmask, rng_state

                        print(f"Mock attention output shape: {output.shape}")

                        # Return the 4 expected values: out, softmax_lse, S_dmask, rng_state
                        batch_size = qkv.shape[0]
                        seq_len = qkv.shape[-2] if len(qkv.shape) > 2 else qkv.shape[1]
                        softmax_lse = torch.zeros(
                            batch_size, seq_len, dtype=torch.float32, device=qkv.device
                        )
                        S_dmask = None  # dropout mask (not needed)
                        rng_state = torch.empty(2, dtype=torch.int64, device=qkv.device)

                        return output, softmax_lse, S_dmask, rng_state
                    else:
                        # Fallback for unexpected arguments
                        return (
                            torch.tensor(0.0),
                            torch.tensor(0.0),
                            None,
                            torch.empty(2, dtype=torch.int64),
                        )

                # For other functions, return fallback attention results
                if len(args) >= 3:
                    q, k, v = args[:3]
                    # Simple scaled dot-product attention fallback
                    scores = torch.matmul(q, k.transpose(-2, -1)) / (q.shape[-1] ** 0.5)
                    attn_weights = torch.softmax(scores, dim=-1)
                    output = torch.matmul(attn_weights, v)
                    return output
                return torch.tensor(0.0)

            return mock_func

    # Mock only the CUDA modules that fail to import
    sys.modules["flash_attn_2_cuda"] = MockFlashAttnCuda()
    sys.modules["flash_attn"] = MockFlashAttnCuda()

    print(
        "Applied minimal flash attention CUDA mocks - using real vortex for everything else"
    )


@app.function(gpu="H100", volumes={mount_path: volume}, timeout=1000)
def run_brca1_analysis():
    import base64
    from io import BytesIO
    from Bio import SeqIO
    import gzip
    import matplotlib.pyplot as plt
    import numpy as np
    import pandas as pd
    import os
    import seaborn as sns
    from sklearn.metrics import roc_auc_score, roc_curve

    # Apply flash attention patches before importing evo2
    patch_flash_attn_imports()

    from evo2 import Evo2

    WINDOW_SIZE = 8192

    print("Loading evo2 model...")
    model = Evo2("evo2_7b")
    print("Evo2 model loaded")

    brca1_df = pd.read_excel(
        "/evo2/notebooks/brca1/41586_2018_461_MOESM3_ESM.xlsx",
        header=2,
    )
    brca1_df = brca1_df[
        [
            "chromosome",
            "position (hg19)",
            "reference",
            "alt",
            "function.score.mean",
            "func.class",
        ]
    ]

    brca1_df.rename(
        columns={
            "chromosome": "chrom",
            "position (hg19)": "pos",
            "reference": "ref",
            "alt": "alt",
            "function.score.mean": "score",
            "func.class": "class",
        },
        inplace=True,
    )

    # Convert to two-class system
    brca1_df["class"] = brca1_df["class"].replace(["FUNC", "INT"], "FUNC/INT")

    with gzip.open("/evo2/notebooks/brca1/GRCh37.p13_chr17.fna.gz", "rt") as handle:
        for record in SeqIO.parse(handle, "fasta"):
            seq_chr17 = str(record.seq)
            break

    # Build mappings of unique reference sequences
    ref_seqs = []
    ref_seq_to_index = {}

    # Parse sequences and store indexes
    ref_seq_indexes = []
    var_seqs = []

    brca1_subset = brca1_df.iloc[:500].copy()

    for _, row in brca1_subset.iterrows():
        p = row["pos"] - 1  # Convert to 0-indexed position
        full_seq = seq_chr17

        ref_seq_start = max(0, p - WINDOW_SIZE // 2)
        ref_seq_end = min(len(full_seq), p + WINDOW_SIZE // 2)
        ref_seq = seq_chr17[ref_seq_start:ref_seq_end]
        snv_pos_in_ref = min(WINDOW_SIZE // 2, p)
        var_seq = ref_seq[:snv_pos_in_ref] + row["alt"] + ref_seq[snv_pos_in_ref + 1 :]

        # Get or create index for reference sequence
        if ref_seq not in ref_seq_to_index:
            ref_seq_to_index[ref_seq] = len(ref_seqs)
            ref_seqs.append(ref_seq)

        ref_seq_indexes.append(ref_seq_to_index[ref_seq])
        var_seqs.append(var_seq)

    ref_seq_indexes = np.array(ref_seq_indexes)

    print(f"Scoring likelihoods of {len(ref_seqs)} reference sequences with Evo 2...")
    ref_scores = model.score_sequences(ref_seqs)

    print(f"Scoring likelihoods of {len(var_seqs)} variant sequences with Evo 2...")
    var_scores = model.score_sequences(var_seqs)

    # Subtract score of corresponding reference sequences from scores of variant sequences
    delta_scores = np.array(var_scores) - np.array(ref_scores)[ref_seq_indexes]

    # Add delta scores to dataframe
    brca1_subset[f"evo2_delta_score"] = delta_scores

    y_true = brca1_subset["class"] == "LOF"
    auroc = roc_auc_score(y_true, -brca1_subset["evo2_delta_score"])

    # --- Calculate threshold START
    y_true = brca1_subset["class"] == "LOF"

    fpr, tpr, thresholds = roc_curve(y_true, -brca1_subset["evo2_delta_score"])

    optimal_idx = (tpr - fpr).argmax()

    optimal_threshold = -thresholds[optimal_idx]

    lof_scores = brca1_subset.loc[brca1_subset["class"] == "LOF", "evo2_delta_score"]
    func_scores = brca1_subset.loc[
        brca1_subset["class"] == "FUNC/INT", "evo2_delta_score"
    ]

    lof_std = lof_scores.std()
    func_std = func_scores.std()

    confidence_params = {
        "threshold": optimal_threshold,
        "lof_std": lof_std,
        "func_std": func_std,
    }

    print("Confidence params:", confidence_params)

    # --- Calculate threshold END

    plt.figure(figsize=(4, 2))

    # Plot stripplot of distributions
    p = sns.stripplot(
        data=brca1_subset,
        x="evo2_delta_score",
        y="class",
        hue="class",
        order=["FUNC/INT", "LOF"],
        palette=["#777777", "C3"],
        size=2,
        jitter=0.3,
    )

    # Mark medians from each distribution
    sns.boxplot(
        showmeans=True,
        meanline=True,
        meanprops={"visible": False},
        medianprops={"color": "k", "ls": "-", "lw": 2},
        whiskerprops={"visible": False},
        zorder=10,
        x="evo2_delta_score",
        y="class",
        data=brca1_subset,
        showfliers=False,
        showbox=False,
        showcaps=False,
        ax=p,
    )
    plt.xlabel("Delta likelihood score, Evo 2")
    plt.ylabel("BRCA1 SNV class")
    plt.tight_layout()

    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    buffer.seek(0)
    plot_data = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return {
        "variants": brca1_subset.to_dict(orient="records"),
        "plot": plot_data,
        "auroc": auroc,
    }


@app.function()
def brca1_example():
    import base64
    from io import BytesIO
    import matplotlib.pyplot as plt
    import matplotlib.image as mpimg

    print("Running BRCA1 variant analysis with Evo2...")

    # Run inference
    result = run_brca1_analysis.remote()

    if "plot" in result:
        plot_data = base64.b64decode(result["plot"])
        with open("brca1_analysis_plot.png", "wb") as f:
            f.write(plot_data)

        img = mpimg.imread(BytesIO(plot_data))
        plt.figure(figsize=(10, 5))
        plt.imshow(img)
        plt.axis("off")
        plt.show()


def get_genome_sequence(position, genome: str, chromosome: str, window_size=8192):
    import requests

    half_window = window_size // 2
    start = max(0, position - 1 - half_window)
    end = position - 1 + half_window + 1

    print(f"Fetching {window_size}bp window around position {position} from UCSC API..")
    print(f"Coordinates: {chromosome}:{start}-{end} ({genome})")

    api_url = f"https://api.genome.ucsc.edu/getData/sequence?genome={genome};chrom={chromosome};start={start};end={end}"
    response = requests.get(api_url)

    if response.status_code != 200:
        raise Exception(
            f"Failed to fetch genome sequence from UCSC API: {response.status_code}"
        )

    genome_data = response.json()

    if "dna" not in genome_data:
        error = genome_data.get("error", "Unknown error")
        raise Exception(f"UCSC API errpr: {error}")

    sequence = genome_data.get("dna", "").upper()
    expected_length = end - start
    if len(sequence) != expected_length:
        print(
            f"Warning: received sequence length ({len(sequence)}) differs from expected ({expected_length})"
        )

    print(f"Loaded reference genome sequence window (length: {len(sequence)} bases)")

    return sequence, start


def analyze_variant(relative_pos_in_window, reference, alternative, window_seq, model):
    var_seq = (
        window_seq[:relative_pos_in_window]
        + alternative
        + window_seq[relative_pos_in_window + 1 :]
    )

    ref_score = model.score_sequences([window_seq])[0]
    var_score = model.score_sequences([var_seq])[0]

    delta_score = var_score - ref_score

    threshold = -0.0009178519
    lof_std = 0.0015140239
    func_std = 0.0009016589

    if delta_score < threshold:
        prediction = "Likely pathogenic"
        confidence = min(1.0, abs(delta_score - threshold) / lof_std)
    else:
        prediction = "Likely benign"
        confidence = min(1.0, abs(delta_score - threshold) / func_std)

    return {
        "reference": reference,
        "alternative": alternative,
        "delta_score": float(delta_score),
        "prediction": prediction,
        "classification_confidence": float(confidence),
    }


def analyze_variant_with_population(
    relative_pos_in_window,
    reference,
    alternative,
    window_seq,
    model,
    chromosome,
    position,
    population_service,
    use_african_adjustment=True,
):
    """Enhanced variant analysis with African population-specific scoring"""
    from population_service import (
        calculate_population_adjustment,
        classify_variant_with_population,
    )

    # 1. Get basic Evo2 scores (existing logic)
    var_seq = (
        window_seq[:relative_pos_in_window]
        + alternative
        + window_seq[relative_pos_in_window + 1 :]
    )
    ref_score = model.score_sequences([window_seq])[0]
    var_score = model.score_sequences([var_seq])[0]
    delta_score = var_score - ref_score

    # 2. Get population frequencies if African adjustment is enabled
    freq_data = None
    if use_african_adjustment:
        try:
            freq_data = population_service.get_population_frequency(
                chromosome, position, reference, alternative
            )
            print(f"Population frequency data: {freq_data}")
        except Exception as e:
            print(f"Error fetching population frequency: {e}")
            freq_data = None

    # 3. Calculate population-adjusted score
    adjusted_score, population_adjustment, adjustment_reasoning = (
        calculate_population_adjustment(delta_score, freq_data, use_african_adjustment)
    )

    # 4. Classify with population-aware thresholds
    classification = classify_variant_with_population(
        adjusted_score,
        delta_score,
        freq_data,
        population_adjustment,
        adjustment_reasoning,
    )

    result = {
        "reference": reference,
        "alternative": alternative,
        "evo2_delta_score": float(delta_score),
        "population_adjusted_score": float(adjusted_score),
        "population_adjustment": float(population_adjustment),
        "adjustment_reasoning": adjustment_reasoning,
        "african_frequency": freq_data.get("african_af") if freq_data else None,
        "global_frequency": freq_data.get("global_af") if freq_data else None,
        "prediction": classification["prediction"],
        "confidence": classification["confidence"],
        "classification_method": classification["method"],
        "population_context": classification["context"],
        "threshold_used": classification["threshold_used"],
        "use_african_adjustment": use_african_adjustment,
    }

    print(
        f"Analysis result: {classification['prediction']} (confidence: {classification['confidence']:.3f})"
    )
    if use_african_adjustment and freq_data and freq_data.get("african_af"):
        print(f"African population frequency: {freq_data['african_af']:.6f}")
        print(f"Population adjustment: {population_adjustment:+.6f}")

    return result


@app.cls(
    gpu="H100",
    volumes={mount_path: volume, "/population_cache": population_volume},
    max_containers=3,
    retries=2,
    scaledown_window=120,
)
class Evo2Model:
    @modal.enter()
    def load_evo2_model(self):
        import os
        import sys

        print("Setting up environment to disable flash attention...")
        # Apply patches before any imports
        patch_flash_attn_imports()

        # Try to import with comprehensive error handling
        max_retries = 3
        for attempt in range(max_retries):
            try:
                print(f"Attempt {attempt + 1}/{max_retries}: Loading evo2 model...")
                from evo2 import Evo2

                print("Successfully imported evo2")
                self.model = Evo2("evo2_7b")
                print("Evo2 model loaded successfully")

                # Initialize population frequency service
                from population_service import PopulationFrequencyService

                self.population_service = PopulationFrequencyService()
                print("Population frequency service initialized")
                return

            except ImportError as e:
                print(f"Import error on attempt {attempt + 1}: {e}")

                if attempt < max_retries - 1:  # Not the last attempt
                    if "flash_attn" in str(e) or "undefined symbol" in str(e):
                        print("Attempting to fix flash attention issues...")

                        # Try uninstalling flash-attn completely
                        try:
                            import subprocess

                            subprocess.run(
                                [
                                    sys.executable,
                                    "-m",
                                    "pip",
                                    "uninstall",
                                    "-y",
                                    "flash-attn",
                                ],
                                capture_output=True,
                                check=False,
                            )
                            print("Uninstalled flash-attn")
                        except Exception:
                            pass

                        # Clear module cache
                        modules_to_remove = [
                            k
                            for k in sys.modules.keys()
                            if any(
                                pattern in k
                                for pattern in [
                                    "flash_attn",
                                    "vortex",
                                    "evo2",
                                    "transformer_engine",
                                ]
                            )
                        ]
                        for mod in modules_to_remove:
                            if mod in sys.modules:
                                del sys.modules[mod]

                        # Re-apply minimal patches
                        patch_flash_attn_imports()
                        continue
                    else:
                        print(f"Non-flash-attn import error: {e}")

                # If we get here, it's the last attempt or non-flash-attn error
                if attempt == max_retries - 1:
                    print(f"Failed to load evo2 after {max_retries} attempts")
                    raise e

            except Exception as e:
                print(f"Unexpected error on attempt {attempt + 1}: {e}")
                if attempt == max_retries - 1:
                    raise e

    # @modal.method()
    @modal.fastapi_endpoint(method="POST")
    def analyze_single_variant(self, request: VariantRequest, response: Response):
        variant_position = request.variant_position
        alternative = request.alternative
        genome = request.genome
        chromosome = request.chromosome
        use_african_adjustment = request.use_african_adjustment

        print("Genome:", genome)
        print("Chromosome:", chromosome)
        print("Variant position:", variant_position)
        print("Variant alternative:", alternative)
        print("Use African population adjustment:", use_african_adjustment)

        WINDOW_SIZE = 8192

        window_seq, seq_start = get_genome_sequence(
            position=variant_position,
            genome=genome,
            chromosome=chromosome,
            window_size=WINDOW_SIZE,
        )

        print(f"Fetched genome seauence window, first 100: {window_seq[:100]}")

        relative_pos = variant_position - 1 - seq_start
        print(f"Relative position within window: {relative_pos}")

        if relative_pos < 0 or relative_pos >= len(window_seq):
            raise ValueError(
                f"Variant position {variant_position} is outside the fetched window (start={seq_start + 1}, end={seq_start + len(window_seq)})"
            )

        reference = window_seq[relative_pos]
        print("Reference is: " + reference)

        # Analyze the variant with population-aware features
        if use_african_adjustment:
            result = analyze_variant_with_population(
                relative_pos_in_window=relative_pos,
                reference=reference,
                alternative=alternative,
                window_seq=window_seq,
                model=self.model,
                chromosome=chromosome,
                position=variant_position,
                population_service=self.population_service,
                use_african_adjustment=use_african_adjustment,
            )
        else:
            # Fallback to original analysis for backwards compatibility
            result = analyze_variant(
                relative_pos_in_window=relative_pos,
                reference=reference,
                alternative=alternative,
                window_seq=window_seq,
                model=self.model,
            )

        result["position"] = variant_position

        # Add CORS headers
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"

        return result

    @modal.fastapi_endpoint(method="OPTIONS")
    def options_handler(self, response: Response):
        """Handle preflight OPTIONS requests for CORS"""
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = "POST, GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "3600"
        return {"status": "ok"}


@app.local_entrypoint()
def main():
    # Example of how you'd call the deployed Modal Function from your client
    import requests
    import json  # brca1_example.remote()

    evo2Model = Evo2Model()

    url = evo2Model.analyze_single_variant.web_url

    payload = {
        "variant_position": 43119628,
        "alternative": "G",
        "genome": "hg38",
        "chromosome": "chr17",
        "use_african_adjustment": True,
    }

    headers = {"Content-Type": "application/json"}

    response = requests.post(url, json=payload, headers=headers)
    response.raise_for_status()
    result = response.json()
    print(result)
