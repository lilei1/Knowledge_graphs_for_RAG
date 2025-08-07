#!/usr/bin/env python3
"""
Visualize the Maize Knowledge Graph

This script creates a simple visualization of the knowledge graph structure
and generates some basic statistics and reports.
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import pandas as pd
import warnings
warnings.filterwarnings("ignore")

class Neo4jConnection:
    """Neo4j database connection wrapper"""

    def __init__(self, uri, username, password, database="neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database

    def close(self):
        if self.driver:
            self.driver.close()

    def query(self, cypher, params=None):
        """Execute a Cypher query and return results"""
        with self.driver.session(database=self.database) as session:
            result = session.run(cypher, params or {})
            return [record.data() for record in result]

def setup_neo4j_connection():
    """Setup Neo4j connection using environment variables"""
    load_dotenv('.env', override=True)

    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')
    NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'neo4j')

    kg = Neo4jConnection(
        uri=NEO4J_URI,
        username=NEO4J_USERNAME,
        password=NEO4J_PASSWORD,
        database=NEO4J_DATABASE
    )

    return kg

def get_graph_statistics(kg):
    """Get basic statistics about the graph"""
    print("=== Knowledge Graph Statistics ===\n")
    
    # Total nodes and relationships
    result = kg.query("MATCH (n) RETURN count(n) as total_nodes")
    total_nodes = result[0]['total_nodes']
    
    result = kg.query("MATCH ()-[r]->() RETURN count(r) as total_relationships")
    total_relationships = result[0]['total_relationships']
    
    print(f"Total Nodes: {total_nodes}")
    print(f"Total Relationships: {total_relationships}")
    print()
    
    # Node counts by type
    print("Node Counts by Type:")
    node_types = ['Gene', 'Trait', 'Genotype', 'QTL', 'Chromosome', 'Trial', 'Location', 'Weather']
    
    for node_type in node_types:
        result = kg.query(f"MATCH (n:{node_type}) RETURN count(n) as count")
        count = result[0]['count'] if result else 0
        if count > 0:
            print(f"  {node_type}: {count}")
    
    print()
    
    # Relationship counts by type
    print("Relationship Counts by Type:")
    result = kg.query("""
        MATCH ()-[r]->()
        RETURN type(r) as relationship_type, count(r) as count
        ORDER BY count DESC
    """)
    
    for row in result:
        print(f"  {row['relationship_type']}: {row['count']}")
    
    print()

def show_graph_schema(kg):
    """Show the graph schema"""
    print("=== Graph Schema ===\n")
    
    # Get all node labels and their properties
    result = kg.query("""
        CALL db.labels() YIELD label
        RETURN label
        ORDER BY label
    """)
    
    print("Node Labels:")
    for row in result:
        print(f"  - {row['label']}")
    
    print()
    
    # Get all relationship types
    result = kg.query("""
        CALL db.relationshipTypes() YIELD relationshipType
        RETURN relationshipType
        ORDER BY relationshipType
    """)
    
    print("Relationship Types:")
    for row in result:
        print(f"  - {row['relationshipType']}")
    
    print()

def show_sample_data(kg):
    """Show sample data from the graph"""
    print("=== Sample Data ===\n")
    
    # Show all nodes with their labels
    print("All Nodes:")
    result = kg.query("""
        MATCH (n)
        RETURN labels(n) as labels, n.name as name
        ORDER BY labels[0], n.name
    """)
    
    current_label = None
    for row in result:
        label = row['labels'][0] if row['labels'] else 'Unknown'
        if label != current_label:
            print(f"\n{label} nodes:")
            current_label = label
        print(f"  - {row['name']}")
    
    print("\n" + "="*50 + "\n")
    
    # Show all relationships
    print("All Relationships:")
    result = kg.query("""
        MATCH (a)-[r]->(b)
        RETURN a.name as source, type(r) as relationship, b.name as target
        ORDER BY a.name, type(r), b.name
    """)
    
    for row in result:
        print(f"  {row['source']} --[{row['relationship']}]--> {row['target']}")
    
    print()

def generate_pathways_report(kg):
    """Generate a report of biological pathways in the graph"""
    print("=== Biological Pathways Report ===\n")
    
    # Gene regulation pathways
    print("1. Gene Regulation Pathways:")
    result = kg.query("""
        MATCH (g:Gene)-[:REGULATES]->(t:Trait)
        RETURN g.name as gene, t.name as trait
        ORDER BY g.name
    """)
    
    for row in result:
        print(f"   {row['gene']} regulates {row['trait']}")
    
    print()
    
    # Genotype-trait associations
    print("2. Genotype-Trait Associations:")
    result = kg.query("""
        MATCH (gt:Genotype)-[:HAS_TRAIT]->(t:Trait)
        RETURN gt.name as genotype, t.name as trait
        ORDER BY gt.name
    """)
    
    for row in result:
        print(f"   {row['genotype']} has {row['trait']}")
    
    print()
    
    # QTL mappings
    print("3. QTL Mappings:")
    result = kg.query("""
        MATCH (t:Trait)-[:ASSOCIATED_WITH]->(q:QTL)-[:LOCATED_ON]->(c:Chromosome)
        RETURN t.name as trait, q.name as qtl, c.name as chromosome
    """)
    
    for row in result:
        print(f"   {row['trait']} → {row['qtl']} → {row['chromosome']}")
    
    print()
    
    # Complete gene-to-chromosome pathways
    print("4. Complete Gene-to-Chromosome Pathways:")
    result = kg.query("""
        MATCH path = (g:Gene)-[:REGULATES]->(t:Trait)-[:ASSOCIATED_WITH]->(q:QTL)-[:LOCATED_ON]->(c:Chromosome)
        RETURN g.name as gene, t.name as trait, q.name as qtl, c.name as chromosome
    """)
    
    if result:
        for row in result:
            print(f"   {row['gene']} → {row['trait']} → {row['qtl']} → {row['chromosome']}")
    else:
        print("   No complete pathways found")
    
    print()

def generate_experimental_report(kg):
    """Generate a report of experimental data in the graph"""
    print("=== Experimental Data Report ===\n")
    
    # Trial information
    print("1. Field Trials:")
    result = kg.query("""
        MATCH (trial:Trial)-[:CONDUCTED_IN]->(loc:Location)
        OPTIONAL MATCH (gt:Genotype)-[:TESTED_IN]->(trial)
        OPTIONAL MATCH (trial)-[:MEASURED]->(trait:Trait)
        OPTIONAL MATCH (loc)-[:HAS_WEATHER]->(w:Weather)
        RETURN trial.name as trial, loc.name as location, 
               collect(DISTINCT gt.name) as genotypes,
               collect(DISTINCT trait.name) as traits,
               collect(DISTINCT w.name) as weather
    """)
    
    for row in result:
        print(f"   Trial: {row['trial']}")
        print(f"     Location: {row['location']}")
        if row['weather'] and row['weather'][0]:
            print(f"     Weather: {', '.join(row['weather'])}")
        if row['genotypes'] and row['genotypes'][0]:
            print(f"     Genotypes tested: {', '.join(row['genotypes'])}")
        if row['traits'] and row['traits'][0]:
            print(f"     Traits measured: {', '.join(row['traits'])}")
        print()

def export_to_csv(kg):
    """Export graph data to CSV files for further analysis"""
    print("=== Exporting Data ===\n")
    
    # Export nodes
    result = kg.query("""
        MATCH (n)
        RETURN labels(n)[0] as node_type, n.name as name
        ORDER BY labels(n)[0], n.name
    """)
    
    nodes_df = pd.DataFrame(result)
    nodes_df.to_csv('graph_nodes.csv', index=False)
    print(f"Exported {len(nodes_df)} nodes to graph_nodes.csv")
    
    # Export relationships
    result = kg.query("""
        MATCH (a)-[r]->(b)
        RETURN a.name as source, type(r) as relationship, b.name as target
        ORDER BY a.name, type(r), b.name
    """)
    
    relationships_df = pd.DataFrame(result)
    relationships_df.to_csv('graph_relationships.csv', index=False)
    print(f"Exported {len(relationships_df)} relationships to graph_relationships.csv")
    
    print()

def main():
    """Main function to visualize and analyze the knowledge graph"""
    print("=== Maize Knowledge Graph Analysis ===\n")

    kg = None
    try:
        # Setup Neo4j connection
        kg = setup_neo4j_connection()

        # Generate various reports
        get_graph_statistics(kg)
        show_graph_schema(kg)
        show_sample_data(kg)
        generate_pathways_report(kg)
        generate_experimental_report(kg)
        export_to_csv(kg)

        print("=== Analysis Complete ===")
        print("Check the generated CSV files for detailed data export.")
        print("Use Neo4j Browser for interactive visualization at http://localhost:7474")

    except Exception as e:
        print(f"Error analyzing knowledge graph: {e}")
        print("Make sure the knowledge graph has been built and Neo4j is running.")
    finally:
        if kg:
            kg.close()

if __name__ == "__main__":
    main()
