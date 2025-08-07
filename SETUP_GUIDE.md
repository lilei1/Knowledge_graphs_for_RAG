# Maize Knowledge Graph Setup Guide

This guide will help you set up and build a knowledge graph for the maize toy data using Neo4j.

## Prerequisites

1. **Neo4j Database**: You need a running Neo4j instance. You can use:
   - Neo4j Desktop (recommended for local development)
   - Neo4j AuraDB (cloud-based)
   - Docker Neo4j container

2. **Python Environment**: Python 3.8 or higher

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set up Neo4j

#### Option A: Neo4j Desktop (Recommended)
1. Download and install [Neo4j Desktop](https://neo4j.com/download/)
2. Create a new project and database
3. Start the database
4. Note the connection details (usually `bolt://localhost:7687`)
5. Set a password for the `neo4j` user

#### Option B: Neo4j AuraDB (Cloud)
1. Go to [Neo4j AuraDB](https://neo4j.com/cloud/aura/)
2. Create a free account and database
3. Note the connection URI and credentials

#### Option C: Docker
```bash
docker run \
    --name neo4j \
    -p7474:7474 -p7687:7687 \
    -d \
    -v $HOME/neo4j/data:/data \
    -v $HOME/neo4j/logs:/logs \
    -v $HOME/neo4j/import:/var/lib/neo4j/import \
    -v $HOME/neo4j/plugins:/plugins \
    --env NEO4J_AUTH=neo4j/your_password_here \
    neo4j:latest
```

### 3. Configure Environment

1. Copy the environment template:
```bash
cp .env.template .env
```

2. Edit `.env` with your Neo4j credentials:
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=your_password_here
NEO4J_DATABASE=neo4j
```

## Building the Knowledge Graph

### Method 1: Using the Python Script

Run the build script directly:
```bash
python build_maize_kg.py
```

This will:
- Connect to Neo4j
- Clear any existing maize data
- Load data from `toydata/maize.csv`
- Create nodes with appropriate labels (Gene, Trait, Genotype, etc.)
- Create relationships between nodes
- Add constraints and indexes
- Verify the graph structure

### Method 2: Using the Jupyter Notebook

1. Start Jupyter:
```bash
jupyter notebook
```

2. Open `notebook/build_maize_kg.ipynb`
3. Run all cells to build and explore the graph

## Data Structure

The knowledge graph will contain the following node types:

- **Gene**: Genetic elements (DREB2A, ZmNAC111, PSY1)
- **Trait**: Phenotypic characteristics (Drought Tolerance, Root Depth, etc.)
- **Genotype**: Maize varieties (B73, Mo17, CML247)
- **QTL**: Quantitative Trait Loci (qDT1.1)
- **Chromosome**: Chromosomal locations (Chromosome 1)
- **Trial**: Field trials (Trial_Ames_2020)
- **Location**: Geographic locations (Ames)
- **Weather**: Environmental conditions (Drought)

## Relationship Types

- `REGULATES`: Gene → Trait
- `HAS_TRAIT`: Genotype → Trait
- `ASSOCIATED_WITH`: Trait → QTL
- `LOCATED_ON`: QTL → Chromosome
- `CONDUCTED_IN`: Trial → Location
- `TESTED_IN`: Genotype → Trial
- `MEASURED`: Trial → Trait
- `HAS_WEATHER`: Location → Weather

## Example Queries

Once the graph is built, you can run these Cypher queries in Neo4j Browser:

### Find all genes and their regulated traits:
```cypher
MATCH (g:Gene)-[:REGULATES]->(t:Trait)
RETURN g.name as gene, t.name as trait
```

### Find genotypes with drought tolerance:
```cypher
MATCH (gt:Genotype)-[:HAS_TRAIT]->(t:Trait {name: "Drought Tolerance"})
RETURN gt.name as genotype
```

### Find the complete pathway from gene to chromosome:
```cypher
MATCH path = (g:Gene)-[:REGULATES]->(t:Trait)-[:ASSOCIATED_WITH]->(q:QTL)-[:LOCATED_ON]->(c:Chromosome)
RETURN g.name as gene, t.name as trait, q.name as qtl, c.name as chromosome
```

### Find trial information:
```cypher
MATCH (trial:Trial)-[:CONDUCTED_IN]->(loc:Location)
MATCH (gt:Genotype)-[:TESTED_IN]->(trial)
MATCH (trial)-[:MEASURED]->(trait:Trait)
RETURN trial.name as trial, loc.name as location, 
       collect(DISTINCT gt.name) as genotypes_tested,
       collect(DISTINCT trait.name) as traits_measured
```

## Verification

After building the graph, you should see:
- 13 nodes total (various types)
- 12 relationships
- Proper node labels and relationship types

## Troubleshooting

### Connection Issues
- Ensure Neo4j is running
- Check your `.env` file credentials
- Verify the URI format (bolt:// for local, neo4j+s:// for AuraDB)

### Permission Issues
- Make sure the Neo4j user has write permissions
- Check if the database name is correct

### Data Issues
- Ensure `toydata/maize.csv` exists and is readable
- Check CSV format (should have subject, predicate, object columns)

## Next Steps

Once your knowledge graph is built, you can:
1. Explore the data using Neo4j Browser
2. Run the existing notebooks (L2-L7) to see advanced querying techniques
3. Extend the graph with additional data
4. Build RAG applications using the knowledge graph

## Support

If you encounter issues:
1. Check the Neo4j logs
2. Verify your environment configuration
3. Ensure all dependencies are installed correctly
