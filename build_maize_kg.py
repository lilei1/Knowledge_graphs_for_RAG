#!/usr/bin/env python3
"""
Build Knowledge Graph for Maize Toy Data using Neo4j

This script reads the maize.csv file and creates a knowledge graph in Neo4j
with proper node labels and relationships for genetic data.
"""

import pandas as pd
import os
try:
    from dotenv import load_dotenv
    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False
    print("Note: python-dotenv not installed. Using default Neo4j settings.")
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
    if DOTENV_AVAILABLE:
        load_dotenv('.env', override=True)

    # Get Neo4j credentials from environment
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password')
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

def clear_existing_data(kg):
    """Clear existing maize data from the graph"""
    print("Clearing existing maize data...")

    # Delete all nodes and relationships (be careful with this in production!)
    cypher = """
    MATCH (n)
    WHERE n:Gene OR n:Trait OR n:Genotype OR n:QTL OR n:Chromosome OR
          n:Trial OR n:Location OR n:Weather
    DETACH DELETE n
    """
    kg.query(cypher)
    print("Existing data cleared.")

def determine_node_type(entity_name):
    """Determine the appropriate node label based on entity name patterns"""
    entity_lower = entity_name.lower()
    
    # Gene patterns
    if any(gene in entity_name for gene in ['DREB2A', 'ZmNAC111', 'PSY1']):
        return 'Gene'
    
    # Trait patterns
    elif any(trait in entity_lower for trait in ['tolerance', 'yield', 'depth', 'color', 'roots']):
        return 'Trait'
    
    # Genotype patterns (typically alphanumeric codes)
    elif entity_name in ['B73', 'Mo17', 'CML247']:
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
    
    # Location patterns
    elif entity_name in ['Ames']:
        return 'Location'
    
    # Weather patterns
    elif entity_name in ['Drought']:
        return 'Weather'
    
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

def load_and_process_data(kg, csv_file='toydata/maize.csv'):
    """Load CSV data and create knowledge graph"""
    print(f"Loading data from {csv_file}...")
    
    # Read the CSV file
    df = pd.read_csv(csv_file)
    print(f"Loaded {len(df)} relationships from CSV")
    
    # First pass: create all nodes
    print("Creating nodes...")
    entities = set()
    entity_types = {}
    
    for _, row in df.iterrows():
        subject = row['subject']
        object_entity = row['object']
        
        entities.add(subject)
        entities.add(object_entity)
    
    # Determine node types for all entities
    for entity in entities:
        node_type = determine_node_type(entity)
        entity_types[entity] = node_type
        create_node(kg, entity, node_type)
    
    print(f"Created {len(entities)} nodes")
    
    # Second pass: create relationships
    print("Creating relationships...")
    for _, row in df.iterrows():
        subject = row['subject']
        predicate = row['predicate']
        object_entity = row['object']
        
        subject_type = entity_types[subject]
        object_type = entity_types[object_entity]
        
        create_relationship(kg, subject, predicate, object_entity, subject_type, object_type)
    
    print(f"Created {len(df)} relationships")

def add_constraints_and_indexes(kg):
    """Add constraints and indexes for better performance"""
    print("Adding constraints and indexes...")
    
    node_types = ['Gene', 'Trait', 'Genotype', 'QTL', 'Chromosome', 'Trial', 'Location', 'Weather']
    
    for node_type in node_types:
        try:
            # Create uniqueness constraint on name property
            cypher = f"CREATE CONSTRAINT {node_type.lower()}_name_unique IF NOT EXISTS FOR (n:{node_type}) REQUIRE n.name IS UNIQUE"
            kg.query(cypher)
            
            # Create index on name property
            cypher = f"CREATE INDEX {node_type.lower()}_name_index IF NOT EXISTS FOR (n:{node_type}) ON (n.name)"
            kg.query(cypher)
        except Exception as e:
            print(f"Note: Constraint/index for {node_type} may already exist: {e}")

def verify_graph(kg):
    """Verify the created graph by running some queries"""
    print("\n=== Graph Verification ===")
    
    # Count total nodes
    result = kg.query("MATCH (n) RETURN count(n) as total_nodes")
    print(f"Total nodes: {result[0]['total_nodes']}")
    
    # Count nodes by type
    node_types = ['Gene', 'Trait', 'Genotype', 'QTL', 'Chromosome', 'Trial', 'Location', 'Weather']
    for node_type in node_types:
        result = kg.query(f"MATCH (n:{node_type}) RETURN count(n) as count")
        count = result[0]['count'] if result else 0
        if count > 0:
            print(f"{node_type} nodes: {count}")
    
    # Count total relationships
    result = kg.query("MATCH ()-[r]->() RETURN count(r) as total_relationships")
    print(f"Total relationships: {result[0]['total_relationships']}")
    
    # Show some example queries
    print("\n=== Example Queries ===")
    
    # Find all genes and what they regulate
    print("Genes and their regulated traits:")
    result = kg.query("""
        MATCH (g:Gene)-[:REGULATES]->(t:Trait)
        RETURN g.name as gene, t.name as trait
    """)
    for row in result:
        print(f"  {row['gene']} regulates {row['trait']}")
    
    # Find genotypes and their traits
    print("\nGenotypes and their traits:")
    result = kg.query("""
        MATCH (gt:Genotype)-[:HAS_TRAIT]->(t:Trait)
        RETURN gt.name as genotype, t.name as trait
    """)
    for row in result:
        print(f"  {row['genotype']} has trait {row['trait']}")

def main():
    """Main function to build the knowledge graph"""
    print("=== Building Maize Knowledge Graph ===")

    kg = None
    try:
        # Setup Neo4j connection
        kg = setup_neo4j_connection()

        # Clear existing data (optional - comment out if you want to keep existing data)
        clear_existing_data(kg)

        # Load and process the CSV data
        load_and_process_data(kg)

        # Add constraints and indexes
        add_constraints_and_indexes(kg)

        # Verify the graph
        verify_graph(kg)

        print("\n=== Knowledge Graph Successfully Built! ===")
        print("You can now query the graph using Cypher queries in Neo4j Browser or through the notebooks.")

    except Exception as e:
        print(f"Error building knowledge graph: {e}")
        print("Make sure Neo4j is running and your .env file contains the correct credentials.")
    finally:
        if kg:
            kg.close()

if __name__ == "__main__":
    main()
