#!/usr/bin/env python3
"""
PubMed Literature Mining for Maize Knowledge Graph

This script demonstrates how to:
1. Search PubMed for maize genetics papers
2. Extract abstracts
3. Use LLMs to extract structured relationships
4. Generate CSV files for knowledge graph expansion

Requirements:
pip install biopython openai anthropic requests
"""

import json
import csv
import os
import time
from typing import List, Dict, Any, Optional
from Bio import Entrez
import requests

# Set your email for PubMed (required)
Entrez.email = "your.email@example.com"

class LiteratureMiner:
    """Class to handle literature mining and LLM extraction"""
    
    def __init__(self, llm_provider="openai", api_key=None):
        self.llm_provider = llm_provider
        self.api_key = api_key or os.getenv(f"{llm_provider.upper()}_API_KEY")
    
    def search_pubmed(self, query: str, max_results: int = 10) -> List[str]:
        """Search PubMed and return list of PMIDs"""
        try:
            handle = Entrez.esearch(db="pubmed", term=query, retmax=max_results)
            search_results = Entrez.read(handle)
            handle.close()
            return search_results["IdList"]
        except Exception as e:
            print(f"Error searching PubMed: {e}")
            return []
    
    def fetch_abstracts(self, pmids: List[str]) -> List[Dict[str, str]]:
        """Fetch abstracts for given PMIDs"""
        abstracts = []
        try:
            handle = Entrez.efetch(db="pubmed", id=",".join(pmids), rettype="abstract", retmode="text")
            records = Entrez.read(handle)
            handle.close()
            
            for record in records['PubmedArticle']:
                try:
                    pmid = str(record['MedlineCitation']['PMID'])
                    title = record['MedlineCitation']['Article']['ArticleTitle']
                    
                    # Extract abstract text
                    abstract_sections = record['MedlineCitation']['Article'].get('Abstract', {}).get('AbstractText', [])
                    if abstract_sections:
                        if isinstance(abstract_sections, list):
                            abstract = " ".join([str(section) for section in abstract_sections])
                        else:
                            abstract = str(abstract_sections)
                    else:
                        abstract = "No abstract available"
                    
                    abstracts.append({
                        'pmid': pmid,
                        'title': title,
                        'abstract': abstract
                    })
                except Exception as e:
                    print(f"Error processing record: {e}")
                    continue
                    
        except Exception as e:
            print(f"Error fetching abstracts: {e}")
        
        return abstracts
    
    def extract_with_openai(self, abstract: str) -> List[Dict[str, str]]:
        """Extract relationships using OpenAI GPT"""
        try:
            import openai
            openai.api_key = self.api_key
            
            prompt = self._create_extraction_prompt(abstract)
            
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a scientific literature mining expert specializing in plant genetics."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=1000
            )
            
            result = response.choices[0].message.content
            return self._parse_llm_response(result)
            
        except Exception as e:
            print(f"Error with OpenAI extraction: {e}")
            return []
    
    def extract_with_anthropic(self, abstract: str) -> List[Dict[str, str]]:
        """Extract relationships using Anthropic Claude"""
        try:
            import anthropic
            
            client = anthropic.Anthropic(api_key=self.api_key)
            prompt = self._create_extraction_prompt(abstract)
            
            response = client.messages.create(
                model="claude-3-sonnet-20240229",
                max_tokens=1000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            
            result = response.content[0].text
            return self._parse_llm_response(result)
            
        except Exception as e:
            print(f"Error with Anthropic extraction: {e}")
            return []
    
    def _create_extraction_prompt(self, abstract: str) -> str:
        """Create extraction prompt for LLM"""
        return f"""
        Extract structured biological relationships from this maize/corn genetics abstract.
        Focus on genes, traits, genotypes, QTLs, chromosomes, pathways, and markers.
        
        Return ONLY a valid JSON array of relationships in this format:
        [
            {{"subject": "gene_name", "predicate": "regulates", "object": "trait_name"}},
            {{"subject": "genotype_name", "predicate": "has_trait", "object": "trait_name"}},
            {{"subject": "trait_name", "predicate": "associated_with", "object": "qtl_name"}},
            {{"subject": "qtl_name", "predicate": "located_on", "object": "chromosome_name"}},
            {{"subject": "gene_name", "predicate": "participates_in", "object": "pathway_name"}},
            {{"subject": "gene_name", "predicate": "has_marker", "object": "marker_name"}}
        ]
        
        Rules:
        - Use exact gene names from the text (e.g., ZmDREB2A, ZmVPP1)
        - Use descriptive trait names (e.g., "Drought Tolerance", "Yield")
        - Use standard genotype names (e.g., B73, Mo17)
        - Use QTL format like qDT1.1 if mentioned
        - Use "Chromosome X" format
        - Only extract explicitly stated relationships
        - Return empty array [] if no clear relationships found
        
        Abstract: {abstract}
        
        JSON:
        """
    
    def _parse_llm_response(self, response: str) -> List[Dict[str, str]]:
        """Parse LLM response and extract JSON"""
        try:
            # Try to find JSON in the response
            start = response.find('[')
            end = response.rfind(']') + 1
            if start != -1 and end != 0:
                json_str = response[start:end]
                return json.loads(json_str)
            else:
                return []
        except Exception as e:
            print(f"Error parsing LLM response: {e}")
            return []
    
    def extract_relationships(self, abstract: str) -> List[Dict[str, str]]:
        """Extract relationships using configured LLM provider"""
        if self.llm_provider == "openai":
            return self.extract_with_openai(abstract)
        elif self.llm_provider == "anthropic":
            return self.extract_with_anthropic(abstract)
        else:
            print(f"Unsupported LLM provider: {self.llm_provider}")
            return []

def main():
    """Main function to demonstrate PubMed mining"""
    print("=== PubMed Literature Mining for Maize Knowledge Graph ===\n")
    
    # Example search queries for maize genetics
    search_queries = [
        "maize drought tolerance genes",
        "corn QTL mapping chromosome",
        "Zea mays transcription factors stress",
        "maize genotype phenotype association"
    ]
    
    # Initialize miner (you'll need API keys for real usage)
    miner = LiteratureMiner(llm_provider="openai")  # or "anthropic"
    
    all_relationships = []
    processed_papers = []
    
    for query in search_queries:
        print(f"Searching PubMed for: '{query}'")
        
        # Search PubMed
        pmids = miner.search_pubmed(query, max_results=5)
        print(f"Found {len(pmids)} papers")
        
        if not pmids:
            continue
        
        # Fetch abstracts
        abstracts = miner.fetch_abstracts(pmids)
        print(f"Retrieved {len(abstracts)} abstracts")
        
        # Process each abstract
        for paper in abstracts:
            print(f"\nProcessing PMID: {paper['pmid']}")
            print(f"Title: {paper['title'][:100]}...")
            
            # Extract relationships (would use real LLM here)
            relationships = miner.extract_relationships(paper['abstract'])
            
            if relationships:
                print(f"Extracted {len(relationships)} relationships:")
                for rel in relationships[:3]:  # Show first 3
                    print(f"  {rel['subject']} --[{rel['predicate']}]--> {rel['object']}")
                if len(relationships) > 3:
                    print(f"  ... and {len(relationships) - 3} more")
                
                all_relationships.extend(relationships)
                processed_papers.append(paper)
            else:
                print("  No relationships extracted")
            
            # Rate limiting
            time.sleep(1)
        
        print("-" * 60)
    
    # Save results
    if all_relationships:
        output_file = "toydata/pubmed_extracted.csv"
        with open(output_file, 'w', newline='') as csvfile:
            fieldnames = ['subject', 'predicate', 'object']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for rel in all_relationships:
                writer.writerow(rel)
        
        print(f"\n=== Results ===")
        print(f"Processed {len(processed_papers)} papers")
        print(f"Extracted {len(all_relationships)} relationships")
        print(f"Saved to: {output_file}")
        
        # Show statistics
        predicates = {}
        for rel in all_relationships:
            pred = rel['predicate']
            predicates[pred] = predicates.get(pred, 0) + 1
        
        print(f"\nRelationship types:")
        for pred, count in sorted(predicates.items()):
            print(f"  {pred}: {count}")
    
    else:
        print("\nNo relationships extracted. Check API keys and connectivity.")
    
    print(f"\n=== Setup Instructions ===")
    print("1. Install: pip install biopython openai anthropic")
    print("2. Set API key: export OPENAI_API_KEY='your-key' or ANTHROPIC_API_KEY='your-key'")
    print("3. Set email: Update Entrez.email in the script")
    print("4. Run this script to extract real literature data")
    print("5. Use expand_maize_kg.py to add extracted data to your graph")

if __name__ == "__main__":
    main()
