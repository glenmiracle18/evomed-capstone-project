# 🧬 African Population-Aware BRCA1 Variant Analysis - UML Diagrams

## 📊 Class Diagram - Core System Architecture

```mermaid
classDiagram
    class VariantRequest {
        +int variant_position
        +string alternative
        +string chromosome
        +bool use_african_adjustment
        +validate()
    }

    class VariantResponse {
        +string prediction
        +float confidence
        +float evo2_delta_score
        +float population_adjustment
        +float african_frequency
    }

    class Evo2Model {
        -model
        -population_service
        +analyze_single_variant()
        +load_model()
    }

    class PopulationFrequencyService {
        -gnomad_api_url
        -cache_expiry_days
        +get_population_frequency()
        +get_cached_frequency()
        +cache_frequency()
    }

    class BiasAdjustmentEngine {
        +calculate_population_adjustment()
        +classify_variant_with_population()
        -apply_frequency_rules()
    }

    class GenomeSequenceService {
        -ucsc_api_url
        +get_genome_sequence()
        -fetch_from_ucsc()
    }

    class CacheManager {
        -db_path
        +get_cached_data()
        +cache_data()
        +cleanup_expired()
    }

    class VariantClassifier {
        -base_threshold
        +classify_standard()
        +classify_population_aware()
        +calculate_confidence()
    }

    %% Relationships
    Evo2Model --> VariantRequest
    Evo2Model --> VariantResponse
    Evo2Model --> PopulationFrequencyService
    Evo2Model --> GenomeSequenceService
    Evo2Model --> BiasAdjustmentEngine
    Evo2Model --> VariantClassifier
    
    PopulationFrequencyService --> CacheManager
    BiasAdjustmentEngine --> VariantClassifier
    
    %% Compositions
    Evo2Model *-- PopulationFrequencyService
    PopulationFrequencyService *-- CacheManager
```

## 🔄 Sequence Diagram - Variant Analysis Workflow

```mermaid
sequenceDiagram
    participant Client as NextJS Frontend
    participant API as FastAPI Server
    participant Evo2 as Evo2Model
    participant PopSvc as PopulationFrequencyService
    participant Cache as CacheManager
    participant gnomAD as gnomAD API
    participant UCSC as UCSC Genome API
    participant BiasEng as BiasAdjustmentEngine
    participant Classifier as VariantClassifier

    Client->>+API: POST /analyze variant
    Note over Client,API: VariantRequest: chr17:43115779 G>A

    API->>+Evo2: analyze_single_variant(request)
    
    %% Genome Sequence Retrieval
    Evo2->>+UCSC: get_genome_sequence(chr17, 43115779, hg38)
    UCSC-->>-Evo2: 8192bp sequence window
    Note over Evo2: Calculate relative position in window
    
    %% Population Frequency Lookup
    Evo2->>+PopSvc: get_population_frequency(chr17, 43115779, G, A)
    
    PopSvc->>+Cache: get_cached_frequency(chr17, 43115779, G, A)
    alt Cache Hit
        Cache-->>PopSvc: cached frequency data
    else Cache Miss
        Cache-->>PopSvc: None
        PopSvc->>+gnomAD: GraphQL query for variant frequencies
        gnomAD-->>-PopSvc: African AF=0.0234, Global AF=0.0156
        PopSvc->>Cache: cache_frequency(variant, freq_data)
    end
    PopSvc-->>-Evo2: frequency data with African context
    
    %% Evo2 Model Inference
    Note over Evo2: Load reference and variant sequences
    Evo2->>Evo2: model.score_sequences([ref_seq, var_seq])
    Note over Evo2: Calculate delta score: -0.00234
    
    %% Population-Aware Analysis
    Evo2->>+BiasEng: calculate_population_adjustment(delta_score, freq_data)
    Note over BiasEng: Apply frequency-based rules
    Note over BiasEng: African AF=0.0234 → +0.002 adjustment
    BiasEng-->>-Evo2: adjusted_score=-0.00034, reasoning
    
    %% Final Classification
    Evo2->>+Classifier: classify_population_aware(adjusted_score, freq_data)
    Note over Classifier: Compare against dynamic threshold
    Note over Classifier: Calculate confidence score
    Classifier-->>-Evo2: prediction="Likely Benign", confidence=0.856
    
    %% Response Assembly
    Evo2-->>-API: VariantResponse with all analysis results
    
    API-->>-Client: JSON response with classification
    Note over Client: Display results with population context

    %% Parallel Metrics Collection
    par Metrics Collection
        PopSvc->>MetricsCollector: record_cache_hit(true)
        Evo2->>MetricsCollector: record_response_time(4.2s)
        API->>MetricsCollector: record_successful_analysis()
    end
```

## 📋 Component Interaction Notes

### **Class Diagram Key Features:**

1. **Core Service Classes:**
   - `Evo2Model`: Main orchestrator for variant analysis
   - `PopulationFrequencyService`: Handles gnomAD integration and caching
   - `BiasAdjustmentEngine`: Implements African population bias mitigation

2. **Data Models:**
   - `VariantRequest`: Input validation and structure
   - `VariantResponse`: Comprehensive analysis results

3. **Supporting Services:**
   - `CacheManager`: SQLite-based frequency caching
   - `GenomeSequenceService`: UCSC API integration
   - `MetricsCollector`: Performance monitoring

### **Sequence Diagram Key Flows:**

1. **Request Processing:**
   - Frontend → API → Evo2Model orchestration
   - Input validation and coordinate handling

2. **Data Retrieval:**
   - Parallel genome sequence and population frequency lookup
   - Smart caching with fallback to external APIs

3. **ML Pipeline:**
   - Evo2 inference on reference and variant sequences
   - Population-aware bias adjustment
   - Dynamic threshold classification

4. **Response Assembly:**
   - Comprehensive results with population context
   - Performance metrics collection

### **Design Patterns Demonstrated:**

- **Service Layer Pattern**: Clear separation of concerns
- **Repository Pattern**: CacheManager abstracts data persistence
- **Strategy Pattern**: Different classification strategies based on population data
- **Observer Pattern**: MetricsCollector monitors system performance
- **Facade Pattern**: Evo2Model provides simplified interface to complex ML pipeline
