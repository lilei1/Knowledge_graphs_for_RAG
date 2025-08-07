#!/usr/bin/env python3
"""
Expand the Maize Knowledge Graph with Additional Data

This script loads additional CSV files to expand the existing knowledge graph
with more genes, genotypes, traits, QTLs, trials, and molecular data.
"""

import pandas as pd
import os
from dotenv import load_dotenv
from neo4j import GraphDatabase
import warnings
warnings.filterwarnings("ignore")

class Neo4jConnection:
    """Neo4j database connection wrapper"""
    
    def __init__(self, uri, username=None, password=None, database="neo4j"):
        if username and password:
            self.driver = GraphDatabase.driver(uri, auth=(username, password))
        else:
            self.driver = GraphDatabase.driver(uri)
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
    
    # Get Neo4j credentials from environment
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'test123')
    NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    print(f"Connecting to Neo4j at: {NEO4J_URI}")
    
    # Initialize Neo4j connection
    kg = Neo4jConnection(
        uri=NEO4J_URI, 
        username=NEO4J_USERNAME, 
        password=NEO4J_PASSWORD, 
        database=NEO4J_DATABASE
    )
    
    # Test connection
    try:
        result = kg.query("RETURN 1 as test")
        print("Connection successful!")
    except Exception as e:
        print(f"Connection failed: {e}")
        raise
    
    return kg

def determine_node_type(entity_name):
    """Determine the appropriate node label based on entity name patterns"""
    entity_lower = entity_name.lower()
    
    # Gene patterns (expanded)
    if any(pattern in entity_name for pattern in ['DREB', 'Zm', 'PSY', 'VPP', 'NF-Y', 'CCT', 'EREB', 'WRKY', 'MYB', 'HDZ', 'TCP', 'NAC', 'ARF', 'GRF', 'SPL', 'KN', 'GA20ox']):
        return 'Gene'
    
    # Trait patterns (expanded)
    elif any(trait in entity_lower for trait in ['tolerance', 'yield', 'depth', 'color', 'roots', 'flowering', 'resistance', 'production', 'architecture', 'height', 'senescence', 'development', 'size', 'elongation', 'efficiency', 'protein', 'kernel', 'leaves', 'system', 'lodging', 'rainfall', 'stress']):
        return 'Trait'
    
    # Genotype patterns (expanded)
    elif entity_name in ['B73', 'Mo17', 'CML247', 'W22', 'Oh43', 'PH207', 'Ki3', 'A632', 'Tx303', 'NC350', 'F7', 'B37']:
        return 'Genotype'
    
    # QTL patterns
    elif entity_name.startswith('q') and any(char.isdigit() for char in entity_name):
        return 'QTL'
    
    # Chromosome patterns
    elif 'chromosome' in entity_lower:
        return 'Chromosome'
    
    # Trial patterns
    elif 'trial' in entity_lower:
        return 'Trial'
    
    # Location patterns (expanded)
    elif entity_name in ['Ames', 'Iowa', 'Nebraska', 'Illinois', 'Kansas', 'Minnesota']:
        return 'Location'
    
    # Weather patterns (expanded)
    elif any(weather in entity_lower for weather in ['drought', 'normal', 'high', 'cold', 'wind', 'rainfall', 'temperature']):
        return 'Weather'
    
    # Molecular marker patterns
    elif entity_name.startswith('SNP_') or entity_name.startswith('SSR_'):
        return 'Marker'
    
    # Pathway patterns
    elif 'pathway' in entity_lower or 'signaling' in entity_lower or 'biosynthesis' in entity_lower or 'metabolism' in entity_lower or 'response' in entity_lower or 'clock' in entity_lower or 'division' in entity_lower:
        return 'Pathway'
    
    # Default to Entity if no pattern matches
    else:
        return 'Entity'

def create_node(kg, entity_name, node_type):
    """Create a node with appropriate label and properties"""
    cypher = f"""
    MERGE (n:{node_type} {{name: $name}})
    RETURN n
    """
    kg.query(cypher, params={'name': entity_name})

def create_relationship(kg, subject, predicate, object_entity, subject_type, object_type):
    """Create a relationship between two nodes"""
    # Convert predicate to uppercase and replace spaces with underscores
    relationship_type = predicate.upper().replace(' ', '_')
    
    cypher = f"""
    MATCH (s:{subject_type} {{name: $subject}})
    MATCH (o:{object_type} {{name: $object}})
    MERGE (s)-[r:{relationship_type}]->(o)
    RETURN s, r, o
    """
    
    result = kg.query(cypher, params={
        'subject': subject, 
        'object': object_entity
    })
    
    if not result:
        print(f"Warning: Could not create relationship {subject} -{relationship_type}-> {object_entity}")

def load_csv_data(kg, csv_file):
    """Load a single CSV file and add to knowledge graph"""
    print(f"Loading data from {csv_file}...")
    
    # Read the CSV file
    df = pd.read_csv(csv_file)
    print(f"  Found {len(df)} relationships")
    
    # Collect all entities and their types
    entities = set()
    entity_types = {}
    
    for _, row in df.iterrows():
        subject = row['subject']
        object_entity = row['object']
        
        entities.add(subject)
        entities.add(object_entity)
    
    # Determine node types for all entities
    new_nodes = 0
    for entity in entities:
        node_type = determine_node_type(entity)
        entity_types[entity] = node_type
        
        # Check if node already exists
        existing = kg.query(f"MATCH (n:{node_type} {{name: $name}}) RETURN n", params={'name': entity})
        if not existing:
            create_node(kg, entity, node_type)
            new_nodes += 1
    
    print(f"  Created {new_nodes} new nodes")
    
    # Create relationships
    new_relationships = 0
    for _, row in df.iterrows():
        subject = row['subject']
        predicate = row['predicate']
        object_entity = row['object']
        
        subject_type = entity_types[subject]
        object_type = entity_types[object_entity]
        
        create_relationship(kg, subject, predicate, object_entity, subject_type, object_type)
        new_relationships += 1
    
    print(f"  Created {new_relationships} relationships")
    return new_nodes, new_relationships

def get_graph_stats(kg):
    """Get current graph statistics"""
    node_count = kg.query("MATCH (n) RETURN count(n) as count")[0]['count']
    rel_count = kg.query("MATCH ()-[r]->() RETURN count(r) as count")[0]['count']
    return node_count, rel_count

def main():
    """Main function to expand the knowledge graph"""
    print("=== Expanding Maize Knowledge Graph ===")
    
    kg = None
    try:
        # Setup Neo4j connection
        kg = setup_neo4j_connection()
        
        # Get initial stats
        initial_nodes, initial_rels = get_graph_stats(kg)
        print(f"\nInitial graph: {initial_nodes} nodes, {initial_rels} relationships")
        
        # List of additional CSV files to load
        csv_files = [
            'toydata/additional_genes.csv',
            'toydata/genotype_traits.csv', 
            'toydata/qtl_mappings.csv',
            'toydata/field_trials.csv',
            'toydata/molecular_markers.csv',
            'toydata/pathways.csv'
        ]
        
        total_new_nodes = 0
        total_new_rels = 0
        
        # Load each CSV file
        for csv_file in csv_files:
            if os.path.exists(csv_file):
                new_nodes, new_rels = load_csv_data(kg, csv_file)
                total_new_nodes += new_nodes
                total_new_rels += new_rels
            else:
                print(f"Warning: {csv_file} not found, skipping...")
        
        # Get final stats
        final_nodes, final_rels = get_graph_stats(kg)
        
        print(f"\n=== Expansion Complete ===")
        print(f"Added {total_new_nodes} new nodes and {total_new_rels} new relationships")
        print(f"Final graph: {final_nodes} nodes, {final_rels} relationships")
        print(f"Growth: +{final_nodes - initial_nodes} nodes, +{final_rels - initial_rels} relationships")
        
        # Show some example queries with the expanded data
        print(f"\n=== Sample Queries with Expanded Data ===")
        
        # Count nodes by type
        print("\nNode counts by type:")
        node_types = ['Gene', 'Trait', 'Genotype', 'QTL', 'Chromosome', 'Trial', 'Location', 'Weather', 'Marker', 'Pathway']
        for node_type in node_types:
            result = kg.query(f"MATCH (n:{node_type}) RETURN count(n) as count")
            count = result[0]['count'] if result else 0
            if count > 0:
                print(f"  {node_type}: {count}")
        
        # Show pathway information
        print("\nBiological pathways:")
        result = kg.query("""
            MATCH (g:Gene)-[:PARTICIPATES_IN]->(p:Pathway)-[:REGULATES]->(t:Trait)
            RETURN g.name as gene, p.name as pathway, t.name as trait
            LIMIT 5
        """)
        for row in result:
            print(f"  {row['gene']} → {row['pathway']} → {row['trait']}")
        
        print("\nYour expanded knowledge graph is ready for advanced queries and analysis!")
        
    except Exception as e:
        print(f"Error expanding knowledge graph: {e}")
    finally:
        if kg:
            kg.close()

if __name__ == "__main__":
    main()
