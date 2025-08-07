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
   pip install -r requirements.txt
   ```

2. **Set up Neo4j** (see SETUP_GUIDE.md for detailed instructions)

3. **Configure environment:**
   ```bash
   cp .env.template .env
   # Edit .env with your Neo4j credentials
   ```

4. **Build the knowledge graph:**
   ```bash
   python build_maize_kg.py
   ```

5. **Analyze the graph:**
   ```bash
   python visualize_kg.py
   ```

## Features

- **Automated Knowledge Graph Construction**: Converts CSV data into a structured Neo4j graph
- **Intelligent Node Classification**: Automatically categorizes entities (Genes, Traits, Genotypes, etc.)
- **Relationship Mapping**: Creates meaningful connections between biological entities
- **Interactive Notebooks**: Jupyter notebooks for exploration and analysis
- **Visualization Tools**: Scripts to analyze and export graph data

## Data Model

The knowledge graph represents maize genetic data with the following entities:

- **Genes**: Genetic elements (DREB2A, ZmNAC111, PSY1)
- **Traits**: Phenotypic characteristics (Drought Tolerance, Root Depth, Kernel Color)
- **Genotypes**: Maize varieties (B73, Mo17, CML247)
- **QTLs**: Quantitative Trait Loci (qDT1.1)
- **Chromosomes**: Chromosomal locations
- **Trials**: Field experiments
- **Locations**: Geographic locations
- **Weather**: Environmental conditions

## Example Queries

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

## Getting Started

For detailed setup instructions, see [SETUP_GUIDE.md](SETUP_GUIDE.md).

## Contributing

Feel free to contribute by:
- Adding more data sources
- Improving the data model
- Creating additional analysis tools
- Enhancing visualizations
