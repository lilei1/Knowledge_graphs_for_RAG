# Knowledge Graphs for RAG

This project demonstrates how to build knowledge graphs for Retrieval-Augmented Generation (RAG) using Neo4j, with a focus on maize genetic data.

## Project Structure

```
├── README.md                    # This file
├── SETUP_GUIDE.md              # Detailed setup instructions
├── LITERATURE_MINING_GUIDE.md  # Guide for extracting data from literature
├── DATABASE_MINING_GUIDE.md    # Guide for mining biological databases
├── DATA_MINING_SUMMARY.md      # Complete overview of all mining approaches
├── requirements.txt            # Python dependencies
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

## Quick Start

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

## Features

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
