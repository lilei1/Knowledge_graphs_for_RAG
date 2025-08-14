#!/usr/bin/env python3
"""
Simple Test Script for Knowledge Graph System (Python 3.13 Compatible)

This script provides basic testing without heavy ML dependencies.
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
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleKGTester:
    """Simple test suite without heavy ML dependencies"""
    
    def __init__(self):
        self.test_results = {}
        
    def run_basic_tests(self):
        """Run basic tests without Neo4j or ML dependencies"""
        logger.info("🧪 Starting Simple Knowledge Graph System Tests")
        
        tests = [
            ("Data File Validation", self.test_data_files),
            ("VCF File Parsing", self.test_vcf_parsing),
            ("Phenotype Data Processing", self.test_phenotype_processing),
            ("Environmental Data Processing", self.test_environmental_processing),
            ("CSV Generation", self.test_csv_generation)
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
    
    def test_data_files(self):
        """Test that all required data files exist"""
        logger.info("Checking test data files...")
        
        required_files = [
            "test_data/sample_vcf.vcf",
            "test_data/sample_phenotypes_wide.csv",
            "test_data/sample_phenotypes_long.csv",
            "test_data/sample_environmental.csv",
            "test_data/test_config.yaml"
        ]
        
        missing_files = []
        existing_files = []
        
        for file_path in required_files:
            if os.path.exists(file_path):
                existing_files.append(file_path)
                file_size = os.path.getsize(file_path)
                logger.info(f"  ✅ {file_path} ({file_size} bytes)")
            else:
                missing_files.append(file_path)
                logger.warning(f"  ❌ {file_path} - MISSING")
        
        return {
            'existing_files': len(existing_files),
            'missing_files': len(missing_files),
            'files': existing_files
        }
    
    def test_vcf_parsing(self):
        """Test VCF file parsing without Neo4j"""
        logger.info("Testing VCF file parsing...")
        
        vcf_file = "test_data/sample_vcf.vcf"
        if not os.path.exists(vcf_file):
            raise FileNotFoundError(f"VCF file not found: {vcf_file}")
        
        # Simple VCF parsing
        variants = []
        samples = []
        
        with open(vcf_file, 'r') as f:
            for line in f:
                if line.startswith('##'):
                    continue
                elif line.startswith('#CHROM'):
                    # Parse sample names
                    fields = line.strip().split('\t')
                    if len(fields) > 9:
                        samples = fields[9:]
                elif not line.startswith('#'):
                    # Parse variant
                    fields = line.strip().split('\t')
                    if len(fields) >= 8:
                        variant = {
                            'chromosome': fields[0],
                            'position': int(fields[1]),
                            'id': fields[2],
                            'ref': fields[3],
                            'alt': fields[4],
                            'quality': fields[5]
                        }
                        variants.append(variant)
        
        logger.info(f"  Parsed {len(variants)} variants")
        logger.info(f"  Found {len(samples)} samples: {samples}")
        
        return {
            'variants_count': len(variants),
            'samples_count': len(samples),
            'samples': samples,
            'chromosomes': list(set(v['chromosome'] for v in variants))
        }
    
    def test_phenotype_processing(self):
        """Test phenotype data processing"""
        logger.info("Testing phenotype data processing...")
        
        # Test wide format
        wide_file = "test_data/sample_phenotypes_wide.csv"
        if os.path.exists(wide_file):
            df_wide = pd.read_csv(wide_file)
            logger.info(f"  Wide format: {df_wide.shape[0]} rows, {df_wide.shape[1]} columns")
            
            # Identify trait columns
            metadata_cols = ['germplasm_id', 'trial_id', 'plot_id', 'replicate', 'block', 'timestamp']
            trait_cols = [col for col in df_wide.columns if col not in metadata_cols]
            logger.info(f"  Traits: {trait_cols}")
            
            wide_stats = {
                'rows': df_wide.shape[0],
                'columns': df_wide.shape[1],
                'traits': trait_cols,
                'germplasm_count': df_wide['germplasm_id'].nunique(),
                'trial_count': df_wide['trial_id'].nunique()
            }
        else:
            wide_stats = {'error': 'Wide format file not found'}
        
        # Test long format
        long_file = "test_data/sample_phenotypes_long.csv"
        if os.path.exists(long_file):
            df_long = pd.read_csv(long_file)
            logger.info(f"  Long format: {df_long.shape[0]} measurements")
            
            traits = df_long['trait'].unique().tolist()
            logger.info(f"  Traits: {traits}")
            
            long_stats = {
                'measurements': df_long.shape[0],
                'traits': traits,
                'germplasm_count': df_long['germplasm_id'].nunique(),
                'trial_count': df_long['trial_id'].nunique()
            }
        else:
            long_stats = {'error': 'Long format file not found'}
        
        return {
            'wide_format': wide_stats,
            'long_format': long_stats
        }
    
    def test_environmental_processing(self):
        """Test environmental data processing"""
        logger.info("Testing environmental data processing...")
        
        env_file = "test_data/sample_environmental.csv"
        if not os.path.exists(env_file):
            raise FileNotFoundError(f"Environmental file not found: {env_file}")
        
        df_env = pd.read_csv(env_file)
        logger.info(f"  Environmental data: {df_env.shape[0]} locations")
        
        locations = df_env['location'].tolist()
        stress_types = df_env['stress_type'].unique().tolist()
        
        logger.info(f"  Locations: {locations}")
        logger.info(f"  Stress types: {stress_types}")
        
        return {
            'locations_count': len(locations),
            'locations': locations,
            'stress_types': stress_types,
            'temperature_range': [df_env['temperature_avg'].min(), df_env['temperature_avg'].max()],
            'precipitation_range': [df_env['precipitation_total'].min(), df_env['precipitation_total'].max()]
        }
    
    def test_csv_generation(self):
        """Test generating CSV files for the original system"""
        logger.info("Testing CSV generation for original system...")
        
        # Create simple gene-trait relationships
        gene_trait_data = [
            {"subject": "DREB2A", "predicate": "regulates", "object": "Drought Tolerance"},
            {"subject": "ZmNAC111", "predicate": "regulates", "object": "Root Depth"},
            {"subject": "PSY1", "predicate": "regulates", "object": "Kernel Color"},
            {"subject": "ZmCCT", "predicate": "regulates", "object": "Flowering Time"},
            {"subject": "B73", "predicate": "has_trait", "object": "Drought Tolerance"},
            {"subject": "Mo17", "predicate": "has_trait", "object": "High Yield"},
            {"subject": "W22", "predicate": "has_trait", "object": "Disease Resistance"},
        ]
        
        # Save to CSV
        output_file = "test_data/generated_relationships.csv"
        df = pd.DataFrame(gene_trait_data)
        df.to_csv(output_file, index=False)
        
        logger.info(f"  Generated {len(gene_trait_data)} relationships")
        logger.info(f"  Saved to: {output_file}")
        
        return {
            'relationships_count': len(gene_trait_data),
            'output_file': output_file,
            'subjects': df['subject'].unique().tolist(),
            'predicates': df['predicate'].unique().tolist(),
            'objects': df['object'].unique().tolist()
        }
    
    def generate_test_report(self):
        """Generate test report"""
        logger.info("\n" + "="*60)
        logger.info("📊 SIMPLE TEST REPORT SUMMARY")
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
        report_file = f"simple_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        logger.info(f"\n📄 Report saved to: {report_file}")
        
        if failed_tests == 0:
            logger.info("\n🎉 ALL BASIC TESTS PASSED!")
            logger.info("You can now try:")
            logger.info("1. Original system: python3 build_maize_kg.py")
            logger.info("2. Install full requirements for production system")
        else:
            logger.info(f"\n⚠️  {failed_tests} test(s) failed. Check the errors above.")

def main():
    """Main test execution"""
    print("🧬 Simple Knowledge Graph System - Test Suite")
    print("="*60)
    print("This test runs without heavy ML dependencies")
    print()
    
    # Check Python version
    python_version = sys.version_info
    logger.info(f"Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    
    # Check pandas availability
    try:
        import pandas as pd
        logger.info(f"Pandas version: {pd.__version__}")
    except ImportError:
        logger.error("Pandas not available. Install with: pip install pandas")
        return
    
    # Run tests
    tester = SimpleKGTester()
    tester.run_basic_tests()

if __name__ == "__main__":
    main()
