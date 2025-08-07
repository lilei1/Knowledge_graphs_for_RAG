# Literature Mining with LLMs for Knowledge Graph Construction

This guide shows you how to extract real biological data from scientific literature using Large Language Models (LLMs) to expand your maize knowledge graph.

## 🎯 **Why Literature Mining?**

Instead of creating synthetic data, you can extract **real, validated relationships** from published research papers to build a comprehensive and accurate knowledge graph.

## 🔧 **Available Tools**

### 1. **`literature_mining.py`** - Demo with Example Abstracts
- Uses realistic abstracts based on real research
- Shows LLM prompt engineering for relationship extraction
- Demonstrates the extraction workflow
- **Run:** `python3 literature_mining.py`

### 2. **`pubmed_mining.py`** - Real PubMed Integration
- Searches PubMed for maize genetics papers
- Fetches actual abstracts
- Uses OpenAI/Anthropic APIs for extraction
- **Requires:** API keys and additional packages

## 🚀 **Approach 1: Using Existing LLM APIs**

### **Setup:**
```bash
pip install biopython openai anthropic requests
export OPENAI_API_KEY="your-openai-key"
# OR
export ANTHROPIC_API_KEY="your-anthropic-key"
```

### **Usage:**
```python
from pubmed_mining import LiteratureMiner

# Initialize with your preferred LLM
miner = LiteratureMiner(llm_provider="openai")  # or "anthropic"

# Search PubMed
pmids = miner.search_pubmed("maize drought tolerance genes", max_results=10)

# Fetch abstracts
abstracts = miner.fetch_abstracts(pmids)

# Extract relationships
for paper in abstracts:
    relationships = miner.extract_relationships(paper['abstract'])
    # relationships = [{"subject": "DREB2A", "predicate": "regulates", "object": "Drought Tolerance"}, ...]
```

## 🔬 **Approach 2: Using Local LLMs**

For privacy or cost concerns, use local models:

### **Setup Ollama (Local LLM):**
```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Download a model
ollama pull llama2:13b
# or
ollama pull mistral:7b
```

### **Integration Example:**
```python
import requests
import json

def extract_with_ollama(abstract, model="llama2:13b"):
    prompt = create_extraction_prompt(abstract)
    
    response = requests.post('http://localhost:11434/api/generate',
                           json={
                               'model': model,
                               'prompt': prompt,
                               'stream': False
                           })
    
    return parse_response(response.json()['response'])
```

## 📚 **Approach 3: Specialized Biomedical LLMs**

Use models trained specifically on biomedical literature:

### **BioBERT/PubMedBERT:**
```python
from transformers import AutoTokenizer, AutoModel
import torch

# Load biomedical model
tokenizer = AutoTokenizer.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")
model = AutoModel.from_pretrained("microsoft/BiomedNLP-PubMedBERT-base-uncased-abstract")

# Use for relationship extraction
def extract_with_biobert(text):
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
    outputs = model(**inputs)
    # Process outputs for relationship extraction
    return relationships
```

## 🎯 **Prompt Engineering for Biological Data**

### **Key Prompt Components:**

1. **Clear Instructions:**
```
Extract structured biological relationships from this maize genetics abstract.
Focus on genes, traits, genotypes, QTLs, chromosomes, pathways, and markers.
```

2. **Specific Format:**
```json
[
    {"subject": "gene_name", "predicate": "regulates", "object": "trait_name"},
    {"subject": "genotype_name", "predicate": "has_trait", "object": "trait_name"}
]
```

3. **Domain Rules:**
```
- Use exact gene names (e.g., ZmDREB2A, ZmVPP1)
- Use descriptive trait names (e.g., "Drought Tolerance")
- Use standard genotype names (e.g., B73, Mo17)
- Only extract explicitly stated relationships
```

## 📊 **Data Sources for Mining**

### **1. PubMed/NCBI**
- **Search queries:** "maize drought tolerance", "corn QTL mapping"
- **API:** Biopython Entrez
- **Coverage:** Comprehensive biomedical literature

### **2. Plant Science Journals**
- Plant Cell, Plant Physiology, Theoretical and Applied Genetics
- **Access:** Many have APIs or are open access

### **3. Specialized Databases**
- **MaizeGDB:** Maize genetics and genomics database
- **Gramene:** Comparative plant genomics
- **KEGG:** Pathway information

### **4. Preprint Servers**
- **bioRxiv:** Biology preprints
- **Often more recent:** Latest research findings

## 🔄 **Complete Workflow**

### **Step 1: Search and Collect**
```python
# Search multiple sources
queries = [
    "maize drought tolerance genes",
    "corn QTL chromosome mapping", 
    "Zea mays transcription factors"
]

papers = []
for query in queries:
    pmids = search_pubmed(query, max_results=20)
    abstracts = fetch_abstracts(pmids)
    papers.extend(abstracts)
```

### **Step 2: Extract Relationships**
```python
all_relationships = []
for paper in papers:
    relationships = extract_with_llm(paper['abstract'])
    all_relationships.extend(relationships)
```

### **Step 3: Quality Control**
```python
# Remove duplicates
unique_relationships = remove_duplicates(all_relationships)

# Validate gene names against databases
validated_relationships = validate_gene_names(unique_relationships)

# Check for consistency
consistent_relationships = check_consistency(validated_relationships)
```

### **Step 4: Integration**
```python
# Save to CSV
save_to_csv(consistent_relationships, "toydata/literature_mined.csv")

# Add to knowledge graph
python3 expand_maize_kg.py
```

## 📈 **Quality Metrics**

### **Precision:** How many extracted relationships are correct?
- Manual validation by domain experts
- Cross-reference with known databases
- Check against multiple papers

### **Recall:** How many true relationships were missed?
- Compare with manually curated datasets
- Use multiple LLMs and combine results

### **Consistency:** Are relationships consistent across papers?
- Check for contradictions
- Resolve conflicts using paper quality/recency

## 💡 **Best Practices**

### **1. Prompt Optimization**
- Test prompts on known papers
- Iterate based on extraction quality
- Use few-shot examples in prompts

### **2. Multi-Model Ensemble**
- Use multiple LLMs (GPT-4, Claude, Llama)
- Combine results for higher accuracy
- Vote on conflicting extractions

### **3. Domain Validation**
- Collaborate with plant biologists
- Use existing databases for validation
- Implement confidence scoring

### **4. Incremental Processing**
- Process papers in batches
- Save intermediate results
- Resume from failures

## 🔧 **Implementation Example**

Let's extract real data and add it to your graph:

```bash
# 1. Run the demo to see how it works
python3 literature_mining.py

# 2. Check the extracted data
head toydata/literature_extracted.csv

# 3. Add to your knowledge graph
python3 expand_maize_kg.py

# 4. Analyze the expanded graph
python3 visualize_kg.py
```

## 🎯 **Expected Results**

With literature mining, you can extract:
- **500-1000+ gene-trait relationships** from recent papers
- **Validated QTL mappings** from mapping studies  
- **Pathway information** from functional studies
- **Genotype-environment interactions** from field trials
- **Molecular marker associations** from GWAS studies

This creates a **knowledge graph based on real scientific evidence** rather than synthetic data!

## 🚀 **Next Steps**

1. **Set up API keys** for OpenAI/Anthropic
2. **Run literature mining** on your research area
3. **Validate extracted relationships** with experts
4. **Integrate with your knowledge graph**
5. **Build RAG applications** using real biological knowledge

The combination of LLMs + literature mining + knowledge graphs creates a powerful system for biological discovery and analysis!
