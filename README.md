# Knowledge Graphs for RAG

This project demonstrates how to build knowledge graphs for Retrieval-Augmented Generation (RAG) using Neo4j, with a focus on maize genetic data.

## Project Structure

```
├── README.md                    # This file
├── SETUP_GUIDE.md              # Detailed setup instructions
├── requirements.txt            # Python dependencies
├── .env.template              # Environment configuration template
├── build_maize_kg.py          # Main script to build the knowledge graph
├── visualize_kg.py            # Script to analyze and visualize the graph
├── toydata/
│   └── maize.csv              # Sample maize genetic data
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

6. **Analyze the graph:**
   ```bash
   python3 visualize_kg.py
   ```

## Features

- **Automated Knowledge Graph Construction**: Converts CSV data into a structured Neo4j graph
- **Intelligent Node Classification**: Automatically categorizes entities across 10+ types
- **Comprehensive Data Model**: Supports genes, traits, genotypes, QTLs, pathways, markers, and more
- **Multi-source Data Integration**: Combines genetic, phenotypic, and experimental data
- **Advanced Query Examples**: 50+ Cypher queries for complex biological analysis
- **Interactive Notebooks**: Jupyter notebooks for exploration and analysis
- **Visualization Tools**: Scripts to analyze and export graph data
- **Scalable Architecture**: Easily expandable with new CSV data sources

## Data Model

The expanded knowledge graph represents comprehensive maize genetic data with:

### **Node Types (115 total nodes):**
- **18 Genes**: DREB2A, ZmVPP1, ZmNF-YB2, ZmCCT, etc.
- **32 Traits**: Drought Tolerance, Cold Tolerance, Nitrogen Use Efficiency, etc.
- **12 Genotypes**: B73, Mo17, W22, Oh43, PH207, etc.
- **10 QTLs**: qDT1.1, qCT2.1, qNUE3.1, etc. (mapped across all 10 chromosomes)
- **10 Chromosomes**: Complete maize genome representation
- **7 Pathways**: ABA Signaling, Defense Response, Anthocyanin Biosynthesis, etc.
- **10 Markers**: SNP and SSR markers linked to genes and QTLs
- **6 Trials**: Multi-location field experiments (2020-2023)
- **6 Locations**: Ames, Iowa, Nebraska, Illinois, Kansas, Minnesota
- **3 Weather**: Environmental conditions (Drought, Cold Stress, High Temperature)

### **Relationship Types (127 total relationships):**
- **REGULATES**: Gene → Trait regulation
- **HAS_TRAIT**: Genotype → Trait associations
- **PARTICIPATES_IN**: Gene → Pathway involvement
- **ASSOCIATED_WITH**: Trait → QTL mappings
- **LOCATED_ON**: QTL → Chromosome positions
- **HAS_MARKER**: Gene → Molecular marker links
- **TESTED_IN**: Genotype → Trial participation
- **MEASURED**: Trial → Trait evaluation
- **CONDUCTED_IN**: Trial → Location mapping
- **HAS_WEATHER**: Location → Environmental conditions
- **LINKED_TO**: Marker → QTL associations

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

## Getting Started

For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md).

## Contributing

Feel free to contribute by:
- Adding more data sources
- Improving the data model
- Creating additional analysis tools
- Enhancing visualizations
