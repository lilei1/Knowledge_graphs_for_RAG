#!/usr/bin/env python3
"""
Real API Mining Examples for Biological Databases

This script shows actual API calls to real databases.
Some require internet connection and may have rate limits.
"""

import requests
import json
import csv
import time
import pandas as pd
from typing import List, Dict, Any
from urllib.parse import quote

class RealAPIMiner:
    """Real API mining from biological databases"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; BiologyResearcher/1.0)'
        })
    
    def mine_kegg_real(self) -> List[Dict[str, str]]:
        """Mine real data from KEGG REST API"""
        print("Mining KEGG database (real API calls)...")
        
        relationships = []
        
        try:
            # Get maize pathways
            pathway_url = "http://rest.kegg.jp/list/pathway/zma"
            response = self.session.get(pathway_url, timeout=10)
            
            if response.status_code == 200:
                pathways = response.text.strip().split('\n')
                
                for pathway_line in pathways[:5]:  # Limit to first 5
                    if '\t' in pathway_line:
                        pathway_id, pathway_name = pathway_line.split('\t', 1)
                        
                        # Clean pathway name
                        clean_name = pathway_name.replace(' - Zea mays (maize)', '')
                        
                        # Categorize pathway
                        if any(word in clean_name.lower() for word in ['metabolic', 'metabolism']):
                            category = "Metabolic Pathway"
                        elif any(word in clean_name.lower() for word in ['biosynthesis', 'synthesis']):
                            category = "Biosynthesis Pathway"
                        elif any(word in clean_name.lower() for word in ['signaling', 'signal']):
                            category = "Signaling Pathway"
                        else:
                            category = "Biological Pathway"
                        
                        relationships.append({
                            "subject": clean_name,
                            "predicate": "is_a",
                            "object": category
                        })
                        
                        # Get genes in this pathway
                        gene_relationships = self._get_kegg_pathway_genes(pathway_id, clean_name)
                        relationships.extend(gene_relationships)
                        
                        time.sleep(1)  # Rate limiting
            
        except Exception as e:
            print(f"Error mining KEGG: {e}")
        
        return relationships
    
    def _get_kegg_pathway_genes(self, pathway_id: str, pathway_name: str) -> List[Dict[str, str]]:
        """Get genes for a specific KEGG pathway"""
        relationships = []
        
        try:
            gene_url = f"http://rest.kegg.jp/get/{pathway_id}"
            response = self.session.get(gene_url, timeout=10)
            
            if response.status_code == 200:
                content = response.text
                
                # Parse gene section (simplified)
                if "GENE" in content:
                    gene_section = content.split("GENE")[1].split("///")[0]
                    lines = gene_section.split('\n')
                    
                    for line in lines[:3]:  # Limit to 3 genes per pathway
                        if line.strip() and not line.startswith(' '):
                            parts = line.strip().split()
                            if len(parts) >= 2:
                                gene_id = parts[0]
                                gene_name = parts[1] if len(parts) > 1 else gene_id
                                
                                relationships.append({
                                    "subject": gene_name,
                                    "predicate": "participates_in",
                                    "object": pathway_name
                                })
        
        except Exception as e:
            print(f"Error getting genes for pathway {pathway_id}: {e}")
        
        return relationships
    
    def mine_uniprot_real(self, gene_list: List[str]) -> List[Dict[str, str]]:
        """Mine real data from UniProt REST API"""
        print("Mining UniProt database (real API calls)...")
        
        relationships = []
        base_url = "https://rest.uniprot.org/uniprotkb/search"
        
        for gene in gene_list[:3]:  # Limit to avoid rate limits
            try:
                # Search for maize proteins
                query = f'organism_id:4577 AND gene_exact:{gene}'
                params = {
                    'query': query,
                    'format': 'json',
                    'size': 2
                }
                
                response = self.session.get(base_url, params=params, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if 'results' in data and data['results']:
                        for result in data['results']:
                            # Extract protein function
                            if 'comments' in result:
                                for comment in result['comments']:
                                    if comment.get('commentType') == 'FUNCTION':
                                        texts = comment.get('texts', [])
                                        if texts:
                                            function_text = texts[0].get('value', '')
                                            if function_text:
                                                # Truncate long descriptions
                                                short_function = function_text[:80] + "..." if len(function_text) > 80 else function_text
                                                relationships.append({
                                                    "subject": gene,
                                                    "predicate": "has_function",
                                                    "object": short_function
                                                })
                            
                            # Extract GO terms
                            if 'dbReferences' in result:
                                go_count = 0
                                for ref in result['dbReferences']:
                                    if ref.get('type') == 'GO' and go_count < 2:  # Limit GO terms
                                        properties = ref.get('properties', {})
                                        go_term = properties.get('term', '')
                                        if go_term:
                                            relationships.append({
                                                "subject": gene,
                                                "predicate": "has_go_term",
                                                "object": go_term
                                            })
                                            go_count += 1
                
                time.sleep(2)  # Rate limiting for UniProt
                
            except Exception as e:
                print(f"Error querying UniProt for {gene}: {e}")
        
        return relationships
    
    def mine_ensembl_real(self, gene_list: List[str]) -> List[Dict[str, str]]:
        """Mine real data from Ensembl Plants REST API"""
        print("Mining Ensembl Plants database (real API calls)...")
        
        relationships = []
        base_url = "https://rest.ensembl.org"
        
        for gene in gene_list[:3]:  # Limit to avoid rate limits
            try:
                # Try to lookup gene symbol
                lookup_url = f"{base_url}/lookup/symbol/zea_mays/{gene}"
                headers = {'Content-Type': 'application/json'}
                
                response = self.session.get(lookup_url, headers=headers, timeout=15)
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract chromosome location
                    if 'seq_region_name' in data:
                        chromosome = f"Chromosome {data['seq_region_name']}"
                        relationships.append({
                            "subject": gene,
                            "predicate": "located_on",
                            "object": chromosome
                        })
                    
                    # Extract gene biotype
                    if 'biotype' in data:
                        relationships.append({
                            "subject": gene,
                            "predicate": "has_biotype",
                            "object": data['biotype']
                        })
                    
                    # Extract strand information
                    if 'strand' in data:
                        strand = "Plus Strand" if data['strand'] == 1 else "Minus Strand"
                        relationships.append({
                            "subject": gene,
                            "predicate": "on_strand",
                            "object": strand
                        })
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error querying Ensembl for {gene}: {e}")
        
        return relationships
    
    def mine_ebi_expression_atlas(self, gene_list: List[str]) -> List[Dict[str, str]]:
        """Mine gene expression data from EBI Expression Atlas"""
        print("Mining EBI Expression Atlas (real API calls)...")
        
        relationships = []
        base_url = "https://www.ebi.ac.uk/gxa/json/experiments"
        
        try:
            # Get maize experiments
            params = {
                'species': 'zea mays',
                'experimentType': 'baseline'
            }
            
            response = self.session.get(base_url, params=params, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                
                if 'experiments' in data:
                    for exp in data['experiments'][:2]:  # Limit experiments
                        exp_id = exp.get('experimentAccession', '')
                        exp_description = exp.get('experimentDescription', '')
                        
                        if exp_description:
                            # Create experiment-tissue relationships
                            relationships.append({
                                "subject": f"Experiment_{exp_id}",
                                "predicate": "studies",
                                "object": exp_description[:50] + "..." if len(exp_description) > 50 else exp_description
                            })
        
        except Exception as e:
            print(f"Error querying Expression Atlas: {e}")
        
        return relationships
    
    def mine_plantgenie(self) -> List[Dict[str, str]]:
        """Mine data from PlantGenIE (if available)"""
        print("Mining PlantGenIE database...")
        
        relationships = []
        
        # PlantGenIE API example (may require specific endpoints)
        try:
            # This is a placeholder - actual API endpoints may differ
            url = "https://plantgenie.org/api/v1/species/zea_mays/genes"
            
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                # Parse response based on actual API structure
                print("PlantGenIE API response received")
                # Implementation would depend on actual API structure
        
        except Exception as e:
            print(f"PlantGenIE not accessible: {e}")
        
        return relationships

def save_to_csv(relationships: List[Dict[str, str]], filename: str):
    """Save relationships to CSV"""
    if relationships:
        df = pd.DataFrame(relationships)
        df = df.drop_duplicates()
        df.to_csv(filename, index=False)
        print(f"Saved {len(df)} relationships to {filename}")

def main():
    """Main function for real API mining"""
    print("=== Real Database API Mining ===\n")
    print("Note: This requires internet connection and respects API rate limits\n")
    
    miner = RealAPIMiner()
    all_relationships = []
    
    # Gene list for testing
    test_genes = ["DREB2A", "ZmVPP1", "ZmNF-YB2"]
    
    # Mine from different databases
    mining_functions = [
        ("KEGG", lambda: miner.mine_kegg_real()),
        ("UniProt", lambda: miner.mine_uniprot_real(test_genes)),
        ("Ensembl", lambda: miner.mine_ensembl_real(test_genes)),
        ("Expression Atlas", lambda: miner.mine_ebi_expression_atlas(test_genes)),
    ]
    
    for db_name, mining_func in mining_functions:
        print(f"\n--- Mining {db_name} ---")
        try:
            relationships = mining_func()
            print(f"Extracted {len(relationships)} relationships")
            
            if relationships:
                for rel in relationships[:2]:  # Show first 2
                    print(f"  {rel['subject']} --[{rel['predicate']}]--> {rel['object']}")
                if len(relationships) > 2:
                    print(f"  ... and {len(relationships) - 2} more")
            
            all_relationships.extend(relationships)
            
        except Exception as e:
            print(f"Error mining {db_name}: {e}")
        
        print(f"Waiting 3 seconds (rate limiting)...")
        time.sleep(3)
    
    # Save results
    if all_relationships:
        output_file = "toydata/real_api_mined.csv"
        save_to_csv(all_relationships, output_file)
        
        print(f"\n=== Summary ===")
        print(f"Total relationships: {len(all_relationships)}")
        
        # Show relationship types
        predicates = {}
        for rel in all_relationships:
            pred = rel['predicate']
            predicates[pred] = predicates.get(pred, 0) + 1
        
        print("Relationship types:")
        for pred, count in sorted(predicates.items()):
            print(f"  {pred}: {count}")
        
        print(f"\nNext step: python3 expand_maize_kg.py")
    else:
        print("No relationships extracted. Check internet connection and API availability.")

if __name__ == "__main__":
    main()
