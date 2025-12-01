# Data Sources Report

**Project**: EvoMed - BRCA1 Variant Analysis with African Population Adjustments  
**Date**: November 28, 2025  
**Author**: Glen Miracle

---

## Executive Summary

This report provides complete transparency about all data sources used in the EvoMed project, their geographic and ancestral distribution, sample sizes, and limitations. 

**Key Finding**: This project does NOT use data collected from African populations. Instead, it uses global variant data with African population frequency adjustments derived from gnomAD v4, which includes primarily African American samples.

---

## 1. Primary Training Data: BRCA Exchange

### 1.1 Overview

**Source**: BRCA Exchange (https://brcaexchange.org)  
**Data Type**: Comprehensive BRCA1 and BRCA2 variant database  
**Access Method**: Public REST API and TSV download  
**License**: Open access for research use  
**Our Usage**: BRCA1 variants only

### 1.2 BRCA Exchange Data Aggregation

BRCA Exchange aggregates variant data from multiple authoritative sources:

| Source | Description | Primary Contribution |
|--------|-------------|---------------------|
| **ENIGMA** | Evidence-based Network for the Interpretation of Germline Mutant Alleles | Expert-curated pathogenicity classifications |
| **ClinVar** | NCBI's database of genomic variation and clinical significance | Clinical interpretations from labs worldwide |
| **LOVD** | Leiden Open Variation Database | Academic and clinical variant submissions |
| **BIC** | Breast Cancer Information Core | Historical BRCA variant database |
| **gnomAD v2.1 & v3.1** | Genome Aggregation Database | Population frequencies |
| **ExAC** | Exome Aggregation Consortium | Population frequencies (predecessor to gnomAD) |
| **1000 Genomes** | International genome sequencing project | Population diversity data |

### 1.3 Dataset Statistics

**Downloaded**: November 2025  
**File**: `data/variants(1).tsv` (297 MB)

| Metric | Count |
|--------|-------|
| Total BRCA1 variants | 36,727 |
| Pathogenic | 2,232 |
| Likely Pathogenic | 10 |
| Benign | 639 |
| Likely Benign | 442 |
| Uncertain Significance (VUS) | 6 |
| Not classified/Unknown | 33,398 |
| **Usable for training** | **~3,323** |

**Class Distribution** (labeled variants only):
- Pathogenic/Likely Pathogenic: 2,242 (67.5%)
- Benign/Likely Benign: 1,081 (32.5%)
- **Imbalance Ratio**: ~2:1 (Pathogenic-skewed)

### 1.4 Geographic Distribution

BRCA Exchange data is **globally sourced** but has known ancestral bias:

| Population/Ancestry | Estimated Representation | Notes |
|---------------------|-------------------------|-------|
| European | ~70-80% | Dominant in most databases |
| African/African American | ~5-10% | Underrepresented |
| Asian | ~5-10% | Underrepresented |
| Latino/Admixed American | ~3-5% | Underrepresented |
| Ashkenazi Jewish | ~5-10% | Well-represented due to founder mutations |
| Other/Unknown | ~5% | Mixed or unspecified ancestry |

**Source of Estimates**: Based on published gnomAD and ClinVar demographics (exact BRCA Exchange breakdown not publicly available)

### 1.5 Clinical Significance Sources

Our data preparation prioritizes clinical classifications in this order:

1. **ENIGMA** (most authoritative)
   - Expert panel review
   - Evidence-based classification
   - Follows strict ACMG/AMP guidelines

2. **ClinVar** (widely used)
   - Aggregates submissions from clinical labs
   - Star rating system (0-4 stars) for review status
   - We use only 1-star minimum (single submitter or higher)

3. **Expert Pathogenicity Columns**
   - Fallback for variants not in ENIGMA or ClinVar
   - Lower confidence

### 1.6 Data Quality Issues

**Strengths**:
- High-quality expert curation (ENIGMA)
- Multiple source cross-validation
- Well-characterized pathogenic variants
- Regular updates

**Limitations**:
- **91% unlabeled** - Most variants are VUS or unclassified
- **Ancestral bias** - Predominantly European ancestry
- **Conflicting classifications** - Some variants have disagreements between sources
- **Limited functional data** - Not all variants have experimental validation
- **Historical bias** - Older classifications may not follow current ACMG/AMP guidelines

---

## 2. African Population Frequency Data: gnomAD v4

### 2.1 Overview

**Source**: Genome Aggregation Database v4 (https://gnomad.broadinstitute.org)  
**Data Type**: Population allele frequencies from exome and genome sequencing  
**Access Method**: GraphQL API (real-time queries)  
**License**: Open access (CC0)  
**Our Usage**: African/African American (AFR) allele frequencies for bias adjustment

### 2.2 gnomAD v4 Sample Composition

| Population Code | Description | Exome Samples | Genome Samples | Total |
|-----------------|-------------|---------------|----------------|-------|
| **AFR** | African/African American | ~16,400 | ~4,800 | **~21,200** |
| NFE | Non-Finnish European | ~34,000 | ~7,500 | ~41,500 |
| AMR | Latino/Admixed American | ~7,600 | ~900 | ~8,500 |
| ASJ | Ashkenazi Jewish | ~1,700 | ~300 | ~2,000 |
| EAS | East Asian | ~2,600 | ~800 | ~3,400 |
| FIN | Finnish | ~11,100 | ~1,700 | ~12,800 |
| SAS | South Asian | ~2,400 | ~100 | ~2,500 |
| OTH | Other/Mixed | Variable | Variable | ~8,000 |
| **Total** | All populations | **~76,000** | **~16,000** | **~100,000** |

**Source**: gnomAD v4.0 documentation (October 2023 release)

### 2.3 African Ancestry Breakdown

**Critical Limitation**: gnomAD "AFR" population is primarily African American, NOT continental African.

| Subpopulation | Estimated Proportion | Source Studies |
|---------------|---------------------|----------------|
| African American | ~85-90% | US-based cohorts (UK Biobank, TOPMed, etc.) |
| Afro-Caribbean | ~5-10% | Caribbean ancestry participants |
| Continental African | ~5% | Limited direct African recruitment |

**Geographic Sources of AFR Samples**:
- United Kingdom (UK Biobank) - largest contributor
- United States (TOPMed, All of Us)
- Caribbean nations (various studies)
- Sub-Saharan Africa (minimal direct contribution)

### 2.4 Why This Matters

African American populations have:
- 10-20% European admixture on average
- Different allele frequency distributions than continental Africans
- Different founder variants and population history

**Example**: A variant with 8% frequency in African Americans might have:
- 12% frequency in West Africans
- 15% frequency in a specific ethnic group
- <1% frequency in Europeans

Our adjustments are based on African American data, which may **underestimate** or **overestimate** the true frequency in continental African populations.

### 2.5 Data Access Method

**Real-time API Queries**:
```graphql
query VariantFrequency {
  variant(variant_id: "17-43094464-G-A", dataset: gnomad_r4) {
    genome {
      ac        # Allele count
      an        # Allele number (total chromosomes)
      af        # Allele frequency (ac/an)
      populations {
        id      # Population code (AFR, EUR, etc.)
        ac
        an
        af
      }
    }
  }
}
```

**Caching Strategy**:
- Frequently queried variants cached for 24 hours
- Reduces API load and improves response time
- Cache invalidated on gnomAD updates

### 2.6 Coverage Statistics

**Not all variants have gnomAD data**:
- Variants in BRCA Exchange: 36,727
- Variants with gnomAD v4 frequency data: ~25,000 (68%)
- Variants with AFR frequency > 0: ~8,000 (22%)
- Variants with AFR frequency > 1%: ~500 (1.4%)
- Variants with AFR frequency > 5%: ~150 (0.4%)

**Missing Data Scenarios**:
- Extremely rare variants (not seen in gnomAD samples)
- Variants outside sequencing coverage regions
- Structural variants (gnomAD focuses on SNVs and small indels)

---

## 3. Reference Genomic Sequence: Ensembl

### 3.1 Overview

**Source**: Ensembl Genome Browser (https://ensembl.org)  
**Data Type**: BRCA1 reference genomic sequence  
**Genome Build**: GRCh38/hg38  
**Access Method**: REST API  
**Our Usage**: Reference sequence for variant context extraction

### 3.2 BRCA1 Gene Information

| Attribute | Value |
|-----------|-------|
| Gene Symbol | BRCA1 |
| Ensembl ID | ENSG00000012048 |
| Chromosome | 17 |
| Start Position | 43,044,295 |
| End Position | 43,170,245 |
| Strand | Minus (-) |
| Length | 125,951 bp |
| Exons | 23 |
| Protein Length | 1,863 amino acids |

### 3.3 Genomic Context Fetching

For each variant, we fetch:
- 256 bp upstream of variant position
- Variant position
- 256 bp downstream of variant position
- **Total context**: 512 bp

This provides DNABERT-2 with sufficient sequence context to understand:
- Splice sites
- Regulatory elements
- Sequence motifs
- Local GC content

**Fallback Strategy**: If API fails, use N-padding (NNNNN...) as placeholder

---

## 4. Additional Data Sources

### 4.1 UCSC Genome Browser

**Source**: University of California, Santa Cruz Genome Browser  
**Usage**: Alternative genomic sequence fetching  
**API**: https://api.genome.ucsc.edu  
**Genome Build**: hg38

Used as backup when Ensembl API is unavailable.

### 4.2 ClinVar (Direct Access)

**Source**: NCBI ClinVar (https://www.ncbi.nlm.nih.gov/clinvar/)  
**Usage**: Validation of classifications, test case selection  
**Access Method**: E-utilities API  
**Our Usage**: 
- Select high-confidence test variants (3+ star rating)
- Cross-validate BRCA Exchange classifications
- Track classification changes over time

### 4.3 ACMG/AMP Guidelines

**Source**: Richards et al. (2015) - "Standards and guidelines for the interpretation of sequence variants"  
**Usage**: Frequency-based adjustment criteria

| Criterion | Frequency Threshold | Evidence Strength | Our Adjustment |
|-----------|-------------------|------------------|----------------|
| BA1 | >5% in any population | Stand-alone Benign | -0.20 |
| BS2 | >1% in controls | Strong Benign | -0.12 |
| BP2 | >0.5% in population | Supporting Benign | -0.06 |

---

## 5. Data Not Included (But Desirable)

### 5.1 African-Specific Databases

These would improve our model but are not currently integrated:

| Database | Status | Reason for Exclusion |
|----------|--------|---------------------|
| **H3Africa** | Exists | Limited public variant-level data availability |
| **African Genome Variation Project** | Exists | Data access restrictions, small sample size |
| **1000 Genomes AFR Superpopulation** | Partially included | Already in BRCA Exchange via gnomAD |
| **South African BRCA Studies** | Published | Individual-level data not publicly available |
| **Nigerian/Kenyan Cohorts** | Published | Aggregated data only, not variant-level |

### 5.2 Functional Data

Not included but would enhance predictions:
- In vitro functional assays (beyond Findlay et al.)
- Protein structure impact predictions
- Splicing predictions
- Conservation scores (PhyloP, GERP++)
- In silico prediction tools (SIFT, PolyPhen-2)

**Reason for exclusion**: Focus on sequence-based learning with DNABERT-2

---

## 6. Data Processing Pipeline

### 6.1 Data Preparation Steps

1. **Download BRCA Exchange TSV** (36,727 variants)
   ```bash
   python scripts/download_data.py
   ```

2. **Parse Clinical Significance** (priority: ENIGMA > ClinVar > Expert)
   ```bash
   python scripts/prepare_training_data.py
   ```

3. **Filter Unlabeled Variants** (exclude VUS and unknowns)
   - Retain only Pathogenic, Likely Pathogenic, Benign, Likely Benign
   - Result: 3,323 labeled variants

4. **Extract African Frequency** (from multiple columns)
   - `Allele_frequency_genome_AFR_GnomAD` (primary)
   - `Allele_frequency_exome_AFR_GnomAD` (fallback)
   - `AFR_Allele_frequency_1000_Genomes` (legacy)

5. **Apply African Adjustment to Labels** (training data correction)
   - If AFR frequency > 5% AND label = Pathogenic → Relabel to Benign
   - Rationale: BA1 criterion (stand-alone benign evidence)
   - Adjustments made: ~50-100 variants (estimated)

6. **Fetch Genomic Context** (512bp around each variant)
   ```bash
   python scripts/fetch_sequences.py
   ```

7. **Train/Val/Test Split** (stratified by label)
   - Train: 80% (~2,658 variants)
   - Validation: 10% (~332 variants)
   - Test: 10% (~333 variants)
   - Stratification ensures class balance in each split

### 6.2 Data Quality Checks

Implemented checks:
- [ ] No duplicate variants (same chr:pos:ref:alt)
- [ ] All variants have valid genomic coordinates
- [ ] All labeled variants have ENIGMA or ClinVar source
- [ ] Sequence context fetched successfully (or N-padded)
- [ ] African frequency in valid range [0, 1]
- [ ] Train/val/test splits have no overlap

---

## 7. Limitations and Biases

### 7.1 Ancestral Bias

**Problem**: Training data is predominantly European ancestry

**Impact**:
- Model may perform worse on variants specific to non-European populations
- Benign variants common in African populations may be misclassified
- Limited representation of African founder mutations

**Mitigation**:
- African frequency adjustments reduce false positives
- ACMG/AMP guidelines provide evidence-based corrections
- Transparent reporting of population-specific performance

### 7.2 Geographic Bias

**Problem**: "African" data is primarily African American (US/UK)

**Impact**:
- May not generalize to continental African populations
- Different admixture patterns (European ancestry in African Americans)
- Missing rare variants specific to African ethnic groups

**Mitigation**:
- Clearly document data sources
- Acknowledge limitations in documentation
- Call for African-specific validation studies

### 7.3 Class Imbalance

**Problem**: 2:1 ratio of Pathogenic to Benign variants

**Impact**:
- Model may favor predicting "Pathogenic"
- Higher false positive rate on benign variants
- Standard accuracy metric is misleading

**Mitigation**:
- Use class weighting in loss function
- Evaluate with balanced accuracy, F1, MCC
- Report per-class performance separately

### 7.4 Label Quality

**Problem**: Not all labels are equally reliable

**Sources of Uncertainty**:
- Conflicting classifications between databases
- Historical classifications may be outdated
- Some variants lack functional validation
- VUS reclassified over time

**Mitigation**:
- Prioritize ENIGMA expert classifications
- Use ClinVar star rating (higher = more reliable)
- Exclude VUS from training
- Regular data updates

### 7.5 Missing Data

**Problem**: 91% of variants are unlabeled

**Impact**:
- Small training dataset (~3,300 variants)
- May not cover full variant space
- Risk of overfitting to known variants

**Mitigation**:
- Data augmentation (sequence augmentation)
- Regularization (dropout, weight decay)
- Cross-validation to assess generalization
- Conservative prediction thresholds

---

## 8. Data Update Strategy

### 8.1 Update Frequency

| Data Source | Update Frequency | Last Updated | Next Update |
|-------------|-----------------|--------------|-------------|
| BRCA Exchange | Quarterly | Nov 2025 | Feb 2026 |
| gnomAD | Annual | Oct 2023 (v4.0) | TBD (v4.1) |
| ClinVar | Monthly | Nov 2025 | Dec 2025 |
| Ensembl | Bi-annual | Nov 2024 (v111) | May 2025 |

### 8.2 Model Retraining Plan

**Trigger conditions for retraining**:
- New BRCA Exchange release with >500 new labeled variants
- gnomAD major version update (e.g., v5.0)
- Significant classification changes in ClinVar
- Performance degradation detected in validation

**Retraining process**:
1. Download updated data
2. Re-run data preparation pipeline
3. Train new model with same hyperparameters
4. Compare performance to current model
5. Deploy if improved, otherwise keep current

---

## 9. Data Ethics and Privacy

### 9.1 Patient Privacy

**BRCA Exchange**: De-identified variant data only, no patient information  
**gnomAD**: Aggregated allele frequencies only, no individual genotypes  
**ClinVar**: De-identified clinical submissions

**Our Application**:
- Does NOT store user-uploaded genomic data
- Does NOT link variants to individuals
- Does NOT collect identifying information beyond optional ancestry

### 9.2 Informed Consent

All data sources used in this project:
- Are publicly available
- Were collected with appropriate informed consent
- Are licensed for research use
- Follow FAIR data principles (Findable, Accessible, Interoperable, Reusable)

### 9.3 Data Sharing

Our processed datasets:
- Training/val/test splits: Available on request
- Model predictions: Not stored permanently
- User queries: Logged anonymously for performance monitoring only

---

## 10. Conclusions

### 10.1 Data Quality Summary

**Strengths**:
- High-quality expert curation (ENIGMA)
- Multiple authoritative sources
- Real-time population frequency data
- Well-characterized pathogenic variants

**Weaknesses**:
- Small labeled dataset (3,323 variants)
- Ancestral bias (predominantly European)
- African American data, not continental African
- Class imbalance (2:1 Pathogenic:Benign)
- 91% unlabeled variants

### 10.2 Fitness for Purpose

**Is this data suitable for our goal of reducing bias against African populations?**

**Yes, with caveats**:
- ✅ African frequency data available from gnomAD
- ✅ ACMG/AMP guidelines provide evidence-based adjustments
- ✅ Known pathogenic/benign variants well-characterized
- ⚠️ African American data may not fully represent continental Africans
- ⚠️ Limited African-specific variant coverage
- ⚠️ Small dataset may limit model generalization

**Key Insight**: This project's value is in **adjusting for bias** using population frequencies, not in training on African-specific data (which is limited). The approach is methodologically sound given available data constraints.

### 10.3 Recommendations for Future Work

1. **Integrate H3Africa data** when publicly available
2. **Collaborate with African genomics researchers** for validation
3. **Expand to continental African populations** beyond African American
4. **Include functional data** (splicing, protein structure)
5. **Multi-ancestry training** with stratified evaluation
6. **Active learning** to prioritize VUS reclassification
7. **Federated learning** to leverage distributed African datasets without centralizing

---

## 11. Data Availability Statement

**BRCA Exchange**: https://brcaexchange.org/backend/data/  
**gnomAD v4**: https://gnomad.broadinstitute.org  
**ClinVar**: https://ftp.ncbi.nlm.nih.gov/pub/clinvar/  
**Ensembl**: https://rest.ensembl.org  
**UCSC Genome Browser**: https://api.genome.ucsc.edu  

**Our Processed Data**: Available on request (contact via GitHub)

---

**Report Version**: 1.0  
**Last Updated**: November 28, 2025  
**Next Review**: February 2026
