#!/usr/bin/env python3
"""
Simple Prediction Script for Knowledge Graph

Quick predictions for common use cases:
1. Find genes for a trait
2. Find traits for a gene
3. Predict genotype performance
4. Find candidate genes
"""

import os
from neo4j import GraphDatabase
from dotenv import load_dotenv

def connect_to_neo4j():
    """Connect to Neo4j database"""
    load_dotenv('.env', override=True)
    
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'maize123')
    
    return GraphDatabase.driver(
        NEO4J_URI, 
        auth=(NEO4J_USERNAME, NEO4J_PASSWORD)
    )

def find_genes_for_trait(driver, trait_name):
    """Find genes associated with a specific trait"""
    print(f"\n🔍 Finding genes for trait: {trait_name}")
    print("-" * 40)
    
    with driver.session() as session:
        # Direct gene-trait relationships
        query = """
        MATCH (g:Gene)-[:REGULATES]->(t:Trait {name: $trait_name})
        RETURN g.name as gene, 'Direct regulation' as relationship
        """
        result = session.run(query, trait_name=trait_name)
        
        genes = []
        for record in result:
            genes.append((record['gene'], record['relationship']))
        
        # Genes through pathways
        query = """
        MATCH (g:Gene)-[:PARTICIPATES_IN]->(p:Pathway)-[:REGULATES]->(t:Trait {name: $trait_name})
        RETURN g.name as gene, 'Pathway participation' as relationship
        """
        result = session.run(query, trait_name=trait_name)
        
        for record in result:
            genes.append((record['gene'], record['relationship']))
        
        if genes:
            print("Found genes:")
            for gene, rel in genes:
                print(f"  • {gene} ({rel})")
        else:
            print("No genes found for this trait")
        
        return genes

def find_traits_for_gene(driver, gene_name):
    """Find traits associated with a specific gene"""
    print(f"\n🔍 Finding traits for gene: {gene_name}")
    print("-" * 40)
    
    with driver.session() as session:
        # Direct gene-trait relationships
        query = """
        MATCH (g:Gene {name: $gene_name})-[:REGULATES]->(t:Trait)
        RETURN t.name as trait, 'Direct regulation' as relationship
        """
        result = session.run(query, gene_name=gene_name)
        
        traits = []
        for record in result:
            traits.append((record['trait'], record['relationship']))
        
        # Traits through pathways
        query = """
        MATCH (g:Gene {name: $gene_name})-[:PARTICIPATES_IN]->(p:Pathway)-[:REGULATES]->(t:Trait)
        RETURN t.name as trait, 'Pathway regulation' as relationship
        """
        result = session.run(query, gene_name=gene_name)
        
        for record in result:
            traits.append((record['trait'], record['relationship']))
        
        if traits:
            print("Found traits:")
            for trait, rel in traits:
                print(f"  • {trait} ({rel})")
        else:
            print("No traits found for this gene")
        
        return traits

def predict_genotype_performance(driver, genotype_name):
    """Predict performance of a genotype based on its traits"""
    print(f"\n🌾 Predicting performance for genotype: {genotype_name}")
    print("-" * 40)
    
    with driver.session() as session:
        # Get genotype traits and trial data
        query = """
        MATCH (g:Genotype {name: $genotype_name})
        OPTIONAL MATCH (g)-[:HAS_TRAIT]->(t:Trait)
        OPTIONAL MATCH (g)-[:TESTED_IN]->(tr:Trial)-[:CONDUCTED_IN]->(l:Location)
        OPTIONAL MATCH (l)-[:HAS_WEATHER]->(w:Weather)
        RETURN collect(DISTINCT t.name) as traits,
               collect(DISTINCT l.name) as locations,
               collect(DISTINCT w.name) as weather
        """
        result = session.run(query, genotype_name=genotype_name)
        record = result.single()
        
        if record:
            traits = record['traits'] if record['traits'] else []
            locations = record['locations'] if record['locations'] else []
            weather = record['weather'] if record['weather'] else []
            
            print(f"Traits: {', '.join(traits) if traits else 'None'}")
            print(f"Tested locations: {', '.join(locations) if locations else 'None'}")
            print(f"Weather conditions: {', '.join(weather) if weather else 'None'}")
            
            # Simple performance prediction based on traits
            if traits:
                print(f"\n🎯 Performance predictions:")
                if "Drought Tolerance" in traits:
                    print("  • Drought conditions: HIGH performance")
                else:
                    print("  • Drought conditions: MEDIUM performance")
                
                if "Cold Tolerance" in traits:
                    print("  • Cold conditions: HIGH performance")
                else:
                    print("  • Cold conditions: MEDIUM performance")
                
                if "High Yield" in traits:
                    print("  • General yield: HIGH potential")
                else:
                    print("  • General yield: MEDIUM potential")
        else:
            print(f"Genotype '{genotype_name}' not found")

def find_candidate_genes(driver, trait_name):
    """Find candidate genes for a trait based on QTL and pathway analysis"""
    print(f"\n🧬 Finding candidate genes for trait: {trait_name}")
    print("-" * 40)
    
    with driver.session() as session:
        # Find QTLs for the trait
        query = """
        MATCH (t:Trait {name: $trait_name})-[:ASSOCIATED_WITH]->(q:QTL)
        RETURN q.name as qtl, q.chromosome as chromosome
        """
        result = session.run(query, trait_name=trait_name)
        
        qtls = [(record['qtl'], record['chromosome']) for record in result]
        
        if qtls:
            print("Associated QTLs:")
            for qtl, chrom in qtls:
                print(f"  • {qtl} on chromosome {chrom}")
            
            # Find genes on the same chromosomes
            print(f"\n🎯 Candidate genes on same chromosomes:")
            for qtl, chrom in qtls:
                if chrom:
                    query = """
                    MATCH (g:Gene)-[:LOCATED_ON]->(c:Chromosome {name: $chromosome})
                    RETURN collect(DISTINCT g.name) as genes
                    """
                    result = session.run(query, chromosome=chrom)
                    record = result.single()
                    if record and record['genes']:
                        print(f"  Chromosome {chrom}: {', '.join(record['genes'])}")
        else:
            print("No QTLs found for this trait")
            
            # Try to find genes through pathways
            print(f"\n🔍 Searching through biological pathways:")
            query = """
            MATCH (g:Gene)-[:PARTICIPATES_IN]->(p:Pathway)-[:REGULATES]->(t:Trait {name: $trait_name})
            RETURN collect(DISTINCT g.name) as genes
            """
            result = session.run(query, trait_name=trait_name)
            record = result.single()
            if record and record['genes']:
                print(f"Pathway-related genes: {', '.join(record['genes'])}")
            else:
                print("No pathway-related genes found")

def show_available_data(driver):
    """Show what data is available for predictions"""
    print("\n📊 Available Data for Predictions")
    print("-" * 40)
    
    with driver.session() as session:
        # Count nodes by type
        query = """
        MATCH (n) RETURN labels(n) as type, count(n) as count
        ORDER BY count DESC
        """
        result = session.run(query)
        
        print("Node types and counts:")
        for record in result:
            node_type = record['type'][0] if record['type'] else 'Unknown'
            print(f"  • {node_type}: {record['count']}")
        
        # Count relationships by type
        query = """
        MATCH ()-[r]->() RETURN type(r) as rel_type, count(r) as count
        ORDER BY count DESC
        LIMIT 10
        """
        result = session.run(query)
        
        print(f"\nTop relationship types:")
        for record in result:
            print(f"  • {record['rel_type']}: {record['count']}")

def main():
    """Main prediction interface"""
    print("🧬 Knowledge Graph Prediction Interface")
    print("=" * 50)
    
    driver = connect_to_neo4j()
    
    try:
        while True:
            print("\n" + "="*50)
            print("Choose a prediction type:")
            print("1. Find genes for a trait")
            print("2. Find traits for a gene")
            print("3. Predict genotype performance")
            print("4. Find candidate genes")
            print("5. Show available data")
            print("6. Exit")
            print("="*50)
            
            choice = input("Enter your choice (1-6): ").strip()
            
            if choice == "1":
                trait = input("Enter trait name (e.g., 'Drought Tolerance'): ").strip()
                if trait:
                    find_genes_for_trait(driver, trait)
            
            elif choice == "2":
                gene = input("Enter gene name (e.g., 'DREB2A'): ").strip()
                if gene:
                    find_traits_for_gene(driver, gene)
            
            elif choice == "3":
                genotype = input("Enter genotype name (e.g., 'B73'): ").strip()
                if genotype:
                    predict_genotype_performance(driver, genotype)
            
            elif choice == "4":
                trait = input("Enter trait name (e.g., 'Drought Tolerance'): ").strip()
                if trait:
                    find_candidate_genes(driver, trait)
            
            elif choice == "5":
                show_available_data(driver)
            
            elif choice == "6":
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please enter 1-6.")
            
            input("\nPress Enter to continue...")
    
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        driver.close()

if __name__ == "__main__":
    main()
