#!/usr/bin/env nextflow

/*
 * Production ETL Pipeline for Biological Knowledge Graph
 * 
 * This Nextflow pipeline automates the ingestion, processing, and integration
 * of biological data into a Neo4j knowledge graph with versioning and validation.
 */

nextflow.enable.dsl=2

// Pipeline parameters
params.vcf_files = "data/vcf/*.vcf.gz"
params.phenotype_files = "data/phenotypes/*.csv"
params.environmental_files = "data/environment/*.csv"
params.literature_files = "data/literature/*.json"
params.output_dir = "results"
params.neo4j_uri = "bolt://localhost:7687"
params.neo4j_user = "neo4j"
params.neo4j_password = "password"
params.batch_size = 10000
params.max_variants = null
params.validation_enabled = true
params.backup_enabled = true

// Include modules
include { validateInputData } from './modules/validation.nf'
include { processVCF } from './modules/vcf_processing.nf'
include { processPhenotypes } from './modules/phenotype_processing.nf'
include { processEnvironmental } from './modules/environmental_processing.nf'
include { integrateKnowledgeGraph } from './modules/kg_integration.nf'
include { trainGNNModels } from './modules/gnn_training.nf'
include { generateReports } from './modules/reporting.nf'
include { backupGraph } from './modules/backup.nf'

// Main workflow
workflow {
    
    log.info """
    =====================================
    Biological Knowledge Graph Pipeline
    =====================================
    VCF files       : ${params.vcf_files}
    Phenotype files : ${params.phenotype_files}
    Environment files: ${params.environmental_files}
    Output directory: ${params.output_dir}
    Neo4j URI       : ${params.neo4j_uri}
    Batch size      : ${params.batch_size}
    =====================================
    """
    
    // Create output directory
    file(params.output_dir).mkdirs()
    
    // Input channels
    vcf_ch = Channel.fromPath(params.vcf_files)
    phenotype_ch = Channel.fromPath(params.phenotype_files)
    environmental_ch = Channel.fromPath(params.environmental_files)
    
    // Validation stage
    if (params.validation_enabled) {
        validated_vcf = validateInputData(vcf_ch, 'vcf')
        validated_phenotypes = validateInputData(phenotype_ch, 'phenotype')
        validated_environmental = validateInputData(environmental_ch, 'environmental')
    } else {
        validated_vcf = vcf_ch
        validated_phenotypes = phenotype_ch
        validated_environmental = environmental_ch
    }
    
    // Backup existing graph if enabled
    if (params.backup_enabled) {
        backup_result = backupGraph()
    }
    
    // Processing stages
    processed_vcf = processVCF(validated_vcf)
    processed_phenotypes = processPhenotypes(validated_phenotypes)
    processed_environmental = processEnvironmental(validated_environmental)
    
    // Combine all processed data
    all_processed_data = processed_vcf
        .mix(processed_phenotypes)
        .mix(processed_environmental)
        .collect()
    
    // Knowledge graph integration
    kg_result = integrateKnowledgeGraph(all_processed_data)
    
    // Train GNN models
    gnn_models = trainGNNModels(kg_result)
    
    // Generate reports
    reports = generateReports(kg_result, gnn_models)
    
    // Output summary
    reports.view { report ->
        log.info "Pipeline completed successfully!"
        log.info "Reports generated: ${report}"
    }
}

// Workflow for incremental updates
workflow incremental_update {
    
    log.info "Running incremental update workflow"
    
    // Get only new/modified files
    new_vcf_ch = Channel.fromPath(params.vcf_files)
        .filter { file -> file.lastModified() > getLastRunTimestamp() }
    
    new_phenotype_ch = Channel.fromPath(params.phenotype_files)
        .filter { file -> file.lastModified() > getLastRunTimestamp() }
    
    // Process only new data
    if (new_vcf_ch.count() > 0 || new_phenotype_ch.count() > 0) {
        processed_new_vcf = processVCF(new_vcf_ch)
        processed_new_phenotypes = processPhenotypes(new_phenotype_ch)
        
        // Incremental integration
        incremental_result = integrateKnowledgeGraph(
            processed_new_vcf.mix(processed_new_phenotypes).collect()
        )
        
        // Retrain models if significant changes
        if (shouldRetrainModels(incremental_result)) {
            updated_models = trainGNNModels(incremental_result)
        }
    } else {
        log.info "No new data found for incremental update"
    }
}

// Workflow for data validation only
workflow validate_only {
    
    log.info "Running validation-only workflow"
    
    vcf_ch = Channel.fromPath(params.vcf_files)
    phenotype_ch = Channel.fromPath(params.phenotype_files)
    environmental_ch = Channel.fromPath(params.environmental_files)
    
    validation_results = validateInputData(
        vcf_ch.mix(phenotype_ch).mix(environmental_ch),
        'all'
    )
    
    validation_results.view { result ->
        log.info "Validation completed: ${result}"
    }
}

// Helper functions
def getLastRunTimestamp() {
    def timestampFile = file("${params.output_dir}/.last_run_timestamp")
    if (timestampFile.exists()) {
        return timestampFile.text.toLong()
    }
    return 0L
}

def shouldRetrainModels(integration_result) {
    // Logic to determine if models need retraining
    // Based on number of new nodes/edges added
    def stats = integration_result.stats
    def newNodes = stats.new_nodes ?: 0
    def newEdges = stats.new_edges ?: 0
    
    // Retrain if more than 1000 new nodes or 5000 new edges
    return newNodes > 1000 || newEdges > 5000
}

def updateTimestamp() {
    def timestampFile = file("${params.output_dir}/.last_run_timestamp")
    timestampFile.text = System.currentTimeMillis().toString()
}

// Workflow completion handler
workflow.onComplete {
    updateTimestamp()
    
    log.info """
    Pipeline execution summary:
    ---------------------------
    Completed at: ${workflow.complete}
    Duration    : ${workflow.duration}
    Success     : ${workflow.success}
    Exit status : ${workflow.exitStatus}
    Error report: ${workflow.errorReport ?: 'N/A'}
    """
    
    // Send notification if configured
    if (params.notification_email) {
        sendNotification(workflow)
    }
}

def sendNotification(workflow) {
    // Email notification logic
    def subject = workflow.success ? 
        "KG Pipeline Completed Successfully" : 
        "KG Pipeline Failed"
    
    def body = """
    Pipeline: ${workflow.projectName}
    Status: ${workflow.success ? 'SUCCESS' : 'FAILED'}
    Duration: ${workflow.duration}
    
    ${workflow.success ? 'All stages completed successfully.' : 'Error: ' + workflow.errorReport}
    """
    
    // Implementation would use actual email service
    log.info "Notification sent: ${subject}"
}

// Error handling
workflow.onError {
    log.error "Pipeline execution failed: ${workflow.errorReport}"
    
    // Cleanup temporary files
    cleanupTempFiles()
    
    // Restore from backup if available
    if (params.backup_enabled && params.restore_on_failure) {
        restoreFromBackup()
    }
}

def cleanupTempFiles() {
    def tempDir = file("${params.output_dir}/temp")
    if (tempDir.exists()) {
        tempDir.deleteDir()
        log.info "Temporary files cleaned up"
    }
}

def restoreFromBackup() {
    log.info "Attempting to restore from backup..."
    // Implementation would restore Neo4j from backup
}

// Configuration profiles
profiles {
    
    standard {
        process.executor = 'local'
        process.cpus = 4
        process.memory = '8 GB'
    }
    
    cluster {
        process.executor = 'slurm'
        process.queue = 'compute'
        process.cpus = 8
        process.memory = '16 GB'
        process.time = '4h'
    }
    
    cloud {
        process.executor = 'awsbatch'
        aws.region = 'us-east-1'
        aws.batch.cliPath = '/home/ec2-user/miniconda/bin/aws'
        process.queue = 'kg-processing-queue'
    }
    
    docker {
        docker.enabled = true
        docker.runOptions = '-u $(id -u):$(id -g)'
        process.container = 'kg-pipeline:latest'
    }
    
    singularity {
        singularity.enabled = true
        singularity.autoMounts = true
        process.container = 'kg-pipeline.sif'
    }
}

// Resource requirements by process
process {
    
    withName: processVCF {
        cpus = 8
        memory = '32 GB'
        time = '6h'
    }
    
    withName: processPhenotypes {
        cpus = 4
        memory = '16 GB'
        time = '2h'
    }
    
    withName: integrateKnowledgeGraph {
        cpus = 4
        memory = '16 GB'
        time = '4h'
    }
    
    withName: trainGNNModels {
        cpus = 8
        memory = '32 GB'
        time = '8h'
        accelerator = 1, type: 'nvidia-tesla-v100'
    }
}

// Monitoring and metrics
timeline {
    enabled = true
    file = "${params.output_dir}/timeline.html"
}

report {
    enabled = true
    file = "${params.output_dir}/report.html"
}

trace {
    enabled = true
    file = "${params.output_dir}/trace.txt"
}

dag {
    enabled = true
    file = "${params.output_dir}/dag.svg"
}
