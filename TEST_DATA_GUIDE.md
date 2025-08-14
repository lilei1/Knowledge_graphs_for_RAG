# Test Data Guide for Knowledge Graph System

## 🧪 Available Test Data

I've created comprehensive test datasets for both the **learning version** and **production version** of the knowledge graph system.

## 📁 Test Data Files Created

### 🧬 **Genomic Data**
- **`test_data/sample_vcf.vcf`** - Sample VCF file with 10 variants across 8 maize genotypes
  - Contains realistic SNPs and INDELs
  - Includes functional annotations (missense, synonymous, etc.)
  - Covers chromosomes 1, 2, and 3
  - Genotypes: B73, Mo17, W22, Oh43, PH207, Ki3, A632, Tx303

### 🌱 **Phenotypic Data**
- **`test_data/sample_phenotypes_wide.csv`** - Wide format phenotype data
  - 32 measurements across 4 trials
  - Traits: plant_height, grain_yield, flowering_time, drought_tolerance, kernel_color, root_depth
  - Multiple environments: Iowa, Nebraska, Illinois, Kansas

- **`test_data/sample_phenotypes_long.csv`** - Long format phenotype data
  - Same data in long format (one measurement per row)
  - Includes measurement metadata: method, observer, quality flags
  - Time-series measurements with timestamps

### 🌍 **Environmental Data**
- **`test_data/sample_environmental.csv`** - Environmental conditions
  - 5 locations with GPS coordinates
  - Weather data: temperature, precipitation, humidity
  - Soil characteristics: type, pH, elevation
  - Stress conditions: drought, heat, cold stress

### ⚙️ **Configuration**
- **`test_data/test_config.yaml`** - Test configuration file
  - Optimized for testing (small batch sizes, fewer epochs)
  - Points to test data directories
  - CPU-only processing for compatibility

## 🚀 How to Use Test Data

### **Option 1: Quick Test with Learning Version**
```bash
# Use the original toy system with test data
python3 build_maize_kg.py

# The system will automatically use the existing toydata/
# You can also copy test files to toydata/ for testing
cp test_data/test_gene_traits.csv toydata/
python3 expand_maize_kg.py
```

### **Option 2: Production System Testing**
```bash
# Run the comprehensive test suite
python test_production_system.py

# Or test individual components
python production_kg_system.py --config test_data/test_config.yaml --action vcf_only --vcf-dir test_data/
python production_kg_system.py --config test_data/test_config.yaml --action phenotype_only --phenotype-dir test_data/
```

### **Option 3: Manual Component Testing**

#### Test VCF Processing:
```python
from vcf_integration import VCFProcessor
from neo4j import GraphDatabase

# Initialize
driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
processor = VCFProcessor(driver, batch_size=100)

# Process test VCF
stats = processor.process_vcf_file("test_data/sample_vcf.vcf", max_variants=100)
print(f"Processed {stats.total_variants} variants")
```

#### Test Phenotype Processing:
```python
from phenotype_normalization import PhenotypeProcessor

processor = PhenotypeProcessor(driver)
measurements = processor.process_phenotype_file("test_data/sample_phenotypes_wide.csv", format_type="wide")
processor.create_time_series_measurements(measurements)
```

#### Test Environmental Integration:
```python
from environmental_integration import EnvironmentalIntegrator
from datetime import datetime

integrator = EnvironmentalIntegrator(driver)
profile = integrator.process_location(
    "Ames_Iowa", 42.0308, -93.6319,
    datetime(2023, 1, 1), datetime(2023, 12, 31)
)
integrator.integrate_environmental_profile(profile)
```

## 📊 Expected Test Results

### **VCF Processing Results:**
- **Variants**: 10 variants processed
- **Genotypes**: 80 genotype relationships (10 variants × 8 samples)
- **Node Types**: Variant, Germplasm nodes created
- **Processing Time**: <1 second

### **Phenotype Processing Results:**
- **Measurements**: 192 measurements (32 samples × 6 traits)
- **Node Types**: Measurement, Trait nodes created
- **Relationships**: Germplasm-Measurement-Trait connections
- **Ontology Integration**: Crop Ontology trait normalization

### **Environmental Processing Results:**
- **Locations**: 5 environmental profiles
- **Node Types**: Location, Environment, Weather, Soil nodes
- **ENVO Terms**: Environmental ontology annotations
- **Weather Data**: Monthly aggregated weather summaries

## 🔍 Data Validation

### **VCF File Validation:**
```bash
# Check VCF format
head -20 test_data/sample_vcf.vcf

# Validate with production system
python production_kg_system.py --action validate_vcf --vcf-file test_data/sample_vcf.vcf
```

### **Phenotype Data Validation:**
```python
import pandas as pd

# Check wide format
df_wide = pd.read_csv("test_data/sample_phenotypes_wide.csv")
print(f"Wide format: {df_wide.shape[0]} rows, {df_wide.shape[1]} columns")
print(f"Germplasm: {df_wide['germplasm_id'].nunique()} unique")
print(f"Traits: {df_wide.columns[6:].tolist()}")

# Check long format
df_long = pd.read_csv("test_data/sample_phenotypes_long.csv")
print(f"Long format: {df_long.shape[0]} measurements")
print(f"Traits: {df_long['trait'].unique().tolist()}")
```

## 🎯 Test Scenarios

### **Scenario 1: Small Scale Testing**
- Use all test data as-is
- Perfect for development and debugging
- Fast execution (<5 minutes)

### **Scenario 2: Performance Testing**
- Duplicate VCF data to create larger files
- Test batch processing capabilities
- Monitor memory usage and processing speed

### **Scenario 3: Integration Testing**
- Run full pipeline with all data types
- Test GNN model training
- Validate dashboard functionality

## 🛠 Troubleshooting

### **Common Issues:**

1. **Neo4j Connection Error**
   ```bash
   # Start Neo4j
   docker run --name neo4j-test -p7474:7474 -p7687:7687 -d --env NEO4J_AUTH=neo4j/test123 neo4j:4.4
   ```

2. **Missing Dependencies**
   ```bash
   pip install -r requirements_production.txt
   ```

3. **VCF Format Issues**
   - Check file encoding (should be UTF-8)
   - Verify tab-separated format
   - Ensure proper VCF header

4. **Memory Issues**
   - Reduce batch_size in config
   - Use CPU instead of GPU for testing
   - Process smaller data subsets

## 📈 Scaling Test Data

### **Create Larger VCF Files:**
```python
# Duplicate variants with different positions
import pandas as pd

# Read original VCF data lines
with open("test_data/sample_vcf.vcf", 'r') as f:
    lines = f.readlines()

header_lines = [l for l in lines if l.startswith('#')]
data_lines = [l for l in lines if not l.startswith('#')]

# Create larger dataset
with open("test_data/large_sample.vcf", 'w') as f:
    f.writelines(header_lines)
    
    for i in range(100):  # 1000 variants
        for line in data_lines:
            fields = line.strip().split('\t')
            fields[1] = str(int(fields[1]) + i * 1000)  # Adjust position
            fields[2] = f"rs{i:03d}_{fields[2]}"  # Adjust ID
            f.write('\t'.join(fields) + '\n')
```

### **Generate Time-Series Phenotypes:**
```python
import pandas as pd
from datetime import datetime, timedelta

# Create multiple time points
base_data = pd.read_csv("test_data/sample_phenotypes_wide.csv")
time_series_data = []

for days in range(0, 120, 10):  # Every 10 days for 4 months
    for _, row in base_data.iterrows():
        new_row = row.copy()
        new_row['timestamp'] = (datetime(2023, 5, 1) + timedelta(days=days)).strftime('%Y-%m-%d')
        new_row['plant_height'] = row['plant_height'] * (1 + days/120 * 0.5)  # Growth over time
        time_series_data.append(new_row)

pd.DataFrame(time_series_data).to_csv("test_data/time_series_phenotypes.csv", index=False)
```

## ✅ Test Checklist

- [ ] Neo4j database running
- [ ] Test data files present
- [ ] Dependencies installed
- [ ] Configuration file updated
- [ ] Database connection successful
- [ ] VCF processing working
- [ ] Phenotype processing working
- [ ] Environmental integration working
- [ ] GNN models training (optional)
- [ ] Dashboard accessible (optional)

## 🎉 Ready to Test!

Your test data is ready! Choose your testing approach:

1. **🚀 Quick Start**: Run `python test_production_system.py`
2. **🔬 Component Testing**: Test individual modules
3. **📊 Dashboard Testing**: Start the breeder dashboard
4. **⚡ Performance Testing**: Scale up the data and test limits

The test data provides a realistic but manageable dataset to validate all system components! 🧬✨
