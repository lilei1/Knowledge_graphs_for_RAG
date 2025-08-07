#!/usr/bin/env python3
"""
Test Neo4j connection
"""

import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

def test_connection():
    load_dotenv('.env', override=True)
    
    NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://localhost:7687')
    NEO4J_USERNAME = os.getenv('NEO4J_USERNAME', 'neo4j')
    NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'maizepassword')
    NEO4J_DATABASE = os.getenv('NEO4J_DATABASE', 'neo4j')
    
    print(f"Testing connection to: {NEO4J_URI}")
    print(f"Username: {NEO4J_USERNAME}")
    print(f"Password: {'*' * len(NEO4J_PASSWORD)}")
    print(f"Database: {NEO4J_DATABASE}")
    
    try:
        # Try without authentication first
        driver = GraphDatabase.driver(NEO4J_URI)

        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            record = result.single()
            print(f"✅ Connection successful! Test result: {record['test']}")

        driver.close()
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")

if __name__ == "__main__":
    test_connection()
