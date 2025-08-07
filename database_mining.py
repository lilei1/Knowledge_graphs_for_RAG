#!/usr/bin/env python3
"""
Database Mining for Maize Knowledge Graph

This script demonstrates how to extract data from biological databases
like MaizeGDB, Gramene, KEGG, and others for knowledge graph construction.
"""

import requests
import json
import csv
import time
import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Optional
import pandas as pd

class DatabaseMiner:
    """Class to handle mining from various biological databases"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; KnowledgeGraphMiner/1.0)'
        })
    
    def mine_maizegdb_genes(self) -> List[Dict[str, str]]:
        """
        Mine gene data from MaizeGDB
        Note: This is a demonstration - actual API endpoints may differ
        """
        print("Mining MaizeGDB for gene information...")
        
        # MaizeGDB doesn't have a public REST API, but we can demonstrate
        # the approach using their search functionality
        relationships = []
        
        # Example genes to search for (in practice, you'd get these from their database)
        example_genes = [
            "DREB2A", "ZmVPP1", "ZmNF-YB2", "ZmCCT", "ZmDREB1A", 
            "ZmEREB180", "ZmWRKY33", "ZmMYB31", "ZmHDZ10", "ZmTCP14"
        ]
        
        for gene in example_genes:
            try:
                # Simulate database query (replace with actual API calls)
                gene_info = self._simulate_maizegdb_query(gene)
                if gene_info:
                    relationships.extend(gene_info)
                time.sleep(1)  # Rate limiting
            except Exception as e:
                print(f"Error querying {gene}: {e}")
        
        return relationships
    
    def _simulate_maizegdb_query(self, gene: str) -> List[Dict[str, str]]:
        """Simulate MaizeGDB query - replace with actual API calls"""
        # This simulates what you might extract from MaizeGDB
        gene_data = {
            "DREB2A": [
                {"subject": "DREB2A", "predicate": "located_on", "object": "Chromosome 1"},
                {"subject": "DREB2A", "predicate": "regulates", "object": "Drought Tolerance"},
                {"subject": "DREB2A", "predicate": "has_function", "object": "Transcription Factor Activity"}
            ],
            "ZmVPP1": [
                {"subject": "ZmVPP1", "predicate": "located_on", "object": "Chromosome 1"},
                {"subject": "ZmVPP1", "predicate": "regulates", "object": "ABA Response"},
                {"subject": "ZmVPP1", "predicate": "has_function", "object": "Protein Phosphatase Activity"}
            ]
        }
        return gene_data.get(gene, [])
    
    def mine_gramene_qtls(self) -> List[Dict[str, str]]:
        """
        Mine QTL data from Gramene database
        Gramene has REST APIs for plant comparative genomics
        """
        print("Mining Gramene for QTL information...")
        
        relationships = []
        base_url = "https://data.gramene.org/v60/search"
        
        # Example QTL search (this is a simplified example)
        qtl_traits = ["drought tolerance", "yield", "flowering time", "plant height"]
        
        for trait in qtl_traits:
            try:
                # Construct search query
                params = {
                    'q': f'maize {trait} QTL',
                    'rows': 10,
                    'fl': 'id,name,description,species'
                }
                
                response = self.session.get(base_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    qtl_data = self._parse_gramene_response(data, trait)
                    relationships.extend(qtl_data)
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error querying Gramene for {trait}: {e}")
        
        return relationships
    
    def _parse_gramene_response(self, data: dict, trait: str) -> List[Dict[str, str]]:
        """Parse Gramene API response"""
        relationships = []
        
        # This is a simplified parser - actual implementation would be more complex
        if 'response' in data and 'docs' in data['response']:
            for doc in data['response']['docs'][:5]:  # Limit to 5 results
                if 'name' in doc:
                    qtl_name = doc['name']
                    relationships.append({
                        "subject": trait.title(),
                        "predicate": "associated_with",
                        "object": qtl_name
                    })
        
        return relationships
    
    def mine_kegg_pathways(self) -> List[Dict[str, str]]:
        """
        Mine pathway data from KEGG database
        KEGG has REST APIs for pathway information
        """
        print("Mining KEGG for pathway information...")
        
        relationships = []
        
        # KEGG REST API endpoints
        kegg_base = "http://rest.kegg.jp"
        
        # Get maize organism code
        org_code = "zma"  # Zea mays
        
        try:
            # Get list of pathways for maize
            pathway_url = f"{kegg_base}/list/pathway/{org_code}"
            response = self.session.get(pathway_url, timeout=10)
            
            if response.status_code == 200:
                pathways = self._parse_kegg_pathways(response.text)
                relationships.extend(pathways)
            
        except Exception as e:
            print(f"Error querying KEGG: {e}")
        
        return relationships
    
    def _parse_kegg_pathways(self, pathway_data: str) -> List[Dict[str, str]]:
        """Parse KEGG pathway data"""
        relationships = []
        
        for line in pathway_data.strip().split('\n'):
            if line:
                parts = line.split('\t')
                if len(parts) >= 2:
                    pathway_id = parts[0]
                    pathway_name = parts[1]
                    
                    # Extract pathway category
                    if "metabolism" in pathway_name.lower():
                        category = "Metabolic Pathway"
                    elif "signaling" in pathway_name.lower():
                        category = "Signaling Pathway"
                    elif "biosynthesis" in pathway_name.lower():
                        category = "Biosynthesis Pathway"
                    else:
                        category = "Biological Pathway"
                    
                    relationships.append({
                        "subject": pathway_name,
                        "predicate": "is_a",
                        "object": category
                    })
        
        return relationships[:10]  # Limit results
    
    def mine_uniprot_proteins(self, gene_list: List[str]) -> List[Dict[str, str]]:
        """
        Mine protein function data from UniProt
        UniProt has excellent REST APIs
        """
        print("Mining UniProt for protein function information...")
        
        relationships = []
        base_url = "https://rest.uniprot.org/uniprotkb/search"
        
        for gene in gene_list:
            try:
                # Search for maize proteins
                params = {
                    'query': f'organism_id:4577 AND gene:{gene}',  # 4577 = Zea mays
                    'format': 'json',
                    'size': 5
                }
                
                response = self.session.get(base_url, params=params, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    protein_data = self._parse_uniprot_response(data, gene)
                    relationships.extend(protein_data)
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error querying UniProt for {gene}: {e}")
        
        return relationships
    
    def _parse_uniprot_response(self, data: dict, gene: str) -> List[Dict[str, str]]:
        """Parse UniProt API response"""
        relationships = []
        
        if 'results' in data:
            for result in data['results']:
                # Extract protein function
                if 'comments' in result:
                    for comment in result['comments']:
                        if comment.get('commentType') == 'FUNCTION':
                            function_text = comment.get('texts', [{}])[0].get('value', '')
                            if function_text:
                                relationships.append({
                                    "subject": gene,
                                    "predicate": "has_function",
                                    "object": function_text[:100] + "..." if len(function_text) > 100 else function_text
                                })
                
                # Extract GO terms
                if 'dbReferences' in result:
                    for ref in result['dbReferences']:
                        if ref.get('type') == 'GO':
                            go_term = ref.get('properties', {}).get('term', '')
                            if go_term and any(keyword in go_term.lower() for keyword in ['binding', 'activity', 'process']):
                                relationships.append({
                                    "subject": gene,
                                    "predicate": "has_go_term",
                                    "object": go_term
                                })
        
        return relationships
    
    def mine_ensembl_plants(self, gene_list: List[str]) -> List[Dict[str, str]]:
        """
        Mine genomic data from Ensembl Plants
        Ensembl has comprehensive REST APIs
        """
        print("Mining Ensembl Plants for genomic information...")
        
        relationships = []
        base_url = "https://rest.ensembl.org"
        
        for gene in gene_list[:5]:  # Limit to avoid rate limits
            try:
                # Search for gene information
                search_url = f"{base_url}/lookup/symbol/zea_mays/{gene}"
                headers = {'Content-Type': 'application/json'}
                
                response = self.session.get(search_url, headers=headers, timeout=10)
                if response.status_code == 200:
                    data = response.json()
                    genomic_data = self._parse_ensembl_response(data, gene)
                    relationships.extend(genomic_data)
                
                time.sleep(1)  # Rate limiting
                
            except Exception as e:
                print(f"Error querying Ensembl for {gene}: {e}")
        
        return relationships
    
    def _parse_ensembl_response(self, data: dict, gene: str) -> List[Dict[str, str]]:
        """Parse Ensembl API response"""
        relationships = []
        
        if 'seq_region_name' in data:
            chromosome = f"Chromosome {data['seq_region_name']}"
            relationships.append({
                "subject": gene,
                "predicate": "located_on",
                "object": chromosome
            })
        
        if 'biotype' in data:
            relationships.append({
                "subject": gene,
                "predicate": "has_biotype",
                "object": data['biotype']
            })
        
        return relationships

def save_relationships_to_csv(relationships: List[Dict[str, str]], filename: str):
    """Save extracted relationships to CSV file"""
    if relationships:
        df = pd.DataFrame(relationships)
        # Remove duplicates
        df = df.drop_duplicates()
        df.to_csv(filename, index=False)
        print(f"Saved {len(df)} unique relationships to {filename}")
    else:
        print("No relationships to save")

def main():
    """Main function to demonstrate database mining"""
    print("=== Database Mining for Maize Knowledge Graph ===\n")
    
    miner = DatabaseMiner()
    all_relationships = []
    
    # Mine from different databases
    databases = [
        ("MaizeGDB", miner.mine_maizegdb_genes),
        ("Gramene", miner.mine_gramene_qtls),
        ("KEGG", miner.mine_kegg_pathways),
    ]
    
    # Example gene list for protein databases
    gene_list = ["DREB2A", "ZmVPP1", "ZmNF-YB2", "ZmCCT", "ZmDREB1A"]
    
    for db_name, mining_function in databases:
        print(f"\n--- Mining {db_name} ---")
        try:
            if db_name in ["UniProt", "Ensembl"]:
                relationships = mining_function(gene_list)
            else:
                relationships = mining_function()
            
            print(f"Extracted {len(relationships)} relationships from {db_name}")
            if relationships:
                for rel in relationships[:3]:  # Show first 3
                    print(f"  {rel['subject']} --[{rel['predicate']}]--> {rel['object']}")
                if len(relationships) > 3:
                    print(f"  ... and {len(relationships) - 3} more")
            
            all_relationships.extend(relationships)
            
        except Exception as e:
            print(f"Error mining {db_name}: {e}")
    
    # Save all relationships
    if all_relationships:
        output_file = "toydata/database_mined.csv"
        save_relationships_to_csv(all_relationships, output_file)
        
        print(f"\n=== Summary ===")
        print(f"Total relationships extracted: {len(all_relationships)}")
        print(f"Saved to: {output_file}")
        
        # Show statistics
        predicates = {}
        for rel in all_relationships:
            pred = rel['predicate']
            predicates[pred] = predicates.get(pred, 0) + 1
        
        print(f"\nRelationship types:")
        for pred, count in sorted(predicates.items()):
            print(f"  {pred}: {count}")
    
    print(f"\n=== Database Mining Guide ===")
    print("1. MaizeGDB: Curated maize genetics data (web scraping needed)")
    print("2. Gramene: Plant comparative genomics (REST API available)")
    print("3. KEGG: Pathway information (REST API available)")
    print("4. UniProt: Protein function data (REST API available)")
    print("5. Ensembl Plants: Genomic annotations (REST API available)")
    print("\nNext: Run 'python3 expand_maize_kg.py' to add database_mined.csv to your graph")

if __name__ == "__main__":
    main()
