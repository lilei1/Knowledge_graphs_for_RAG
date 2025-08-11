#!/usr/bin/env nextflow

/*
 * VCF Processing Module for Knowledge Graph Pipeline
 * 
 * Processes VCF files and extracts genotypic data for graph integration
 */

process processVCF {
    tag "$vcf_file.baseName"
    publishDir "${params.output_dir}/processed_vcf", mode: 'copy'
    
    input:
    path vcf_file
    
    output:
    path "*.processed.csv", emit: processed_data
    path "*.stats.json", emit: stats
    path "*.log", emit: logs
    
    script:
    """
    #!/usr/bin/env python3
    
    import sys
    import json
    import logging
    import pandas as pd
    from datetime import datetime
    
    # Add the pipeline modules to Python path
    sys.path.append('${projectDir}')
    from vcf_integration import VCFProcessor, ProcessingStats
    from production_schema import ProductionSchema
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('${vcf_file.baseName}.log'),
            logging.StreamHandler()
        ]
    )
    logger = logging.getLogger(__name__)
    
    def main():
        logger.info("Starting VCF processing for ${vcf_file}")
        
        try:
            # Initialize VCF processor (without Neo4j for this stage)
            processor = VCFProcessor(neo4j_driver=None, batch_size=${params.batch_size})
            
            # Parse VCF header to get samples
            samples, metadata = processor.parse_vcf_header('${vcf_file}')
            logger.info(f"Found {len(samples)} samples in VCF")
            
            # Process VCF file and extract data
            variants_data = []
            genotype_data = []
            
            # Read VCF file
            open_func = gzip.open if '${vcf_file}'.endswith('.gz') else open
            
            with open_func('${vcf_file}', 'rt') as f:
                line_count = 0
                for line in f:
                    if line.startswith('#'):
                        continue
                    
                    # Parse variant
                    variant = processor.parse_vcf_line(line, samples)
                    if variant is None:
                        continue
                    
                    # Create variant data
                    variant_node = processor.create_variant_node(variant)
                    variants_data.append(variant_node)
                    
                    # Create genotype relationships
                    for sample_id, genotype in variant.genotypes.items():
                        if genotype and genotype != './.' and genotype != '.':
                            alleles = genotype.replace('|', '/').split('/')
                            dosage = sum(1 for allele in alleles if allele.isdigit() and int(allele) > 0)
                            
                            genotype_data.append({
                                'germplasm_id': sample_id,
                                'variant_id': variant_node['variant_id'],
                                'genotype': genotype,
                                'dosage': dosage,
                                'quality_score': variant.quality
                            })
                    
                    line_count += 1
                    if ${params.max_variants ?: 'None'} and line_count >= ${params.max_variants ?: 'float("inf")'}:
                        break
                    
                    if line_count % 10000 == 0:
                        logger.info(f"Processed {line_count} variants")
            
            # Save processed data
            variants_df = pd.DataFrame(variants_data)
            genotypes_df = pd.DataFrame(genotype_data)
            
            variants_df.to_csv('${vcf_file.baseName}_variants.processed.csv', index=False)
            genotypes_df.to_csv('${vcf_file.baseName}_genotypes.processed.csv', index=False)
            
            # Generate statistics
            stats = {
                'file': '${vcf_file}',
                'processing_time': datetime.now().isoformat(),
                'total_variants': len(variants_df),
                'total_genotypes': len(genotypes_df),
                'samples': len(samples),
                'chromosomes': variants_df['chromosome'].nunique() if len(variants_df) > 0 else 0,
                'variant_types': variants_df['variant_type'].value_counts().to_dict() if len(variants_df) > 0 else {}
            }
            
            with open('${vcf_file.baseName}.stats.json', 'w') as f:
                json.dump(stats, f, indent=2)
            
            logger.info(f"VCF processing completed: {stats['total_variants']} variants, {stats['total_genotypes']} genotypes")
            
        except Exception as e:
            logger.error(f"VCF processing failed: {e}")
            raise
    
    if __name__ == "__main__":
        import gzip
        main()
    """
}

process validateVCF {
    tag "$vcf_file.baseName"
    
    input:
    path vcf_file
    
    output:
    path "*.validation.json", emit: validation_result
    
    script:
    """
    #!/usr/bin/env python3
    
    import json
    import gzip
    import logging
    from datetime import datetime
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    def validate_vcf(vcf_file):
        validation_result = {
            'file': vcf_file,
            'validation_time': datetime.now().isoformat(),
            'is_valid': True,
            'errors': [],
            'warnings': [],
            'stats': {}
        }
        
        try:
            open_func = gzip.open if vcf_file.endswith('.gz') else open
            
            with open_func(vcf_file, 'rt') as f:
                line_count = 0
                header_lines = 0
                data_lines = 0
                samples = []
                
                for line in f:
                    line_count += 1
                    
                    if line.startswith('##'):
                        header_lines += 1
                    elif line.startswith('#CHROM'):
                        # Parse sample names
                        fields = line.strip().split('\\t')
                        if len(fields) > 9:
                            samples = fields[9:]
                        header_lines += 1
                    elif not line.startswith('#'):
                        data_lines += 1
                        
                        # Validate data line format
                        fields = line.strip().split('\\t')
                        if len(fields) < 8:
                            validation_result['errors'].append(f"Line {line_count}: Insufficient fields ({len(fields)} < 8)")
                            validation_result['is_valid'] = False
                        
                        # Check chromosome format
                        chrom = fields[0]
                        if not chrom.replace('chr', '').replace('X', '').replace('Y', '').replace('MT', '').isdigit() and chrom not in ['X', 'Y', 'MT', 'chrX', 'chrY', 'chrMT']:
                            validation_result['warnings'].append(f"Line {line_count}: Unusual chromosome format: {chrom}")
                        
                        # Check position
                        try:
                            pos = int(fields[1])
                            if pos <= 0:
                                validation_result['errors'].append(f"Line {line_count}: Invalid position: {pos}")
                                validation_result['is_valid'] = False
                        except ValueError:
                            validation_result['errors'].append(f"Line {line_count}: Non-numeric position: {fields[1]}")
                            validation_result['is_valid'] = False
                    
                    # Limit validation to first 100,000 lines for performance
                    if line_count > 100000:
                        break
                
                validation_result['stats'] = {
                    'total_lines': line_count,
                    'header_lines': header_lines,
                    'data_lines': data_lines,
                    'samples': len(samples)
                }
                
                if data_lines == 0:
                    validation_result['errors'].append("No data lines found in VCF file")
                    validation_result['is_valid'] = False
                
                if len(samples) == 0:
                    validation_result['warnings'].append("No sample columns found")
        
        except Exception as e:
            validation_result['is_valid'] = False
            validation_result['errors'].append(f"Exception during validation: {str(e)}")
        
        return validation_result
    
    # Run validation
    result = validate_vcf('${vcf_file}')
    
    with open('${vcf_file.baseName}.validation.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    if result['is_valid']:
        print(f"VCF validation PASSED for ${vcf_file}")
    else:
        print(f"VCF validation FAILED for ${vcf_file}")
        for error in result['errors']:
            print(f"ERROR: {error}")
    """
}

process createGermplasmNodes {
    tag "germplasm_creation"
    publishDir "${params.output_dir}/germplasm", mode: 'copy'
    
    input:
    path processed_vcf_files
    
    output:
    path "germplasm_nodes.csv", emit: germplasm_data
    
    script:
    """
    #!/usr/bin/env python3
    
    import pandas as pd
    import logging
    from pathlib import Path
    
    logging.basicConfig(level=logging.INFO)
    logger = logging.getLogger(__name__)
    
    def extract_germplasm_from_vcf_data():
        germplasm_set = set()
        
        # Process all genotype files
        for vcf_file in Path('.').glob('*_genotypes.processed.csv'):
            logger.info(f"Processing {vcf_file}")
            df = pd.read_csv(vcf_file)
            
            if 'germplasm_id' in df.columns:
                germplasm_set.update(df['germplasm_id'].unique())
        
        # Create germplasm nodes
        germplasm_data = []
        for germplasm_id in germplasm_set:
            germplasm_data.append({
                'germplasm_id': germplasm_id,
                'name': germplasm_id,
                'species': 'Zea mays',  # Default for maize
                'source': 'VCF_processing'
            })
        
        germplasm_df = pd.DataFrame(germplasm_data)
        germplasm_df.to_csv('germplasm_nodes.csv', index=False)
        
        logger.info(f"Created {len(germplasm_df)} germplasm nodes")
        return germplasm_df
    
    extract_germplasm_from_vcf_data()
    """
}

process aggregateVCFStats {
    publishDir "${params.output_dir}/stats", mode: 'copy'
    
    input:
    path stats_files
    
    output:
    path "vcf_processing_summary.json", emit: summary
    
    script:
    """
    #!/usr/bin/env python3
    
    import json
    import pandas as pd
    from pathlib import Path
    from datetime import datetime
    
    def aggregate_stats():
        all_stats = []
        
        for stats_file in Path('.').glob('*.stats.json'):
            with open(stats_file, 'r') as f:
                stats = json.load(f)
                all_stats.append(stats)
        
        # Calculate summary statistics
        summary = {
            'processing_summary': {
                'total_files': len(all_stats),
                'total_variants': sum(s['total_variants'] for s in all_stats),
                'total_genotypes': sum(s['total_genotypes'] for s in all_stats),
                'total_samples': sum(s['samples'] for s in all_stats),
                'processing_time': datetime.now().isoformat()
            },
            'file_details': all_stats
        }
        
        with open('vcf_processing_summary.json', 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"VCF Processing Summary:")
        print(f"  Files processed: {summary['processing_summary']['total_files']}")
        print(f"  Total variants: {summary['processing_summary']['total_variants']:,}")
        print(f"  Total genotypes: {summary['processing_summary']['total_genotypes']:,}")
        print(f"  Total samples: {summary['processing_summary']['total_samples']:,}")
    
    aggregate_stats()
    """
}
