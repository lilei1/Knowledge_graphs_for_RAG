# Advanced Cypher Queries for Expanded Maize Knowledge Graph

This document contains example Cypher queries to explore your expanded maize knowledge graph with 115 nodes and 127 relationships.

## Basic Exploration Queries

### Count all nodes and relationships
```cypher
MATCH (n) RETURN count(n) as total_nodes;
MATCH ()-[r]->() RETURN count(r) as total_relationships;
```

### Show all node types and their counts
```cypher
MATCH (n)
RETURN labels(n)[0] as node_type, count(n) as count
ORDER BY count DESC;
```

### Show all relationship types and their counts
```cypher
MATCH ()-[r]->()
RETURN type(r) as relationship_type, count(r) as count
ORDER BY count DESC;
```

## Gene-Centric Queries

### Find all genes and their regulated traits
```cypher
MATCH (g:Gene)-[:REGULATES]->(t:Trait)
RETURN g.name as gene, t.name as trait
ORDER BY g.name;
```

### Find genes involved in multiple pathways
```cypher
MATCH (g:Gene)-[:PARTICIPATES_IN]->(p:Pathway)
WITH g, collect(p.name) as pathways
WHERE size(pathways) > 1
RETURN g.name as gene, pathways;
```

### Find genes with molecular markers
```cypher
MATCH (g:Gene)-[:HAS_MARKER]->(m:Marker)
RETURN g.name as gene, m.name as marker
ORDER BY g.name;
```

## Pathway Analysis Queries

### Find complete gene → pathway → trait connections
```cypher
MATCH (g:Gene)-[:PARTICIPATES_IN]->(p:Pathway)-[:REGULATES]->(t:Trait)
RETURN g.name as gene, p.name as pathway, t.name as trait
ORDER BY p.name, g.name;
```

### Find all genes in the ABA signaling pathway
```cypher
MATCH (g:Gene)-[:PARTICIPATES_IN]->(p:Pathway {name: "ABA Signaling Pathway"})
RETURN g.name as gene
ORDER BY g.name;
```

### Find pathways that regulate drought tolerance
```cypher
MATCH (p:Pathway)-[:REGULATES]->(t:Trait {name: "Drought Tolerance"})
RETURN p.name as pathway;
```

## QTL and Genomic Queries

### Find complete gene → trait → QTL → chromosome pathways
```cypher
MATCH path = (g:Gene)-[:REGULATES]->(t:Trait)-[:ASSOCIATED_WITH]->(q:QTL)-[:LOCATED_ON]->(c:Chromosome)
RETURN g.name as gene, t.name as trait, q.name as qtl, c.name as chromosome
ORDER BY c.name, g.name;
```

### Find all QTLs on a specific chromosome
```cypher
MATCH (q:QTL)-[:LOCATED_ON]->(c:Chromosome {name: "Chromosome 1"})
RETURN q.name as qtl
ORDER BY q.name;
```

### Find traits with both genes and QTLs
```cypher
MATCH (g:Gene)-[:REGULATES]->(t:Trait)<-[:ASSOCIATED_WITH]-(q:QTL)
RETURN t.name as trait, collect(DISTINCT g.name) as genes, collect(DISTINCT q.name) as qtls
ORDER BY t.name;
```

## Genotype and Breeding Queries

### Find genotypes with multiple desirable traits
```cypher
MATCH (gt:Genotype)-[:HAS_TRAIT]->(t:Trait)
WITH gt, collect(t.name) as traits
WHERE size(traits) >= 2
RETURN gt.name as genotype, traits
ORDER BY size(traits) DESC, gt.name;
```

### Find genotypes suitable for drought conditions
```cypher
MATCH (gt:Genotype)-[:HAS_TRAIT]->(t:Trait)
WHERE t.name CONTAINS "Drought" OR t.name CONTAINS "Deep Root"
RETURN gt.name as genotype, t.name as trait
ORDER BY gt.name;
```

### Find genotypes tested in multiple trials
```cypher
MATCH (gt:Genotype)-[:TESTED_IN]->(trial:Trial)
WITH gt, collect(trial.name) as trials
WHERE size(trials) > 1
RETURN gt.name as genotype, trials
ORDER BY size(trials) DESC;
```

## Field Trial and Environmental Queries

### Find trials conducted under stress conditions
```cypher
MATCH (trial:Trial)-[:CONDUCTED_IN]->(loc:Location)-[:HAS_WEATHER]->(w:Weather)
WHERE w.name CONTAINS "Drought" OR w.name CONTAINS "Stress" OR w.name CONTAINS "High"
RETURN trial.name as trial, loc.name as location, w.name as weather
ORDER BY trial.name;
```

### Find genotypes tested under drought conditions
```cypher
MATCH (gt:Genotype)-[:TESTED_IN]->(trial:Trial)-[:CONDUCTED_IN]->(loc:Location)-[:HAS_WEATHER]->(w:Weather {name: "Drought"})
RETURN gt.name as genotype, trial.name as trial, loc.name as location
ORDER BY gt.name;
```

### Find what traits were measured in each location
```cypher
MATCH (trial:Trial)-[:CONDUCTED_IN]->(loc:Location)
MATCH (trial)-[:MEASURED]->(trait:Trait)
RETURN loc.name as location, collect(DISTINCT trait.name) as traits_measured
ORDER BY loc.name;
```

## Molecular Marker Queries

### Find SNP markers and their associated traits
```cypher
MATCH (m:Marker)-[:ASSOCIATED_WITH]->(t:Trait)
WHERE m.name STARTS WITH "SNP_"
RETURN m.name as snp_marker, t.name as trait
ORDER BY m.name;
```

### Find SSR markers linked to QTLs
```cypher
MATCH (m:Marker)-[:LINKED_TO]->(q:QTL)
WHERE m.name STARTS WITH "SSR_"
RETURN m.name as ssr_marker, q.name as qtl
ORDER BY m.name;
```

### Find genes with both markers and pathway information
```cypher
MATCH (g:Gene)-[:HAS_MARKER]->(m:Marker)
MATCH (g)-[:PARTICIPATES_IN]->(p:Pathway)
RETURN g.name as gene, m.name as marker, p.name as pathway
ORDER BY g.name;
```

## Complex Multi-hop Queries

### Find the shortest path between two specific genes
```cypher
MATCH path = shortestPath((g1:Gene {name: "DREB2A"})-[*]-(g2:Gene {name: "ZmVPP1"}))
RETURN path;
```

### Find all genes that could affect drought tolerance (direct or indirect)
```cypher
MATCH (g:Gene)-[:REGULATES|PARTICIPATES_IN*1..2]->(t:Trait {name: "Drought Tolerance"})
RETURN DISTINCT g.name as gene
ORDER BY g.name;
```

### Find genotypes that share traits with B73
```cypher
MATCH (b73:Genotype {name: "B73"})-[:HAS_TRAIT]->(shared_trait:Trait)<-[:HAS_TRAIT]-(other:Genotype)
WHERE other.name <> "B73"
RETURN other.name as genotype, collect(shared_trait.name) as shared_traits
ORDER BY size(shared_traits) DESC, other.name;
```

## Breeding and Selection Queries

### Find parent genotypes for drought tolerance breeding
```cypher
MATCH (gt:Genotype)-[:HAS_TRAIT]->(t:Trait)
WHERE t.name CONTAINS "Drought" OR t.name CONTAINS "Deep Root" OR t.name CONTAINS "Water"
RETURN gt.name as potential_parent, collect(t.name) as drought_related_traits
ORDER BY size(drought_related_traits) DESC;
```

### Find complementary genotypes for trait stacking
```cypher
MATCH (gt1:Genotype)-[:HAS_TRAIT]->(t1:Trait)
MATCH (gt2:Genotype)-[:HAS_TRAIT]->(t2:Trait)
WHERE gt1.name < gt2.name AND t1.name <> t2.name
WITH gt1, gt2, collect(DISTINCT t1.name) + collect(DISTINCT t2.name) as combined_traits
RETURN gt1.name as parent1, gt2.name as parent2, combined_traits
ORDER BY size(combined_traits) DESC
LIMIT 10;
```

## Statistical and Summary Queries

### Count traits per chromosome
```cypher
MATCH (t:Trait)-[:ASSOCIATED_WITH]->(q:QTL)-[:LOCATED_ON]->(c:Chromosome)
RETURN c.name as chromosome, count(DISTINCT t) as trait_count
ORDER BY trait_count DESC;
```

### Find the most connected nodes (highest degree)
```cypher
MATCH (n)
WITH n, size((n)--()) as degree
RETURN labels(n)[0] as node_type, n.name as name, degree
ORDER BY degree DESC
LIMIT 10;
```

### Find orphan nodes (nodes with no connections)
```cypher
MATCH (n)
WHERE NOT (n)--()
RETURN labels(n)[0] as node_type, n.name as name;
```

## Use these queries in:
1. **Neo4j Browser**: http://localhost:7474
2. **Python scripts**: Using the Neo4jConnection class
3. **Jupyter notebooks**: For interactive analysis

Remember to replace specific names in the queries with your own values of interest!
