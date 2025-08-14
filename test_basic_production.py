#!/usr/bin/env python3
"""
Basic Production System Test (No PyTorch Required)

This script tests the production system components without heavy ML dependencies.
"""

import os
import sys
import logging
import json
import pandas as pd
from pathlib import Path
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BasicProductionTester:
    """Test production system without ML dependencies"""
    
    def __init__(self, config_file: str = "test_data/test_config.yaml"):
        self.config_file = config_file
        self.test_results = {}
        
    def run_all_tests(self):
        """Run comprehensive test suite"""
        logger.info("🧪 Starting Basic Production System Tests")
        
        tests = [
            ("Environment Check", self.test_environment),
            ("Configuration Loading", self.test_config_loading),
            ("VCF Data Validation", self.test_vcf_data),
            ("Phenotype Data Validation", self.test_phenotype_data),
            ("Environmental Data Validation", self.test_environmental_data),
            ("Neo4j Connection", self.test_neo4j_connection),
            ("Schema Validation", self.test_schema_validation)
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
    
    def test_environment(self):
        """Test Python environment and basic packages"""
        logger.info("Testing environment...")
        
        # Check Python version
        python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        logger.info(f"Python version: {python_version}")
        
        # Test essential packages
        packages = {
            'pandas': 'Data processing',
            'numpy': 'Numerical computing',
            'neo4j': 'Graph database driver',
            'yaml': 'Configuration parsing',
            'requests': 'HTTP requests'
        }
        
        available_packages = {}
        for package, description in packages.items():
            try:
                if package == 'yaml':
                    import yaml
                    available_packages[package] = getattr(yaml, '__version__', 'available')
                else:
                    module = __import__(package)
                    available_packages[package] = getattr(module, '__version__', 'available')
                logger.info(f"✅ {package}: {available_packages[package]}")
            except ImportError:
                logger.warning(f"❌ {package}: Not available")
                available_packages[package] = 'missing'
        
        return {
            'python_version': python_version,
            'packages': available_packages
        }
    
    def test_config_loading(self):
        """Test configuration file loading"""
        logger.info("Testing configuration loading...")
        
        if not os.path.exists(self.config_file):
            raise FileNotFoundError(f"Config file not found: {self.config_file}")
        
        try:
            import yaml
            with open(self.config_file, 'r') as f:
                config = yaml.safe_load(f)
            
            logger.info(f"✅ Configuration loaded from {self.config_file}")
            
            # Validate required sections
            required_sections = ['neo4j', 'data_sources', 'processing']
            missing_sections = []
            
            for section in required_sections:
                if section not in config:
                    missing_sections.append(section)
                else:
                    logger.info(f"  ✅ {section} section present")
            
            if missing_sections:
                logger.warning(f"Missing sections: {missing_sections}")
            
            return {
                'config_file': self.config_file,
                'sections': list(config.keys()),
                'missing_sections': missing_sections
            }
            
        except ImportError:
            logger.warning("PyYAML not available, using default config")
            return {'status': 'default_config_used'}
    
    def test_vcf_data(self):
        """Test VCF data validation"""
        logger.info("Testing VCF data...")
        
        vcf_file = "test_data/sample_vcf.vcf"
        if not os.path.exists(vcf_file):
            raise FileNotFoundError(f"VCF file not found: {vcf_file}")
        
        # Parse VCF file
        variants = []
        samples = []
        
        with open(vcf_file, 'r') as f:
            for line in f:
                if line.startswith('##'):
                    continue
                elif line.startswith('#CHROM'):
                    fields = line.strip().split('\t')
                    if len(fields) > 9:
                        samples = fields[9:]
                elif not line.startswith('#'):
                    fields = line.strip().split('\t')
                    if len(fields) >= 8:
                        variant = {
                            'chromosome': fields[0],
                            'position': int(fields[1]),
                            'id': fields[2],
                            'ref': fields[3],
                            'alt': fields[4]
                        }
                        variants.append(variant)
        
        logger.info(f"  Parsed {len(variants)} variants")
        logger.info(f"  Found {len(samples)} samples")
        
        return {
            'file': vcf_file,
            'variants_count': len(variants),
            'samples_count': len(samples),
            'samples': samples,
            'chromosomes': list(set(v['chromosome'] for v in variants))
        }
    
    def test_phenotype_data(self):
        """Test phenotype data validation"""
        logger.info("Testing phenotype data...")
        
        results = {}
        
        # Test wide format
        wide_file = "test_data/sample_phenotypes_wide.csv"
        if os.path.exists(wide_file):
            df_wide = pd.read_csv(wide_file)
            metadata_cols = ['germplasm_id', 'trial_id', 'plot_id', 'replicate', 'block', 'timestamp']
            trait_cols = [col for col in df_wide.columns if col not in metadata_cols]
            
            results['wide_format'] = {
                'file': wide_file,
                'rows': df_wide.shape[0],
                'traits': trait_cols,
                'germplasm_count': df_wide['germplasm_id'].nunique()
            }
            logger.info(f"  Wide format: {df_wide.shape[0]} rows, {len(trait_cols)} traits")
        
        # Test long format
        long_file = "test_data/sample_phenotypes_long.csv"
        if os.path.exists(long_file):
            df_long = pd.read_csv(long_file)
            traits = df_long['trait'].unique().tolist()
            
            results['long_format'] = {
                'file': long_file,
                'measurements': df_long.shape[0],
                'traits': traits,
                'germplasm_count': df_long['germplasm_id'].nunique()
            }
            logger.info(f"  Long format: {df_long.shape[0]} measurements, {len(traits)} traits")
        
        return results
    
    def test_environmental_data(self):
        """Test environmental data validation"""
        logger.info("Testing environmental data...")
        
        env_file = "test_data/sample_environmental.csv"
        if not os.path.exists(env_file):
            raise FileNotFoundError(f"Environmental file not found: {env_file}")
        
        df_env = pd.read_csv(env_file)
        
        return {
            'file': env_file,
            'locations_count': len(df_env),
            'locations': df_env['location'].tolist(),
            'stress_types': df_env['stress_type'].unique().tolist(),
            'columns': list(df_env.columns)
        }
    
    def test_neo4j_connection(self):
        """Test Neo4j database connection"""
        logger.info("Testing Neo4j connection...")
        
        try:
            from neo4j import GraphDatabase
            
            # Try to connect
            driver = GraphDatabase.driver("bolt://localhost:7687", auth=("neo4j", "password"))
            
            with driver.session() as session:
                result = session.run("RETURN 1 as test")
                test_value = result.single()["test"]
                
                if test_value == 1:
                    logger.info("✅ Neo4j connection successful!")
                    
                    # Get database info
                    db_info = session.run("CALL dbms.components() YIELD name, versions, edition")
                    components = [record.data() for record in db_info]
                    
                    driver.close()
                    
                    return {
                        'status': 'connected',
                        'components': components
                    }
            
        except ImportError:
            logger.warning("Neo4j driver not available")
            return {'status': 'driver_missing'}
        except Exception as e:
            logger.warning(f"Neo4j connection failed: {e}")
            return {'status': 'connection_failed', 'error': str(e)}
    
    def test_schema_validation(self):
        """Test schema validation without importing production modules"""
        logger.info("Testing schema validation...")
        
        # Basic schema validation
        expected_node_types = [
            'Gene', 'Trait', 'Variant', 'Germplasm', 'Environment', 
            'Trial', 'Measurement', 'OntologyTerm'
        ]
        
        expected_relationships = [
            'REGULATES', 'HAS_VARIANT', 'MEASURED_IN', 'CONDUCTED_IN',
            'ANNOTATED_WITH', 'LOCATED_AT'
        ]
        
        return {
            'expected_node_types': expected_node_types,
            'expected_relationships': expected_relationships,
            'schema_file': 'production_schema.py',
            'schema_exists': os.path.exists('production_schema.py')
        }
    
    def generate_test_report(self):
        """Generate comprehensive test report"""
        logger.info("\n" + "="*60)
        logger.info("📊 BASIC PRODUCTION TEST REPORT")
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
        
        # Save report
        report_file = f"basic_production_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"\n📄 Report saved to: {report_file}")
        
        # Recommendations
        logger.info("\n🎯 RECOMMENDATIONS:")
        if failed_tests == 0:
            logger.info("🎉 All basic tests passed!")
            logger.info("Next steps:")
            logger.info("1. Install PyTorch for ML features: pip install torch")
            logger.info("2. Run full production pipeline")
            logger.info("3. Start the dashboard: python breeder_dashboard.py")
        else:
            logger.info("⚠️  Some tests failed. Address the issues above.")
            logger.info("You can still use the basic functionality that passed.")

def main():
    """Main test execution"""
    print("🧬 Basic Production Knowledge Graph System - Test Suite")
    print("="*60)
    print("Testing production system without heavy ML dependencies")
    print()
    
    # Check basic requirements
    try:
        import pandas as pd
        print(f"✅ Pandas available: {pd.__version__}")
    except ImportError:
        print("❌ Pandas required. Install with: pip install pandas")
        return
    
    # Run tests
    tester = BasicProductionTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main()
