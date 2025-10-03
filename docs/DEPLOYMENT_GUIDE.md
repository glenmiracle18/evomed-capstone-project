# African Population Scoring - Deployment Guide

## Quick Start

### 1. Install Dependencies
```bash
cd evo2-backend
pip install -r requirements.txt
```

### 2. Deploy to Modal
```bash
modal deploy main.py
```

### 3. Get API Endpoint
After deployment, Modal will provide an endpoint URL like:
```
https://your-app-name--analyze-single-variant.modal.run
```

### 4. Test the Implementation
```bash
# Update the API_URL in test_african_population.py
python test_african_population.py
```

## Example Usage

### With African Population Adjustment (Default)
```bash
curl -X POST "https://your-endpoint.modal.run" \
  -H "Content-Type: application/json" \
  -d '{
    "variant_position": 5227002,
    "alternative": "A", 
    "genome": "hg38",
    "chromosome": "chr11",
    "use_african_adjustment": true
  }'
```

### Without African Population Adjustment (Original Evo2)
```bash
curl -X POST "https://your-endpoint.modal.run" \
  -H "Content-Type: application/json" \
  -d '{
    "variant_position": 5227002,
    "alternative": "A",
    "genome": "hg38", 
    "chromosome": "chr11",
    "use_african_adjustment": false
  }'
```

## Expected Response Format

```json
{
  "reference": "T",
  "alternative": "A",
  "evo2_delta_score": -0.00234,
  "population_adjusted_score": -0.00134,
  "population_adjustment": 0.001,
  "adjustment_reasoning": "Present in African populations (AF=0.0956, +0.004000)",
  "african_frequency": 0.0956,
  "global_frequency": 0.0234,
  "prediction": "Likely benign",
  "confidence": 0.923,
  "classification_method": "african_high_frequency_adjusted",
  "population_context": "High frequency in African populations (AF=0.0956)",
  "threshold_used": -0.001918,
  "use_african_adjustment": true,
  "position": 5227002
}
```

## Troubleshooting

### Common Issues

1. **Import Error**: Make sure all dependencies are installed
2. **gnomAD Timeout**: The system falls back gracefully
3. **Cache Issues**: Check `/population_cache` volume permissions
4. **Flash Attention**: Already patched in the codebase

### Monitoring

- Check Modal logs for population service initialization
- Monitor response times for gnomAD API calls
- Watch for cache hit rates in the logs

## Performance Notes

- First request per variant may be slower (gnomAD API call)
- Subsequent requests use cached data (much faster)
- Cache expires after 30 days for fresh data