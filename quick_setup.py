#!/usr/bin/env python3
"""
Quick Setup Script for Knowledge Graph System

This script helps you get started quickly by installing the necessary packages
and testing your setup.
"""

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print(f"Output: {e.stdout}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ required")
        return False
    
    if version.major == 3 and version.minor >= 13:
        print("⚠️  Python 3.13 detected - some packages may not be available yet")
    
    return True

def install_basic_packages():
    """Install basic packages needed for the system"""
    packages = [
        "pandas",
        "numpy", 
        "python-dotenv",
        "neo4j"
    ]
    
    print(f"\n📦 Installing basic packages: {', '.join(packages)}")
    
    for package in packages:
        success = run_command(f"pip install {package}", f"Installing {package}")
        if not success:
            print(f"⚠️  Failed to install {package}, but continuing...")
    
    return True

def test_imports():
    """Test if required packages can be imported"""
    print("\n🧪 Testing package imports...")
    
    packages_to_test = [
        ("pandas", "pd"),
        ("numpy", "np"),
        ("neo4j", "GraphDatabase"),
        ("dotenv", "load_dotenv")
    ]
    
    success_count = 0
    
    for package, import_name in packages_to_test:
        try:
            if package == "neo4j":
                from neo4j import GraphDatabase
                print(f"✅ {package}: GraphDatabase imported successfully")
            elif package == "dotenv":
                from dotenv import load_dotenv
                print(f"✅ {package}: load_dotenv imported successfully")
            elif package == "pandas":
                import pandas as pd
                print(f"✅ {package}: version {pd.__version__}")
            elif package == "numpy":
                import numpy as np
                print(f"✅ {package}: version {np.__version__}")
            success_count += 1
        except ImportError as e:
            print(f"❌ {package}: Import failed - {e}")
    
    print(f"\n📊 Import test results: {success_count}/{len(packages_to_test)} packages imported successfully")
    return success_count >= 3  # Need at least pandas, numpy, neo4j

def check_neo4j():
    """Check if Neo4j is available"""
    print("\n🗄️  Checking Neo4j availability...")
    
    try:
        from neo4j import GraphDatabase
        
        # Try to connect to default Neo4j instance
        driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
        
        with driver.session() as session:
            result = session.run("RETURN 1 as test")
            test_value = result.single()["test"]
            if test_value == 1:
                print("✅ Neo4j connection successful!")
                driver.close()
                return True
    except Exception as e:
        print(f"❌ Neo4j connection failed: {e}")
        print("\n💡 To start Neo4j with Docker:")
        print("docker run --name neo4j-test -p7474:7474 -p7687:7687 -d \\")
        print("  --env NEO4J_AUTH=neo4j/password neo4j:4.4")
        print("\nThen access Neo4j Browser at: http://localhost:7474")
        return False

def check_test_data():
    """Check if test data files exist"""
    print("\n📁 Checking test data files...")
    
    test_files = [
        "toydata/maize.csv",
        "test_data/sample_vcf.vcf",
        "test_data/sample_phenotypes_wide.csv"
    ]
    
    existing_files = []
    for file_path in test_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
            existing_files.append(file_path)
        else:
            print(f"❌ {file_path} - not found")
    
    if len(existing_files) > 0:
        print(f"📊 Found {len(existing_files)}/{len(test_files)} test data files")
        return True
    else:
        print("⚠️  No test data files found")
        return False

def suggest_next_steps(neo4j_available, test_data_available):
    """Suggest next steps based on what's available"""
    print("\n🎯 NEXT STEPS:")
    print("=" * 50)
    
    if neo4j_available and test_data_available:
        print("🎉 Everything looks good! You can:")
        print("1. Run the original system:")
        print("   python3 build_maize_kg.py")
        print("2. Run simple tests:")
        print("   python test_simple_system.py")
        print("3. Access Neo4j Browser: http://localhost:7474")
    
    elif test_data_available and not neo4j_available:
        print("📊 Test data available, but Neo4j not running.")
        print("1. Start Neo4j first:")
        print("   docker run --name neo4j-test -p7474:7474 -p7687:7687 -d \\")
        print("     --env NEO4J_AUTH=neo4j/password neo4j:4.4")
        print("2. Then run: python3 build_maize_kg.py")
        print("3. Or run data tests: python test_simple_system.py")
    
    elif neo4j_available and not test_data_available:
        print("🗄️  Neo4j available, but missing test data.")
        print("1. The original toydata should work:")
        print("   python3 build_maize_kg.py")
        print("2. Or create test data:")
        print("   python test_simple_system.py")
    
    else:
        print("⚠️  Missing both Neo4j and test data.")
        print("1. Start Neo4j:")
        print("   docker run --name neo4j-test -p7474:7474 -p7687:7687 -d \\")
        print("     --env NEO4J_AUTH=neo4j/password neo4j:4.4")
        print("2. Run basic tests:")
        print("   python test_simple_system.py")

def main():
    """Main setup function"""
    print("🧬 Knowledge Graph System - Quick Setup")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        return
    
    # Install basic packages
    install_basic_packages()
    
    # Test imports
    imports_ok = test_imports()
    if not imports_ok:
        print("\n❌ Critical packages missing. Please install manually:")
        print("pip install pandas numpy python-dotenv neo4j")
        return
    
    # Check Neo4j
    neo4j_ok = check_neo4j()
    
    # Check test data
    test_data_ok = check_test_data()
    
    # Suggest next steps
    suggest_next_steps(neo4j_ok, test_data_ok)
    
    print("\n✨ Setup complete! Happy graph building! 🚀")

if __name__ == "__main__":
    main()
