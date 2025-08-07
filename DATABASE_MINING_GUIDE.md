# Database Mining Guide for Knowledge Graph Construction

This guide shows you how to extract structured biological data from specialized databases like MaizeGDB, Gramene, KEGG, and others to build comprehensive knowledge graphs.

## 🎯 **Why Database Mining?**

Database mining is often **more reliable** than literature mining because:
- **Pre-curated data**: Expert-validated relationships
- **Structured format**: Consistent data organization
- **Comprehensive coverage**: Systematic data collection
- **Regular updates**: Maintained by domain experts
- **API access**: Programmatic data retrieval

## 🗄️ **Key Databases for Maize Research**

### **1. MaizeGDB (Maize Genetics and Genomics Database)**
- **URL**: https://www.maizegdb.org/
- **Content**: Genes, QTLs, genetic maps, phenotypes, publications
- **Access**: Web interface, no public REST API (requires web scraping)
- **Data Types**: Gene-trait associations, QTL mappings, genetic markers

### **2. Gramene (Plant Comparative Genomics)**
- **URL**: https://www.gramene.org/
- **Content**: Comparative genomics, pathways, ontologies
- **Access**: REST API available
- **API Docs**: https://data.gramene.org/docs/
- **Data Types**: Gene families, pathways, ontology terms

### **3. KEGG (Kyoto Encyclopedia of Genes and Genomes)**
- **URL**: https://www.kegg.jp/
- **Content**: Metabolic pathways, gene functions, diseases
- **Access**: REST API available
- **API Docs**: https://www.kegg.jp/kegg/rest/
- **Data Types**: Pathway-gene associations, enzyme functions

### **4. UniProt (Universal Protein Resource)**
- **URL**: https://www.uniprot.org/
- **Content**: Protein sequences, functions, annotations
- **Access**: REST API available
- **API Docs**: https://www.uniprot.org/help/api
- **Data Types**: Protein functions, GO terms, domains

### **5. Ensembl Plants**
- **URL**: https://plants.ensembl.org/
- **Content**: Genome annotations, gene models, variants
- **Access**: REST API available
- **API Docs**: https://rest.ensembl.org/
- **Data Types**: Gene locations, transcripts, homologs

### **6. Phytozome (Plant Genomics Portal)**
- **URL**: https://phytozome-next.jgi.doe.gov/
- **Content**: Plant genomes, gene families, functional annotations
- **Access**: API available with registration
- **Data Types**: Gene families, functional domains, expression

## 🔧 **Mining Approaches**

### **Approach 1: REST APIs (Recommended)**

Most modern databases provide REST APIs:

```python
import requests

# Example: KEGG API
def get_kegg_pathways(organism="zma"):  # zma = Zea mays
    url = f"http://rest.kegg.jp/list/pathway/{organism}"
    response = requests.get(url)
    return response.text

# Example: UniProt API
def search_uniprot(gene_name, organism_id=4577):  # 4577 = Zea mays
    url = "https://rest.uniprot.org/uniprotkb/search"
    params = {
        'query': f'organism_id:{organism_id} AND gene:{gene_name}',
        'format': 'json'
    }
    response = requests.get(url, params=params)
    return response.json()
```

### **Approach 2: Web Scraping (When No API)**

For databases without APIs (like MaizeGDB):

```python
import requests
from bs4 import BeautifulSoup

def scrape_maizegdb_gene(gene_name):
    # Search for gene
    search_url = f"https://www.maizegdb.org/gene_center/gene/{gene_name}"
    response = requests.get(search_url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract gene information
    # (Implementation depends on page structure)
    return extracted_data
```

### **Approach 3: Database Downloads**

Many databases offer bulk downloads:

```python
import pandas as pd

# Download and parse database files
def parse_database_file(filename):
    df = pd.read_csv(filename, sep='\t')
    relationships = []
    
    for _, row in df.iterrows():
        relationships.append({
            'subject': row['gene'],
            'predicate': 'has_function',
            'object': row['function']
        })
    
    return relationships
```

## 🚀 **Implementation Example**

Let's run the database mining script:

```bash
python3 database_mining.py
```

This will extract data from multiple databases and create `toydata/database_mined.csv`.

## 📊 **Data Extraction Strategies**

### **1. Gene-Centric Mining**
Start with a list of genes and collect all associated information:

```python
genes = ["DREB2A", "ZmVPP1", "ZmNF-YB2"]

for gene in genes:
    # Get function from UniProt
    function_data = mine_uniprot(gene)
    
    # Get location from Ensembl
    location_data = mine_ensembl(gene)
    
    # Get pathways from KEGG
    pathway_data = mine_kegg(gene)
```

### **2. Trait-Centric Mining**
Start with traits and find associated genes/QTLs:

```python
traits = ["drought tolerance", "yield", "flowering time"]

for trait in traits:
    # Get QTLs from Gramene
    qtl_data = mine_gramene_qtls(trait)
    
    # Get genes from MaizeGDB
    gene_data = mine_maizegdb_traits(trait)
```

### **3. Pathway-Centric Mining**
Start with pathways and collect genes/functions:

```python
pathways = ["ABA signaling", "photosynthesis", "starch biosynthesis"]

for pathway in pathways:
    # Get genes from KEGG
    gene_data = mine_kegg_pathway_genes(pathway)
    
    # Get functions from UniProt
    function_data = mine_pathway_functions(pathway)
```

## 🔍 **Quality Control**

### **1. Data Validation**
```python
def validate_gene_names(relationships):
    """Validate gene names against known databases"""
    valid_genes = set()
    
    for rel in relationships:
        if rel['subject'].startswith('Zm'):  # Maize gene naming
            valid_genes.add(rel['subject'])
    
    return valid_genes

def cross_reference_databases(gene, databases):
    """Cross-reference gene across multiple databases"""
    results = {}
    for db_name, db_function in databases.items():
        results[db_name] = db_function(gene)
    return results
```

### **2. Consistency Checking**
```python
def check_consistency(relationships):
    """Check for conflicting information"""
    gene_functions = {}
    
    for rel in relationships:
        if rel['predicate'] == 'has_function':
            gene = rel['subject']
            function = rel['object']
            
            if gene in gene_functions:
                if function not in gene_functions[gene]:
                    print(f"Potential conflict for {gene}: {gene_functions[gene]} vs {function}")
            else:
                gene_functions[gene] = [function]
```

## 📈 **Advanced Mining Techniques**

### **1. Batch Processing**
```python
def batch_mine_genes(gene_list, batch_size=10):
    """Process genes in batches to avoid rate limits"""
    results = []
    
    for i in range(0, len(gene_list), batch_size):
        batch = gene_list[i:i+batch_size]
        batch_results = process_gene_batch(batch)
        results.extend(batch_results)
        
        time.sleep(5)  # Rate limiting
    
    return results
```

### **2. Parallel Processing**
```python
from concurrent.futures import ThreadPoolExecutor
import threading

def parallel_mine_databases(gene_list, databases):
    """Mine multiple databases in parallel"""
    results = []
    
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = []
        
        for db_name, db_function in databases.items():
            future = executor.submit(db_function, gene_list)
            futures.append((db_name, future))
        
        for db_name, future in futures:
            try:
                db_results = future.result(timeout=60)
                results.extend(db_results)
            except Exception as e:
                print(f"Error mining {db_name}: {e}")
    
    return results
```

### **3. Incremental Updates**
```python
def incremental_database_update(last_update_date):
    """Only fetch data updated since last run"""
    
    # Check for new entries since last update
    new_entries = check_database_updates(last_update_date)
    
    # Process only new/updated entries
    new_relationships = []
    for entry in new_entries:
        relationships = process_database_entry(entry)
        new_relationships.extend(relationships)
    
    return new_relationships
```

## 🔄 **Integration Workflow**

### **Complete Database Mining Pipeline:**

```bash
# 1. Mine from databases
python3 database_mining.py

# 2. Validate and clean data
python3 validate_database_data.py

# 3. Add to knowledge graph
python3 expand_maize_kg.py

# 4. Verify integration
python3 visualize_kg.py
```

## 📋 **Best Practices**

### **1. Rate Limiting**
- Respect API rate limits (usually 1-10 requests/second)
- Use delays between requests
- Implement exponential backoff for failures

### **2. Error Handling**
- Handle network timeouts gracefully
- Retry failed requests with backoff
- Log errors for debugging

### **3. Data Caching**
- Cache API responses to avoid repeated requests
- Store intermediate results
- Use database timestamps for incremental updates

### **4. API Key Management**
- Store API keys securely (environment variables)
- Rotate keys regularly
- Monitor usage quotas

## 🎯 **Expected Results**

With database mining, you can extract:

- **1000+ gene-function relationships** from UniProt
- **500+ pathway associations** from KEGG
- **200+ QTL mappings** from Gramene
- **Genomic locations** for all genes from Ensembl
- **Curated phenotype data** from MaizeGDB

This creates a **comprehensive, validated knowledge graph** based on expert-curated data!

## 🚀 **Next Steps**

1. **Run the demo**: `python3 database_mining.py`
2. **Set up API access** for databases requiring authentication
3. **Customize for your research area** (focus on specific traits/pathways)
4. **Implement quality control** and validation steps
5. **Schedule regular updates** to keep data current

Database mining provides the most reliable foundation for biological knowledge graphs! 🧬📊
