# Production Knowledge Graph System for Biological Applications

This is a production-ready, scalable knowledge graph system designed for biological applications, capable of handling millions of genotypes, real phenotypic data, and downstream machine learning applications.

## 🚀 Key Features

### 1. **Data Scaling & Normalization Infrastructure**
- **VCF Integration**: Process millions of genotypes from VCF files with efficient variant normalization
- **Phenotypic Data**: Handle time-series phenotypic measurements with Crop Ontology integration
- **Environmental Data**: Integrate environmental covariates using ENVO ontology and weather APIs
- **ID Normalization**: Consistent identification across Ensembl, Crop Ontology, and ENVO platforms

### 2. **Enhanced Graph Schema**
- **New Node Types**: `:Germplasm`, `:Environment`, `:Trial`, `:Variant`, `:Population`, `:Measurement`
- **Complex Relationships**: Breeding pedigrees, G×E interactions, time-series traits
- **Ontology Integration**: Crop Ontology, ENVO, Gene Ontology terms
- **Temporal Modeling**: Time-series measurements with proper indexing

### 3. **Graph Neural Network Inference Layer**
- **Link Prediction**: Gene-trait association prediction using GCN
- **G×E Interactions**: Genotype × Environment modeling with Graph Attention Networks
- **Candidate Gene Identification**: GraphSAGE-based gene prioritization
- **Scalable Training**: PyTorch Geometric with GPU acceleration

### 4. **ETL Automation & Versioning**
- **Nextflow Pipeline**: Containerized, scalable data processing
- **Graph Versioning**: Neo4j Enterprise backup and rollback capabilities
- **Batch Processing**: Efficient handling of large datasets
- **Quality Control**: Comprehensive data validation and monitoring

### 5. **Production Deployment & Visualization**
- **Neo4j Enterprise**: High-availability cluster deployment
- **Amazon Neptune**: Cloud-native graph database option
- **Breeder Dashboard**: Flask + D3.js visualization interface
- **Access Control**: Role-based security and authentication

## 📋 System Requirements

### Minimum Requirements
- **CPU**: 8 cores
- **RAM**: 32 GB
- **Storage**: 1 TB SSD
- **GPU**: NVIDIA Tesla V100 (for GNN training)

### Recommended for Production
- **CPU**: 16+ cores
- **RAM**: 64+ GB
- **Storage**: 5+ TB NVMe SSD
- **GPU**: NVIDIA A100 or V100
- **Network**: 10 Gbps

## 🛠 Installation

### 1. Clone Repository
```bash
git clone https://github.com/your-org/production-kg-system.git
cd production-kg-system
```

### 2. Install Dependencies
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements_production.txt

# Install Nextflow
curl -s https://get.nextflow.io | bash
sudo mv nextflow /usr/local/bin/
```

### 3. Setup Neo4j Enterprise
```bash
# Using Docker
docker run --name neo4j-production \
  -p7474:7474 -p7687:7687 \
  -d --env NEO4J_AUTH=neo4j/production_password \
  --env NEO4J_ACCEPT_LICENSE_AGREEMENT=yes \
  neo4j:4.4-enterprise

# Or using the deployment script
python production_deployment.py --type neo4j
```

### 4. Configure System
```bash
# Copy configuration template
cp config/production_config.yaml.template config/production_config.yaml

# Edit configuration
nano config/production_config.yaml
```

## 🚀 Quick Start

### 1. Initialize System
```bash
python production_kg_system.py --action status
```

### 2. Run Full Pipeline
```bash
python production_kg_system.py --action full_pipeline
```

### 3. Start Dashboard
```bash
python breeder_dashboard.py
# Access at http://localhost:5000
```

## 📊 Data Processing

### VCF Data Processing
```bash
# Process VCF files
python production_kg_system.py --action vcf_only --vcf-dir data/vcf/

# Using Nextflow pipeline
nextflow run nextflow_pipeline.nf \
  --vcf_files "data/vcf/*.vcf.gz" \
  --batch_size 10000
```

### Phenotype Data Processing
```bash
# Process phenotype files
python production_kg_system.py --action phenotype_only --phenotype-dir data/phenotypes/

# Supported formats:
# - Wide format: traits as columns
# - Long format: one measurement per row
# - Time-series: multiple measurements over time
```

### Environmental Data Integration
```python
from environmental_integration import EnvironmentalIntegrator
from datetime import datetime

integrator = EnvironmentalIntegrator(neo4j_driver)

# Process location with weather and soil data
profile = integrator.process_location(
    location_name="Ames_Iowa",
    lat=42.0308,
    lon=-93.6319,
    start_date=datetime(2020, 1, 1),
    end_date=datetime(2023, 12, 31)
)

integrator.integrate_environmental_profile(profile)
```

## 🧠 Machine Learning

### Train GNN Models
```python
from gnn_inference import GNNInferenceEngine, GNNConfig

# Configure GNN
config = GNNConfig(
    hidden_dim=128,
    num_layers=3,
    dropout=0.2,
    learning_rate=0.001,
    num_epochs=100
)

# Initialize and train
engine = GNNInferenceEngine(neo4j_driver, config)
engine.initialize_models()
engine.save_models("models/production")
```

### Generate Predictions
```python
# Predict gene-trait associations
gene_ids = ["DREB2A", "ZmNAC111", "PSY1"]
trait_ids = ["drought_tolerance", "grain_yield", "flowering_time"]

predictions = engine.predict_gene_trait_associations(gene_ids, trait_ids)

for pred in predictions:
    print(f"{pred.source_id} -> {pred.target_id}: {pred.prediction_score:.3f}")
```

## 🌐 Web Dashboard

### Features
- **Gene-Trait Network Visualization**: Interactive D3.js network graphs
- **Candidate Gene Ranking**: ML-powered gene prioritization
- **Germplasm Performance**: Multi-environment trial analysis
- **Trait Correlations**: Breeding decision support
- **Search & Filter**: Advanced query interface

### API Endpoints
```bash
# Get gene-trait network
curl "http://localhost:5000/api/network?trait_filter=drought&max_nodes=100"

# Get candidate genes
curl "http://localhost:5000/api/candidates?trait_name=yield&top_k=20"

# Get germplasm performance
curl "http://localhost:5000/api/performance?trait_name=height&environment=drought"
```

## 🔧 Configuration

### Production Configuration (`config/production_config.yaml`)
```yaml
neo4j:
  uri: "bolt://localhost:7687"
  username: "neo4j"
  password: "production_password"
  database: "neo4j"

data_sources:
  vcf_directory: "data/vcf/"
  phenotype_directory: "data/phenotypes/"
  environmental_directory: "data/environment/"

processing:
  batch_size: 10000
  max_variants_per_file: 1000000
  parallel_workers: 8

gnn:
  hidden_dim: 256
  num_layers: 4
  dropout: 0.1
  learning_rate: 0.0005
  num_epochs: 200
  device: "cuda"

deployment:
  type: "neo4j"  # or "neptune"
  environment: "production"
```

## 📈 Performance Optimization

### Neo4j Tuning
```bash
# Memory configuration
NEO4J_dbms_memory_heap_initial_size=16G
NEO4J_dbms_memory_heap_max_size=16G
NEO4J_dbms_memory_pagecache_size=32G

# Performance settings
NEO4J_dbms_query_cache_size=1000
NEO4J_dbms_tx_log_rotation_retention_policy=100M size
```

### Batch Processing
- **VCF Processing**: 10,000 variants per batch
- **Phenotype Processing**: 1,000 measurements per batch
- **Relationship Creation**: 5,000 relationships per transaction

### Indexing Strategy
```cypher
-- Essential indexes for performance
CREATE INDEX gene_chromosome_position IF NOT EXISTS 
FOR (g:Gene) ON (g.chromosome, g.start_pos);

CREATE INDEX variant_position IF NOT EXISTS 
FOR (v:Variant) ON (v.chromosome, v.position);

CREATE INDEX measurement_timestamp IF NOT EXISTS 
FOR (m:Measurement) ON (m.timestamp);
```

## 🔒 Security

### Authentication
- Neo4j native authentication
- Role-based access control (RBAC)
- SSL/TLS encryption for all connections

### Data Privacy
- Anonymized germplasm identifiers
- Encrypted data at rest
- Audit logging for all operations

## 📊 Monitoring

### System Metrics
- Node/relationship counts
- Query performance
- Memory usage
- Disk I/O

### Dashboard Monitoring
```bash
# Prometheus metrics endpoint
curl http://localhost:9090/metrics

# Grafana dashboard
http://localhost:3000
```

## 🚀 Deployment Options

### Docker Deployment
```bash
docker-compose up -d
```

### Kubernetes Deployment
```bash
kubectl apply -f k8s/production-deployment.yaml
```

### AWS Neptune
```python
from production_deployment import NeptuneDeployer, NeptuneConfig

config = NeptuneConfig(
    cluster_identifier="kg-production",
    instance_class="db.r5.2xlarge",
    num_instances=3
)

deployer = NeptuneDeployer(config)
deployment_info = deployer.deploy_cluster()
```

## 📚 Documentation

- **[API Documentation](docs/api.md)**: Complete API reference
- **[Schema Documentation](docs/schema.md)**: Graph schema details
- **[Deployment Guide](docs/deployment.md)**: Production deployment
- **[Performance Tuning](docs/performance.md)**: Optimization guide

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Issues**: [GitHub Issues](https://github.com/your-org/production-kg-system/issues)
- **Documentation**: [Wiki](https://github.com/your-org/production-kg-system/wiki)
- **Email**: support@your-org.com

## 🎯 Roadmap

- [ ] Integration with additional biological databases (MaizeGDB, Gramene)
- [ ] Advanced GNN architectures (Graph Transformers)
- [ ] Real-time data streaming capabilities
- [ ] Multi-species support
- [ ] Federated learning across institutions
