# Knowledge Graphs for RAG

This project demonstrates how to build knowledge graphs for Retrieval-Augmented Generation (RAG) using Neo4j, with a focus on maize genetic data.

## 🚀 **NEW: Production-Ready System Available!**

**We now offer both learning/demo and production-ready implementations:**

- **📚 Learning Version**: Original toy data system for education and prototyping
- **🏭 Production Version**: Scalable system handling millions of genotypes, real biological data, and ML applications

**For production deployment, see [PRODUCTION_README.md](PRODUCTION_README.md) and [SCALING_SUMMARY.md](SCALING_SUMMARY.md)**

## Project Structure

### 📚 Learning/Demo Version (Original)
```
├── README.md                    # This file
├── SETUP_GUIDE.md              # Detailed setup instructions
├── LITERATURE_MINING_GUIDE.md  # Guide for extracting data from literature
├── DATABASE_MINING_GUIDE.md    # Guide for mining biological databases
├── DATA_MINING_SUMMARY.md      # Complete overview of all mining approaches
├── requirements.txt            # Python dependencies (learning version)
├── .env.template              # Environment configuration template
├── build_maize_kg.py          # Main script to build the knowledge graph
├── expand_maize_kg.py         # Script to add additional CSV data
├── visualize_kg.py            # Script to analyze and visualize the graph
├── literature_mining.py       # Demo script for LLM-based data extraction
├── pubmed_mining.py           # Real PubMed integration with LLMs
├── database_mining.py         # Demo script for database extraction
├── real_api_mining.py         # Live API calls to real databases
├── example_queries.md         # 50+ advanced Cypher query examples
├── toydata/
│   ├── maize.csv              # Original maize genetic data
│   ├── additional_genes.csv   # Extended gene-trait relationships
│   ├── genotype_traits.csv    # Genotype-trait associations
│   ├── qtl_mappings.csv       # QTL-chromosome mappings
│   ├── field_trials.csv       # Multi-location trial data
│   ├── molecular_markers.csv  # SNP and SSR marker data
│   ├── pathways.csv           # Biological pathway information
│   ├── literature_extracted.csv # LLM-extracted literature data
│   ├── database_mined.csv     # Database-extracted relationships
│   └── real_api_mined.csv     # Live API-extracted data
└── notebook/
    ├── build_maize_kg.ipynb   # Jupyter notebook for building the KG
    ├── L2-query_with_cypher.ipynb
    ├── L3-prep_text_for_RAG.ipynb
    ├── L4-construct_kg_from_text.ipynb
    ├── L5-add_relationships_to_kg.ipynb
    ├── L6-expand_the_kg.ipynb
    └── L7-chat_with_kg.ipynb
```

### 🏭 Production Version (NEW!)
```
├── PRODUCTION_README.md        # Production system documentation
├── SCALING_SUMMARY.md          # Implementation summary
├── requirements_production.txt # Production dependencies
├── production_schema.py        # Enhanced graph schema (10+ node types)
├── vcf_integration.py         # VCF processing for millions of genotypes
├── phenotype_normalization.py # Crop Ontology integration
├── environmental_integration.py # ENVO ontology & weather APIs
├── gnn_inference.py           # Graph Neural Networks for ML
├── nextflow_pipeline.nf       # Automated ETL pipeline
├── production_deployment.py   # Enterprise deployment automation
├── breeder_dashboard.py       # Flask + D3.js visualization dashboard
├── production_kg_system.py    # Main orchestration system
└── modules/
    └── vcf_processing.nf      # Nextflow processing modules
```

## Quick Start

### 📚 Learning Version (Original Toy Data)

1. **Install dependencies:**
   ```bash
   pip3 install -r requirements.txt
   ```

2. **Set up Neo4j** (Docker recommended):
   ```bash
   docker run --name neo4j-maize -p7474:7474 -p7687:7687 -d --env NEO4J_AUTH=neo4j/test123 neo4j:4.4
   ```

3. **Configure environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your Neo4j credentials (default: neo4j/test123)
   ```

4. **Build the basic knowledge graph:**
   ```bash
   python3 build_maize_kg.py
   ```

5. **Expand with additional data:**
   ```bash
   python3 expand_maize_kg.py
   ```

6. **Extract data from literature (optional):**
   ```bash
   python3 literature_mining.py  # Demo with example abstracts
   # OR for real PubMed mining (requires API keys):
   # python3 pubmed_mining.py
   ```

7. **Mine data from databases (optional):**
   ```bash
   python3 database_mining.py    # Demo database extraction
   python3 real_api_mining.py    # Live API calls (requires internet)
   ```

8. **Analyze the graph:**
   ```bash
   python3 visualize_kg.py
   ```

### 🏭 Production Version (Scalable System)

**For production deployment with millions of genotypes and real biological data:**

1. **Install production dependencies:**
   ```bash
   pip3 install -r requirements_production.txt
   ```

2. **Deploy Neo4j Enterprise:**
   ```bash
   python production_deployment.py --type neo4j
   ```

3. **Run production pipeline:**
   ```bash
   python production_kg_system.py --action full_pipeline
   ```

4. **Start breeder dashboard:**
   ```bash
   python breeder_dashboard.py
   # Access at http://localhost:5000
   ```

**📖 See [PRODUCTION_README.md](PRODUCTION_README.md) for complete production setup guide.**

## Features

### 📚 Learning Version Features
- **Automated Knowledge Graph Construction**: Converts CSV data into a structured Neo4j graph
- **Intelligent Node Classification**: Automatically categorizes entities across 10+ types
- **Comprehensive Data Model**: Supports genes, traits, genotypes, QTLs, pathways, markers, and more
- **Multi-source Data Integration**: Combines genetic, phenotypic, and experimental data
- **Literature Mining with LLMs**: Extract real data from scientific papers using GPT/Claude
- **Database Mining**: Direct extraction from KEGG, UniProt, Ensembl, and other biological databases
- **Advanced Query Examples**: 50+ Cypher queries for complex biological analysis
- **Interactive Notebooks**: Jupyter notebooks for exploration and analysis
- **Visualization Tools**: Scripts to analyze and export graph data
- **Scalable Architecture**: Easily expandable with new CSV data sources

### 🏭 Production Version Features
- **🚀 Massive Scale**: Handle millions of genotypes from VCF files
- **🧬 Real Biological Data**: Crop Ontology, ENVO ontology integration
- **🤖 Machine Learning**: Graph Neural Networks for gene-trait prediction
- **⚡ High Performance**: Batch processing, GPU acceleration
- **🏢 Enterprise Deployment**: Neo4j Enterprise, Amazon Neptune support
- **📊 Interactive Dashboard**: Flask + D3.js breeder interface
- **🔄 Automated ETL**: Nextflow pipelines with versioning
- **🔒 Production Security**: SSL/TLS, authentication, access control

## Data Model

The expanded knowledge graph represents comprehensive maize genetic data with:

### **Node Types (142 total nodes):**
- **18 Genes**: DREB2A, ZmVPP1, ZmNF-YB2, ZmCCT, etc.
- **33 Traits**: Drought Tolerance, Cold Tolerance, Nitrogen Use Efficiency, etc.
- **12 Genotypes**: B73, Mo17, W22, Oh43, PH207, etc.
- **11 QTLs**: qDT1.1, qCT2.1, qNUE3.1, etc. (mapped across all 10 chromosomes)
- **10 Chromosomes**: Complete maize genome representation
- **25 Pathways**: Real KEGG pathways + ABA Signaling, Defense Response, etc.
- **10 Markers**: SNP and SSR markers linked to genes and QTLs
- **7 Trials**: Multi-location field experiments (2020-2023)
- **6 Locations**: Ames, Iowa, Nebraska, Illinois, Kansas, Minnesota
- **4 Weather**: Environmental conditions (Drought, Cold Stress, High Temperature)
- **6 Entities**: Expression experiments, protein functions, etc.

### **Relationship Types (154 total relationships):**
- **REGULATES**: Gene → Trait regulation
- **HAS_TRAIT**: Genotype → Trait associations
- **ASSOCIATED_WITH**: Trait → QTL mappings
- **IS_A**: Pathway categorizations (from KEGG database)
- **LOCATED_ON**: QTL → Chromosome positions
- **TESTED_IN**: Genotype → Trial participation
- **MEASURED**: Trial → Trait evaluation
- **PARTICIPATES_IN**: Gene → Pathway involvement
- **CONDUCTED_IN**: Trial → Location mapping
- **HAS_WEATHER**: Location → Environmental conditions
- **HAS_MARKER**: Gene → Molecular marker links
- **LINKED_TO**: Marker → QTL associations
- **HAS_FUNCTION**: Gene → Protein function (from databases)
- **STUDIES**: Experiment → Research focus (from Expression Atlas)

## Example Queries

### Basic Queries
Find genes that regulate drought tolerance:
```cypher
MATCH (g:Gene)-[:REGULATES]->(t:Trait {name: "Drought Tolerance"})
RETURN g.name as gene
```

Find complete pathways from gene to chromosome:
```cypher
MATCH path = (g:Gene)-[:REGULATES]->(t:Trait)-[:ASSOCIATED_WITH]->(q:QTL)-[:LOCATED_ON]->(c:Chromosome)
RETURN g.name, t.name, q.name, c.name
```

### Advanced Queries
Find genes in biological pathways:
```cypher
MATCH (g:Gene)-[:PARTICIPATES_IN]->(p:Pathway)-[:REGULATES]->(t:Trait)
RETURN g.name as gene, p.name as pathway, t.name as trait
```

Find genotypes tested under drought conditions:
```cypher
MATCH (gt:Genotype)-[:TESTED_IN]->(trial:Trial)-[:CONDUCTED_IN]->(loc:Location)-[:HAS_WEATHER]->(w:Weather {name: "Drought"})
RETURN gt.name as genotype, trial.name as trial, loc.name as location
```

**See `example_queries.md` for 50+ advanced query examples!**

## Literature Mining with LLMs

Extract real biological relationships from scientific literature using Large Language Models:

### **🚀 Quick Demo:**
```bash
python3 literature_mining.py
```
This extracts relationships from example abstracts and adds them to your knowledge graph.

### **🔬 Real PubMed Mining:**
```bash
# Setup (requires API keys)
pip install biopython openai anthropic
export OPENAI_API_KEY="your-openai-key"

# Mine real literature
python3 pubmed_mining.py
```

### **📊 What You Get:**
- **Gene-trait relationships** from functional studies
- **QTL mappings** from genetic mapping papers
- **Pathway information** from systems biology research
- **Genotype-environment interactions** from field trials
- **Molecular marker associations** from GWAS studies

### **🎯 Supported LLM Providers:**
- **OpenAI GPT-3.5/GPT-4**: Best accuracy for biological text
- **Anthropic Claude**: Excellent for scientific literature
- **Local models** (Ollama): Privacy-focused option
- **Biomedical LLMs**: Specialized models like BioBERT

### **📚 Data Sources:**
- **PubMed/NCBI**: Comprehensive biomedical literature
- **Plant science journals**: Specialized publications
- **Preprint servers**: Latest research (bioRxiv)
- **Curated databases**: MaizeGDB, Gramene, KEGG

**See `LITERATURE_MINING_GUIDE.md` for detailed instructions and best practices.**

## Database Mining

Extract structured data directly from biological databases using APIs and web scraping:

### **🗄️ Quick Demo:**
```bash
python3 database_mining.py     # Simulate database extraction
python3 real_api_mining.py     # Live API calls to real databases
```

### **🌐 Supported Databases:**
- **KEGG** ✅: Metabolic pathways, gene functions (REST API)
- **UniProt** ✅: Protein functions, GO terms (REST API)
- **Ensembl Plants** ✅: Genomic locations, annotations (REST API)
- **EBI Expression Atlas** ✅: Gene expression experiments (REST API)
- **MaizeGDB**: Curated maize genetics (web scraping required)
- **Gramene**: Plant comparative genomics (REST API)

### **📊 Real Data Extracted:**
- **KEGG Pathways**: Metabolic pathways, Carbon metabolism, Fatty acid metabolism
- **Expression Data**: Transcription profiling experiments from public studies
- **Protein Functions**: Transcription factor activity, Protein phosphatase activity
- **Genomic Locations**: Gene-chromosome mappings
- **GO Terms**: Gene ontology annotations

### **🔧 Mining Approaches:**
- **REST APIs**: Direct programmatic access to databases
- **Web Scraping**: Extract from databases without APIs
- **Bulk Downloads**: Process database dump files
- **Real-time Updates**: Incremental data synchronization

**See `DATABASE_MINING_GUIDE.md` for comprehensive database mining strategies.**

## Getting Started

For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md).

## 🎯 Which Version Should You Use?

### 📚 **Use Learning Version If:**
- Learning about knowledge graphs and Neo4j
- Prototyping with small datasets
- Educational purposes
- Getting started with biological data modeling

### 🏭 **Use Production Version If:**
- Processing millions of genotypes (VCF files)
- Need real biological data integration
- Require machine learning predictions
- Building breeding decision support systems
- Need enterprise-scale deployment
- Want interactive dashboards for breeders

## Performance Evaluation

Monitor and improve your knowledge graph performance using built-in evaluation tools:

### 📊 **Quick Performance Check**
```bash
# Run comprehensive evaluation
python performance_dashboard.py

# Choose option 2 for detailed text summary
```

### 🎯 **Key Performance Metrics**

#### **Graph Structure Metrics**
- **Total Nodes**: Current count and target ranges
- **Total Relationships**: Connection density and coverage
- **Graph Density**: How well-connected your graph is (target: >0.01)
- **Average Degree**: Average connections per node (target: >3.0)
- **Isolated Nodes**: Nodes with no connections (target: 0)

#### **Data Quality Metrics**
- **Name Completeness**: Percentage of nodes with names (target: >90%)
- **Property Completeness**: Percentage of nodes with IDs and metadata (target: >50%)
- **Relationship Properties**: Confidence scores and effect sizes (target: >80%)

#### **Coverage Metrics**
- **Genes with Traits**: Gene-trait association coverage (target: >95%)
- **Traits with QTLs**: QTL mapping coverage (target: >70%)
- **Genotypes with Trials**: Field trial coverage (target: >80%)

### 🔍 **Performance Assessment Commands**

#### **Check Current Status**
```bash
# Quick node and relationship count
python -c "
from neo4j import GraphDatabase
driver = GraphDatabase.driver('bolt://localhost:7687', auth=('neo4j', 'maize123'))
session = driver.session()
result = session.run('MATCH (n) RETURN count(n) as nodes')
print(f'Total nodes: {result.single()[\"nodes\"]}')
session.close()
driver.close()
"
```

#### **Evaluate Specific Metrics**
```cypher
// Check graph density
MATCH (n) WITH count(n) as nodes
MATCH ()-[r]->() WITH nodes, count(r) as rels
RETURN nodes, rels, rels * 100.0 / (nodes * (nodes - 1)) as density_percent;

// Check coverage
MATCH (g:Gene) OPTIONAL MATCH (g)-[:REGULATES]->(t:Trait) 
RETURN count(g) as total_genes, count(t) as genes_with_traits,
       count(t) * 100.0 / count(g) as coverage_percent;

// Find isolated nodes
MATCH (n) WHERE NOT (n)--() RETURN count(n) as isolated_count;
```

### 📈 **Performance Benchmarks**

| Metric | Current | Target | Status |
|--------|---------|---------|---------|
| **Graph Density** | 0.0084 | >0.01 | ⚠️ Needs improvement |
| **Name Completeness** | 80% | >90% | ⚠️ Close to target |
| **Property Completeness** | 0% | >50% | ❌ Major improvement needed |
| **QTL Coverage** | 33.3% | >70% | ❌ Significant improvement needed |
| **Gene-Trait Coverage** | 94.4% | >95% | ✅ Excellent |

### 🚀 **Performance Improvement Strategies**

#### **1. Increase Data Completeness**
```cypher
// Add missing properties
MATCH (g:Gene) WHERE NOT EXISTS(g.gene_id) 
SET g.gene_id = g.name + "_ID";

MATCH (t:Trait) WHERE NOT EXISTS(t.trait_id) 
SET t.trait_id = t.name + "_ID";
```

#### **2. Improve Graph Density**
```cypher
// Add more QTL-trait associations
MATCH (q:QTL), (t:Trait) 
WHERE q.chromosome = "1" AND t.name CONTAINS "Drought"
CREATE (q)-[:ASSOCIATED_WITH]->(t);
```

#### **3. Enhance Relationship Properties**
```cypher
// Add confidence scores to relationships
MATCH ()-[r:REGULATES]->() 
SET r.confidence = 0.8, r.effect_size = 1.0;
```

### 💡 **Key Recommendations**

1. **Focus on QTL Coverage** - Only 33.3% of traits have QTL associations
2. **Add Missing Properties** - 0% property completeness is a major gap
3. **Increase Cross-Entity Connections** - Current density of 0.0084 is low
4. **Enhance Relationship Metadata** - Add confidence scores and effect sizes
5. **Expand Trial Data** - More genotype-environment testing data needed

### 📊 **Performance Dashboard**

The `performance_dashboard.py` script provides:
- **Visual Dashboard**: Charts and graphs of key metrics
- **Text Summary**: Detailed performance breakdown
- **Recommendations**: Actionable improvement suggestions
- **Export Options**: Save results to files

## Contributing

Feel free to contribute by:
- **Adding more data sources**: Create new CSV files, mine literature, or integrate databases
- **Improving literature mining**: Enhance LLM prompts and extraction accuracy
- **Expanding database mining**: Add support for more biological databases (MaizeGDB, Gramene, etc.)
- **Enhancing API integrations**: Improve real-time data synchronization with databases
- **Expanding the data model**: Add new node types and relationship categories
- **Creating analysis tools**: Build specialized query interfaces or visualizations
- **Validating extracted data**: Cross-reference with biological databases and literature
- **Integrating new LLM providers**: Add support for additional AI models
- **Quality control**: Implement data validation and consistency checking pipelines
- **Production enhancements**: Improve scalability, performance, and ML models
- **Performance optimization**: Enhance evaluation tools and benchmarking
