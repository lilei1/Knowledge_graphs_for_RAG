#!/usr/bin/env python3
"""
Test Script for Production Knowledge Graph System

This script provides comprehensive testing for the production system
with sample data and validation.
"""

import os
import sys
import logging
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Add current directory to path for imports
sys.path.append('.')

# Import production modules
try:
    from production_kg_system import ProductionKGSystem
    from vcf_integration import VCFProcessor
    from phenotype_normalization import PhenotypeProcessor
    from environmental_integration import EnvironmentalIntegrator
    from neo4j import GraphDatabase
except ImportError as e:
    print(f"Error importing production modules: {e}")
    print("Make sure you have installed the production requirements:")
    print("pip install -r requirements_production.txt")
    sys.exit(1)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class ProductionSystemTester:
    """Test suite for the production knowledge graph system"""
    
    def __init__(self, config_file: str = "test_data/test_config.yaml"):
        self.config_file = config_file
        self.test_results = {}
        
    def run_all_tests(self):
        """Run comprehensive test suite"""
        logger.info("🧪 Starting Production Knowledge Graph System Tests")
        
        tests = [
            ("Database Connection", self.test_database_connection),
            ("VCF Processing", self.test_vcf_processing),
            ("Phenotype Processing", self.test_phenotype_processing),
            ("Environmental Integration", self.test_environmental_integration),
            ("Full Pipeline", self.test_full_pipeline),
            ("System Status", self.test_system_status)
        ]
        
        for test_name, test_func in tests:
            logger.info(f"\n{'='*50}")
            logger.info(f"🔬 Running Test: {test_name}")
            logger.info(f"{'='*50}")
            
            try:
                result = test_func()
                self.test_results[test_name] = {
                    'status': 'PASSED',
                    'result': result,
                    'timestamp': datetime.now().isoformat()
                }
                logger.info(f"✅ {test_name}: PASSED")
                
            except Exception as e:
                self.test_results[test_name] = {
                    'status': 'FAILED',
                    'error': str(e),
                    'timestamp': datetime.now().isoformat()
                }
                logger.error(f"❌ {test_name}: FAILED - {e}")
        
        self.generate_test_report()
    
    def test_database_connection(self):
        """Test Neo4j database connection"""
        logger.info("Testing database connection...")
        
        # Initialize system
        kg_system = ProductionKGSystem(config_file=self.config_file)
        kg_system.initialize_database()
        
        # Test connection
        with kg_system.neo4j_driver.session() as session:
            result = session.run("RETURN 'Connection successful' as message")
            message = result.single()['message']
        
        kg_system.neo4j_driver.close()
        return {'message': message}
    
    def test_vcf_processing(self):
        """Test VCF file processing"""
        logger.info("Testing VCF processing...")
        
        # Check if test VCF exists
        vcf_file = "test_data/sample_vcf.vcf"
        if not os.path.exists(vcf_file):
            raise FileNotFoundError(f"Test VCF file not found: {vcf_file}")
        
        # Initialize system
        kg_system = ProductionKGSystem(config_file=self.config_file)
        kg_system.initialize_database()
        kg_system.initialize_components()
        
        # Process VCF
        stats = kg_system.process_vcf_data("test_data/")
        
        kg_system.neo4j_driver.close()
        return stats
    
    def test_phenotype_processing(self):
        """Test phenotype data processing"""
        logger.info("Testing phenotype processing...")
        
        # Check test files
        wide_file = "test_data/sample_phenotypes_wide.csv"
        long_file = "test_data/sample_phenotypes_long.csv"
        
        if not os.path.exists(wide_file) or not os.path.exists(long_file):
            raise FileNotFoundError("Test phenotype files not found")
        
        # Initialize system
        kg_system = ProductionKGSystem(config_file=self.config_file)
        kg_system.initialize_database()
        kg_system.initialize_components()
        
        # Process phenotypes
        stats = kg_system.process_phenotype_data("test_data/")
        
        kg_system.neo4j_driver.close()
        return stats
    
    def test_environmental_integration(self):
        """Test environmental data integration"""
        logger.info("Testing environmental integration...")
        
        # Initialize system
        kg_system = ProductionKGSystem(config_file=self.config_file)
        kg_system.initialize_database()
        kg_system.initialize_components()
        
        # Process environmental data
        stats = kg_system.process_environmental_data("test_data/")
        
        kg_system.neo4j_driver.close()
        return stats
    
    def test_full_pipeline(self):
        """Test complete production pipeline"""
        logger.info("Testing full production pipeline...")
        
        # Run full pipeline
        kg_system = ProductionKGSystem(config_file=self.config_file)
        results = kg_system.run_full_pipeline()
        
        return results
    
    def test_system_status(self):
        """Test system status reporting"""
        logger.info("Testing system status...")
        
        # Initialize system
        kg_system = ProductionKGSystem(config_file=self.config_file)
        kg_system.initialize_database()
        
        # Get status
        status = kg_system.get_system_status()
        
        kg_system.neo4j_driver.close()
        return status
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("\n" + "="*60)
        logger.info("📊 TEST REPORT SUMMARY")
        logger.info("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for r in self.test_results.values() if r['status'] == 'PASSED')
        failed_tests = total_tests - passed_tests
        
        logger.info(f"Total Tests: {total_tests}")
        logger.info(f"Passed: {passed_tests} ✅")
        logger.info(f"Failed: {failed_tests} ❌")
        logger.info(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        # Detailed results
        logger.info("\n📋 DETAILED RESULTS:")
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result['status'] == 'PASSED' else "❌"
            logger.info(f"{status_icon} {test_name}: {result['status']}")
            
            if result['status'] == 'FAILED':
                logger.info(f"   Error: {result['error']}")
        
        # Save report to file
        report_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"\n📄 Full report saved to: {report_file}")
        
        if failed_tests == 0:
            logger.info("\n🎉 ALL TESTS PASSED! Production system is ready to use.")
        else:
            logger.info(f"\n⚠️  {failed_tests} test(s) failed. Please check the errors above.")

def create_test_data():
    """Create additional test data if needed"""
    logger.info("Creating additional test data...")
    
    # Create test directory
    os.makedirs("test_data", exist_ok=True)
    
    # Create a simple gene-trait CSV for learning version compatibility
    gene_trait_data = [
        {"subject": "DREB2A", "predicate": "regulates", "object": "Drought Tolerance"},
        {"subject": "ZmNAC111", "predicate": "regulates", "object": "Root Depth"},
        {"subject": "PSY1", "predicate": "regulates", "object": "Kernel Color"},
        {"subject": "ZmCCT", "predicate": "regulates", "object": "Flowering Time"},
        {"subject": "ZmDREB1A", "predicate": "regulates", "object": "Cold Tolerance"},
        {"subject": "B73", "predicate": "has_trait", "object": "Drought Tolerance"},
        {"subject": "Mo17", "predicate": "has_trait", "object": "High Yield"},
        {"subject": "W22", "predicate": "has_trait", "object": "Disease Resistance"},
    ]
    
    df = pd.DataFrame(gene_trait_data)
    df.to_csv("test_data/test_gene_traits.csv", index=False)
    
    logger.info("✅ Test data created successfully")

def main():
    """Main test execution"""
    print("🧬 Production Knowledge Graph System - Test Suite")
    print("="*60)
    
    # Create test data
    create_test_data()
    
    # Run tests
    tester = ProductionSystemTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
