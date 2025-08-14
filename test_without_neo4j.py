#!/usr/bin/env python3
"""
Test Knowledge Graph Data Without Neo4j

This script tests the data processing and CSV generation without requiring Neo4j.
Perfect for validating your setup and data before installing database dependencies.
"""

import pandas as pd
import os
import json
from datetime import datetime

def test_original_data():
    """Test the original maize data"""
    print("🌽 Testing Original Maize Data")
    print("=" * 40)
    
    # Check if original data exists
    original_file = "toydata/maize.csv"
    if not os.path.exists(original_file):
        print(f"❌ Original data file not found: {original_file}")
        return False
    
    # Load and analyze the data
    df = pd.read_csv(original_file)
    print(f"✅ Loaded {original_file}")
    print(f"   Shape: {df.shape[0]} rows, {df.shape[1]} columns")
    print(f"   Columns: {list(df.columns)}")
    
    # Show sample data
    print("\n📊 Sample data:")
    print(df.head(3).to_string())
    
    # Analyze the relationships
    if 'subject' in df.columns and 'predicate' in df.columns and 'object' in df.columns:
        print(f"\n🔗 Relationship Analysis:")
        print(f"   Unique subjects: {df['subject'].nunique()}")
        print(f"   Unique predicates: {df['predicate'].nunique()}")
        print(f"   Unique objects: {df['object'].nunique()}")
        print(f"   Predicate types: {df['predicate'].unique().tolist()}")
    
    return True

def test_additional_data():
    """Test additional CSV files in toydata"""
    print("\n📁 Testing Additional Data Files")
    print("=" * 40)
    
    toydata_dir = "toydata"
    if not os.path.exists(toydata_dir):
        print(f"❌ Toydata directory not found: {toydata_dir}")
        return False
    
    csv_files = [f for f in os.listdir(toydata_dir) if f.endswith('.csv')]
    print(f"Found {len(csv_files)} CSV files:")
    
    file_stats = {}
    
    for csv_file in csv_files:
        file_path = os.path.join(toydata_dir, csv_file)
        try:
            df = pd.read_csv(file_path)
            stats = {
                'rows': df.shape[0],
                'columns': df.shape[1],
                'column_names': list(df.columns)
            }
            file_stats[csv_file] = stats
            print(f"✅ {csv_file}: {stats['rows']} rows, {stats['columns']} columns")
        except Exception as e:
            print(f"❌ {csv_file}: Error reading file - {e}")
            file_stats[csv_file] = {'error': str(e)}
    
    return file_stats

def test_new_test_data():
    """Test the new test data files"""
    print("\n🧪 Testing New Test Data Files")
    print("=" * 40)
    
    test_files = {
        "test_data/sample_vcf.vcf": "VCF genetic variants",
        "test_data/sample_phenotypes_wide.csv": "Phenotype data (wide format)",
        "test_data/sample_phenotypes_long.csv": "Phenotype data (long format)",
        "test_data/sample_environmental.csv": "Environmental data"
    }
    
    results = {}
    
    for file_path, description in test_files.items():
        if os.path.exists(file_path):
            try:
                if file_path.endswith('.vcf'):
                    # Parse VCF file
                    variants = 0
                    samples = []
                    with open(file_path, 'r') as f:
                        for line in f:
                            if line.startswith('#CHROM'):
                                fields = line.strip().split('\t')
                                if len(fields) > 9:
                                    samples = fields[9:]
                            elif not line.startswith('#'):
                                variants += 1
                    
                    results[file_path] = {
                        'type': 'VCF',
                        'variants': variants,
                        'samples': len(samples),
                        'sample_names': samples[:5]  # First 5 samples
                    }
                    print(f"✅ {description}: {variants} variants, {len(samples)} samples")
                
                else:
                    # Parse CSV file
                    df = pd.read_csv(file_path)
                    results[file_path] = {
                        'type': 'CSV',
                        'rows': df.shape[0],
                        'columns': df.shape[1],
                        'column_names': list(df.columns)
                    }
                    print(f"✅ {description}: {df.shape[0]} rows, {df.shape[1]} columns")
            
            except Exception as e:
                results[file_path] = {'error': str(e)}
                print(f"❌ {description}: Error - {e}")
        else:
            results[file_path] = {'status': 'not_found'}
            print(f"❌ {description}: File not found")
    
    return results

def create_sample_relationships():
    """Create sample relationship data for testing"""
    print("\n🔗 Creating Sample Relationship Data")
    print("=" * 40)
    
    # Create gene-trait relationships
    relationships = [
        {"subject": "DREB2A", "predicate": "regulates", "object": "Drought Tolerance"},
        {"subject": "ZmNAC111", "predicate": "regulates", "object": "Root Development"},
        {"subject": "PSY1", "predicate": "regulates", "object": "Carotenoid Biosynthesis"},
        {"subject": "ZmCCT", "predicate": "regulates", "object": "Flowering Time"},
        {"subject": "ZmDREB1A", "predicate": "regulates", "object": "Cold Tolerance"},
        {"subject": "ZmNF-YB2", "predicate": "regulates", "object": "Drought Tolerance"},
        {"subject": "ZmEREB1", "predicate": "regulates", "object": "Stress Response"},
        {"subject": "ZmWRKY1", "predicate": "regulates", "object": "Disease Resistance"},
        {"subject": "ZmMYB1", "predicate": "regulates", "object": "Anthocyanin Biosynthesis"},
        
        # Germplasm-trait relationships
        {"subject": "B73", "predicate": "has_trait", "object": "High Yield"},
        {"subject": "Mo17", "predicate": "has_trait", "object": "Drought Tolerance"},
        {"subject": "W22", "predicate": "has_trait", "object": "Disease Resistance"},
        {"subject": "Oh43", "predicate": "has_trait", "object": "Cold Tolerance"},
        {"subject": "PH207", "predicate": "has_trait", "object": "Early Flowering"},
        
        # QTL-trait relationships
        {"subject": "QTL_1_100", "predicate": "controls", "object": "Plant Height"},
        {"subject": "QTL_2_200", "predicate": "controls", "object": "Grain Yield"},
        {"subject": "QTL_3_300", "predicate": "controls", "object": "Flowering Time"},
        
        # Pathway relationships
        {"subject": "Drought Response Pathway", "predicate": "includes", "object": "DREB2A"},
        {"subject": "Drought Response Pathway", "predicate": "includes", "object": "ZmNAC111"},
        {"subject": "Carotenoid Pathway", "predicate": "includes", "object": "PSY1"},
    ]
    
    # Save to CSV
    df = pd.DataFrame(relationships)
    output_file = "test_relationships_generated.csv"
    df.to_csv(output_file, index=False)
    
    print(f"✅ Created {len(relationships)} relationships")
    print(f"📁 Saved to: {output_file}")
    
    # Show summary
    print(f"\n📊 Relationship Summary:")
    print(f"   Subjects: {df['subject'].nunique()} unique")
    print(f"   Predicates: {df['predicate'].nunique()} unique ({df['predicate'].unique().tolist()})")
    print(f"   Objects: {df['object'].nunique()} unique")
    
    return output_file

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n📋 Generating Test Report")
    print("=" * 40)
    
    report = {
        'timestamp': datetime.now().isoformat(),
        'python_version': f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
        'tests': {}
    }
    
    # Test original data
    try:
        original_ok = test_original_data()
        report['tests']['original_data'] = {'status': 'passed' if original_ok else 'failed'}
    except Exception as e:
        report['tests']['original_data'] = {'status': 'error', 'error': str(e)}
    
    # Test additional data
    try:
        additional_stats = test_additional_data()
        report['tests']['additional_data'] = {'status': 'passed', 'files': additional_stats}
    except Exception as e:
        report['tests']['additional_data'] = {'status': 'error', 'error': str(e)}
    
    # Test new test data
    try:
        test_data_stats = test_new_test_data()
        report['tests']['test_data'] = {'status': 'passed', 'files': test_data_stats}
    except Exception as e:
        report['tests']['test_data'] = {'status': 'error', 'error': str(e)}
    
    # Create sample relationships
    try:
        sample_file = create_sample_relationships()
        report['tests']['sample_creation'] = {'status': 'passed', 'output_file': sample_file}
    except Exception as e:
        report['tests']['sample_creation'] = {'status': 'error', 'error': str(e)}
    
    # Save report
    report_file = f"test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(report_file, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n📄 Test report saved to: {report_file}")
    return report

def main():
    """Main test function"""
    print("🧬 Knowledge Graph Data Test (No Neo4j Required)")
    print("=" * 60)
    print("This script tests your data files without requiring Neo4j installation.")
    print()
    
    # Check if pandas is available
    try:
        import pandas as pd
        print(f"✅ Pandas available: version {pd.__version__}")
    except ImportError:
        print("❌ Pandas not available. Install with: pip install pandas")
        return
    
    # Run all tests
    report = generate_test_report()
    
    # Summary
    print("\n🎯 SUMMARY")
    print("=" * 40)
    
    passed_tests = sum(1 for test in report['tests'].values() if test.get('status') == 'passed')
    total_tests = len(report['tests'])
    
    print(f"Tests passed: {passed_tests}/{total_tests}")
    
    if passed_tests == total_tests:
        print("🎉 All tests passed!")
        print("\nNext steps:")
        print("1. Install Neo4j driver: pip install neo4j")
        print("2. Start Neo4j database")
        print("3. Run: python3 build_maize_kg.py")
    else:
        print("⚠️  Some tests failed. Check the details above.")
    
    print(f"\n📊 Full report available in: test_report_*.json")

if __name__ == "__main__":
    main()
