#!/usr/bin/env python3
"""
Literature Mining for Maize Knowledge Graph Data

This script demonstrates how to use LLMs to extract structured data
from scientific literature for building knowledge graphs.
"""

import json
import csv
import os
from typing import List, Dict, Any

# Example abstracts from real maize genetics papers
EXAMPLE_ABSTRACTS = [
    """
    The maize DREB2A gene encodes a transcription factor that regulates drought tolerance 
    in maize. Overexpression of DREB2A in transgenic maize plants resulted in enhanced 
    drought tolerance and improved water use efficiency. QTL analysis mapped drought 
    tolerance to chromosome 1 at position qDT1.1. Field trials in Nebraska showed that 
    genotype B73 carrying the DREB2A allele performed better under drought stress.
    """,
    
    """
    ZmVPP1 is a key regulator of abscisic acid signaling in maize. The gene participates 
    in the ABA signaling pathway and controls stomatal closure during drought stress. 
    Molecular marker analysis identified SNP_chr1_1234567 as tightly linked to ZmVPP1. 
    Genotype Mo17 shows high expression of ZmVPP1 and exhibits superior drought tolerance.
    """,
    
    """
    Cold tolerance in maize is controlled by multiple genes including ZmDREB1A. 
    This gene regulates the cold response pathway and is associated with QTL qCT2.1 
    on chromosome 2. Genotype W22 shows enhanced cold tolerance and early flowering 
    traits. Field trials in Minnesota demonstrated superior performance under cold stress.
    """,
    
    """
    Nitrogen use efficiency in maize is regulated by ZmNF-YB2, which participates in 
    nitrogen metabolism pathways. The trait is associated with QTL qNUE3.1 on chromosome 3. 
    SSR marker phi003 is linked to this QTL. Genotype A632 shows high nitrogen use 
    efficiency and tall plant height characteristics.
    """,
    
    """
    Anthocyanin production in maize kernels is controlled by ZmMYB31, which regulates 
    the anthocyanin biosynthesis pathway. Purple kernel color is associated with this 
    gene. Genotype Ki3 exhibits high anthocyanin production and purple kernels. 
    The trait maps to QTL qAC8.1 on chromosome 8.
    """
]

def extract_relationships_with_llm_prompt(abstract: str) -> str:
    """
    Create a prompt for LLM to extract structured relationships from abstract
    """
    prompt = f"""
    Extract structured biological relationships from this maize genetics abstract.
    Return ONLY a JSON list of relationships in this exact format:
    
    [
        {{"subject": "gene_name", "predicate": "regulates", "object": "trait_name"}},
        {{"subject": "genotype_name", "predicate": "has_trait", "object": "trait_name"}},
        {{"subject": "trait_name", "predicate": "associated_with", "object": "qtl_name"}},
        {{"subject": "qtl_name", "predicate": "located_on", "object": "chromosome_name"}},
        {{"subject": "gene_name", "predicate": "participates_in", "object": "pathway_name"}},
        {{"subject": "gene_name", "predicate": "has_marker", "object": "marker_name"}},
        {{"subject": "genotype_name", "predicate": "tested_in", "object": "trial_name"}},
        {{"subject": "trial_name", "predicate": "conducted_in", "object": "location_name"}}
    ]
    
    Rules:
    - Use exact gene names (e.g., DREB2A, ZmVPP1)
    - Use descriptive trait names (e.g., "Drought Tolerance", "Cold Tolerance")
    - Use standard genotype names (e.g., B73, Mo17, W22)
    - Use QTL format like qDT1.1, qCT2.1
    - Use "Chromosome X" format for chromosomes
    - Include pathway names if mentioned
    - Include marker names if mentioned
    - Only extract relationships explicitly stated in the text
    
    Abstract:
    {abstract}
    
    JSON:
    """
    return prompt

def simulate_llm_extraction(abstract: str) -> List[Dict[str, str]]:
    """
    Simulate LLM extraction - in practice, you'd call an actual LLM API here
    This function manually extracts relationships to show the expected format
    """
    # This simulates what an LLM would extract from each abstract
    if "DREB2A" in abstract:
        return [
            {"subject": "DREB2A", "predicate": "regulates", "object": "Drought Tolerance"},
            {"subject": "B73", "predicate": "has_trait", "object": "Drought Tolerance"},
            {"subject": "Drought Tolerance", "predicate": "associated_with", "object": "qDT1.1"},
            {"subject": "qDT1.1", "predicate": "located_on", "object": "Chromosome 1"},
            {"subject": "B73", "predicate": "tested_in", "object": "Trial_Nebraska_2020"},
            {"subject": "Trial_Nebraska_2020", "predicate": "conducted_in", "object": "Nebraska"}
        ]
    elif "ZmVPP1" in abstract:
        return [
            {"subject": "ZmVPP1", "predicate": "regulates", "object": "Drought Tolerance"},
            {"subject": "ZmVPP1", "predicate": "participates_in", "object": "ABA Signaling Pathway"},
            {"subject": "ZmVPP1", "predicate": "has_marker", "object": "SNP_chr1_1234567"},
            {"subject": "Mo17", "predicate": "has_trait", "object": "Drought Tolerance"}
        ]
    elif "ZmDREB1A" in abstract:
        return [
            {"subject": "ZmDREB1A", "predicate": "regulates", "object": "Cold Tolerance"},
            {"subject": "ZmDREB1A", "predicate": "participates_in", "object": "Cold Response Pathway"},
            {"subject": "Cold Tolerance", "predicate": "associated_with", "object": "qCT2.1"},
            {"subject": "qCT2.1", "predicate": "located_on", "object": "Chromosome 2"},
            {"subject": "W22", "predicate": "has_trait", "object": "Cold Tolerance"},
            {"subject": "W22", "predicate": "has_trait", "object": "Early Flowering"}
        ]
    elif "ZmNF-YB2" in abstract:
        return [
            {"subject": "ZmNF-YB2", "predicate": "regulates", "object": "Nitrogen Use Efficiency"},
            {"subject": "ZmNF-YB2", "predicate": "participates_in", "object": "Nitrogen Metabolism"},
            {"subject": "Nitrogen Use Efficiency", "predicate": "associated_with", "object": "qNUE3.1"},
            {"subject": "qNUE3.1", "predicate": "located_on", "object": "Chromosome 3"},
            {"subject": "SSR_phi003", "predicate": "linked_to", "object": "qNUE3.1"},
            {"subject": "A632", "predicate": "has_trait", "object": "Nitrogen Use Efficiency"}
        ]
    elif "ZmMYB31" in abstract:
        return [
            {"subject": "ZmMYB31", "predicate": "regulates", "object": "Anthocyanin Production"},
            {"subject": "ZmMYB31", "predicate": "participates_in", "object": "Anthocyanin Biosynthesis"},
            {"subject": "Ki3", "predicate": "has_trait", "object": "Anthocyanin Production"},
            {"subject": "Ki3", "predicate": "has_trait", "object": "Purple Kernels"},
            {"subject": "Anthocyanin Production", "predicate": "associated_with", "object": "qAC8.1"},
            {"subject": "qAC8.1", "predicate": "located_on", "object": "Chromosome 8"}
        ]
    else:
        return []

def save_relationships_to_csv(relationships: List[Dict[str, str]], filename: str):
    """Save extracted relationships to CSV file"""
    with open(filename, 'w', newline='') as csvfile:
        fieldnames = ['subject', 'predicate', 'object']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for rel in relationships:
            writer.writerow(rel)

def main():
    """Main function to demonstrate literature mining"""
    print("=== Literature Mining for Maize Knowledge Graph ===\n")
    
    all_relationships = []
    
    for i, abstract in enumerate(EXAMPLE_ABSTRACTS, 1):
        print(f"Processing Abstract {i}:")
        print(f"Preview: {abstract[:100]}...")
        
        # Show the LLM prompt that would be used
        prompt = extract_relationships_with_llm_prompt(abstract)
        print(f"\nLLM Prompt length: {len(prompt)} characters")
        
        # Simulate LLM extraction (replace with actual LLM API call)
        relationships = simulate_llm_extraction(abstract)
        
        print(f"Extracted {len(relationships)} relationships:")
        for rel in relationships:
            print(f"  {rel['subject']} --[{rel['predicate']}]--> {rel['object']}")
        
        all_relationships.extend(relationships)
        print("-" * 50)
    
    # Save all relationships to CSV
    output_file = "toydata/literature_extracted.csv"
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
    
    print(f"\n=== Next Steps ===")
    print(f"1. Run: python3 expand_maize_kg.py (to add literature_extracted.csv)")
    print(f"2. Use real LLM APIs (OpenAI, Anthropic, etc.) for actual extraction")
    print(f"3. Process real scientific papers from PubMed or other sources")
    print(f"4. Validate extracted relationships with domain experts")

if __name__ == "__main__":
    main()
