#!/usr/bin/env python3
"""
Breeder Dashboard Interface for Production Knowledge Graph

Flask + D3.js dashboard for visualizing gene-trait networks, candidate gene predictions,
and breeding decision support tools.
"""

from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
import pandas as pd
import numpy as np
import json
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from neo4j import GraphDatabase
import networkx as nx
from datetime import datetime, timedelta
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
CORS(app)

@dataclass
class NetworkNode:
    """Represents a node in the gene-trait network"""
    id: str
    label: str
    type: str  # 'gene', 'trait', 'qtl', 'germplasm'
    properties: Dict[str, Any]
    x: Optional[float] = None
    y: Optional[float] = None

@dataclass
class NetworkEdge:
    """Represents an edge in the gene-trait network"""
    source: str
    target: str
    type: str
    weight: float
    properties: Dict[str, Any]

@dataclass
class CandidateGene:
    """Represents a candidate gene prediction"""
    gene_id: str
    gene_name: str
    trait_id: str
    trait_name: str
    prediction_score: float
    confidence: float
    evidence: List[str]
    chromosome: Optional[str] = None
    position: Optional[int] = None

class KnowledgeGraphAPI:
    """API interface to the knowledge graph"""
    
    def __init__(self, neo4j_uri: str, username: str, password: str):
        self.driver = GraphDatabase.driver(neo4j_uri, auth=(username, password))
    
    def get_gene_trait_network(self, trait_filter: Optional[str] = None, 
                              max_nodes: int = 100) -> Tuple[List[NetworkNode], List[NetworkEdge]]:
        """Get gene-trait network data for visualization"""
        
        # Build query based on filters
        where_clause = ""
        if trait_filter:
            where_clause = f"WHERE t.name CONTAINS '{trait_filter}'"
        
        query = f"""
        MATCH (g:Gene)-[r:REGULATES|INFLUENCES|ASSOCIATED_WITH]->(t:Trait)
        {where_clause}
        WITH g, r, t
        LIMIT {max_nodes}
        RETURN g, r, t,
               g.chromosome as gene_chr,
               g.start_pos as gene_pos,
               t.category as trait_category,
               r.effect_size as effect_size
        """
        
        nodes = []
        edges = []
        node_ids = set()
        
        with self.driver.session() as session:
            result = session.run(query)
            
            for record in result:
                gene = record['g']
                trait = record['t']
                relationship = record['r']
                
                # Add gene node
                gene_id = gene['gene_id'] if 'gene_id' in gene else gene['name']
                if gene_id not in node_ids:
                    nodes.append(NetworkNode(
                        id=gene_id,
                        label=gene.get('symbol', gene.get('name', gene_id)),
                        type='gene',
                        properties={
                            'chromosome': record.get('gene_chr'),
                            'position': record.get('gene_pos'),
                            'description': gene.get('description', ''),
                            'biotype': gene.get('biotype', 'protein_coding')
                        }
                    ))
                    node_ids.add(gene_id)
                
                # Add trait node
                trait_id = trait['trait_id'] if 'trait_id' in trait else trait['name']
                if trait_id not in node_ids:
                    nodes.append(NetworkNode(
                        id=trait_id,
                        label=trait.get('name', trait_id),
                        type='trait',
                        properties={
                            'category': record.get('trait_category', 'phenotypic'),
                            'unit': trait.get('unit', ''),
                            'heritability': trait.get('heritability'),
                            'description': trait.get('description', '')
                        }
                    ))
                    node_ids.add(trait_id)
                
                # Add edge
                edges.append(NetworkEdge(
                    source=gene_id,
                    target=trait_id,
                    type=relationship.type,
                    weight=record.get('effect_size', 1.0),
                    properties={
                        'confidence': relationship.get('confidence', 0.5),
                        'evidence_type': relationship.get('evidence_type', 'computational'),
                        'publication': relationship.get('publication', '')
                    }
                ))
        
        return nodes, edges
    
    def get_candidate_genes(self, trait_name: str, top_k: int = 20) -> List[CandidateGene]:
        """Get candidate genes for a specific trait"""
        
        query = """
        MATCH (g:Gene)-[r:REGULATES|INFLUENCES|ASSOCIATED_WITH]->(t:Trait)
        WHERE t.name CONTAINS $trait_name
        WITH g, r, t, 
             coalesce(r.effect_size, 0.5) * coalesce(r.confidence, 0.5) as score
        ORDER BY score DESC
        LIMIT $top_k
        RETURN g.gene_id as gene_id,
               g.symbol as gene_name,
               t.trait_id as trait_id,
               t.name as trait_name,
               score as prediction_score,
               r.confidence as confidence,
               g.chromosome as chromosome,
               g.start_pos as position,
               r.evidence_type as evidence_type
        """
        
        candidates = []
        
        with self.driver.session() as session:
            result = session.run(query, trait_name=trait_name, top_k=top_k)
            
            for record in result:
                candidates.append(CandidateGene(
                    gene_id=record['gene_id'],
                    gene_name=record['gene_name'] or record['gene_id'],
                    trait_id=record['trait_id'],
                    trait_name=record['trait_name'],
                    prediction_score=record['prediction_score'],
                    confidence=record['confidence'] or 0.5,
                    evidence=[record['evidence_type'] or 'computational'],
                    chromosome=record['chromosome'],
                    position=record['position']
                ))
        
        return candidates
    
    def get_germplasm_performance(self, trait_name: str, environment: Optional[str] = None) -> List[Dict]:
        """Get germplasm performance data for a trait"""
        
        env_filter = ""
        if environment:
            env_filter = "AND e.location CONTAINS $environment"
        
        query = f"""
        MATCH (germ:Germplasm)-[:MEASURED_IN]->(m:Measurement)-[:MEASURES]->(t:Trait)
        MATCH (germ)-[:TESTED_IN]->(trial:Trial)-[:CONDUCTED_IN]->(e:Environment)
        WHERE t.name CONTAINS $trait_name {env_filter}
        RETURN germ.name as germplasm,
               avg(toFloat(m.value)) as avg_value,
               count(m) as num_measurements,
               e.location as location,
               trial.year as year
        ORDER BY avg_value DESC
        LIMIT 50
        """
        
        params = {'trait_name': trait_name}
        if environment:
            params['environment'] = environment
        
        performance_data = []
        
        with self.driver.session() as session:
            result = session.run(query, **params)
            
            for record in result:
                performance_data.append({
                    'germplasm': record['germplasm'],
                    'avg_value': record['avg_value'],
                    'num_measurements': record['num_measurements'],
                    'location': record['location'],
                    'year': record['year']
                })
        
        return performance_data
    
    def get_trait_correlations(self, trait_name: str) -> List[Dict]:
        """Get trait correlations for breeding insights"""
        
        query = """
        MATCH (germ:Germplasm)-[:MEASURED_IN]->(m1:Measurement)-[:MEASURES]->(t1:Trait)
        MATCH (germ)-[:MEASURED_IN]->(m2:Measurement)-[:MEASURES]->(t2:Trait)
        WHERE t1.name CONTAINS $trait_name AND t1 <> t2
        WITH t1.name as trait1, t2.name as trait2,
             collect([toFloat(m1.value), toFloat(m2.value)]) as value_pairs
        WHERE size(value_pairs) >= 10
        RETURN trait1, trait2, value_pairs
        LIMIT 20
        """
        
        correlations = []
        
        with self.driver.session() as session:
            result = session.run(query, trait_name=trait_name)
            
            for record in result:
                # Calculate correlation coefficient
                pairs = record['value_pairs']
                if len(pairs) >= 10:
                    x_vals = [pair[0] for pair in pairs if pair[0] is not None and pair[1] is not None]
                    y_vals = [pair[1] for pair in pairs if pair[0] is not None and pair[1] is not None]
                    
                    if len(x_vals) >= 10:
                        correlation = np.corrcoef(x_vals, y_vals)[0, 1]
                        
                        correlations.append({
                            'trait1': record['trait1'],
                            'trait2': record['trait2'],
                            'correlation': correlation,
                            'n_observations': len(x_vals)
                        })
        
        return sorted(correlations, key=lambda x: abs(x['correlation']), reverse=True)

# Initialize KG API
kg_api = KnowledgeGraphAPI(
    neo4j_uri=os.environ.get('NEO4J_URI', 'bolt://localhost:7687'),
    username=os.environ.get('NEO4J_USERNAME', 'neo4j'),
    password=os.environ.get('NEO4J_PASSWORD', 'password')
)

# Routes
@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('dashboard.html')

@app.route('/api/network')
def get_network():
    """API endpoint for gene-trait network data"""
    trait_filter = request.args.get('trait_filter', '')
    max_nodes = int(request.args.get('max_nodes', 100))
    
    try:
        nodes, edges = kg_api.get_gene_trait_network(trait_filter, max_nodes)
        
        return jsonify({
            'nodes': [asdict(node) for node in nodes],
            'edges': [asdict(edge) for edge in edges],
            'status': 'success'
        })
    
    except Exception as e:
        logger.error(f"Error getting network data: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/candidates')
def get_candidates():
    """API endpoint for candidate gene predictions"""
    trait_name = request.args.get('trait_name', '')
    top_k = int(request.args.get('top_k', 20))
    
    if not trait_name:
        return jsonify({'error': 'trait_name parameter required', 'status': 'error'}), 400
    
    try:
        candidates = kg_api.get_candidate_genes(trait_name, top_k)
        
        return jsonify({
            'candidates': [asdict(candidate) for candidate in candidates],
            'status': 'success'
        })
    
    except Exception as e:
        logger.error(f"Error getting candidate genes: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/performance')
def get_performance():
    """API endpoint for germplasm performance data"""
    trait_name = request.args.get('trait_name', '')
    environment = request.args.get('environment', '')
    
    if not trait_name:
        return jsonify({'error': 'trait_name parameter required', 'status': 'error'}), 400
    
    try:
        performance_data = kg_api.get_germplasm_performance(
            trait_name, 
            environment if environment else None
        )
        
        return jsonify({
            'performance': performance_data,
            'status': 'success'
        })
    
    except Exception as e:
        logger.error(f"Error getting performance data: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/correlations')
def get_correlations():
    """API endpoint for trait correlations"""
    trait_name = request.args.get('trait_name', '')
    
    if not trait_name:
        return jsonify({'error': 'trait_name parameter required', 'status': 'error'}), 400
    
    try:
        correlations = kg_api.get_trait_correlations(trait_name)
        
        return jsonify({
            'correlations': correlations,
            'status': 'success'
        })
    
    except Exception as e:
        logger.error(f"Error getting correlations: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/api/search')
def search():
    """API endpoint for searching genes and traits"""
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'all')  # 'gene', 'trait', 'all'
    
    if not query:
        return jsonify({'error': 'q parameter required', 'status': 'error'}), 400
    
    try:
        # Simple search implementation
        cypher_query = """
        MATCH (n)
        WHERE (n:Gene OR n:Trait) 
        AND (n.name CONTAINS $query OR n.symbol CONTAINS $query)
        RETURN n.name as name, 
               n.symbol as symbol,
               labels(n)[0] as type,
               n.description as description
        LIMIT 20
        """
        
        results = []
        with kg_api.driver.session() as session:
            result = session.run(cypher_query, query=query)
            
            for record in result:
                results.append({
                    'name': record['name'],
                    'symbol': record['symbol'],
                    'type': record['type'].lower(),
                    'description': record['description'] or ''
                })
        
        return jsonify({
            'results': results,
            'status': 'success'
        })
    
    except Exception as e:
        logger.error(f"Error in search: {e}")
        return jsonify({'error': str(e), 'status': 'error'}), 500

@app.route('/breeding-assistant')
def breeding_assistant():
    """Breeding assistant tool page"""
    return render_template('breeding_assistant.html')

@app.route('/gene-explorer')
def gene_explorer():
    """Gene explorer page"""
    return render_template('gene_explorer.html')

@app.route('/trait-analysis')
def trait_analysis():
    """Trait analysis page"""
    return render_template('trait_analysis.html')

@app.errorhandler(404)
def not_found(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    # Development server
    app.run(debug=True, host='0.0.0.0', port=5000)
else:
    # Production WSGI
    logger.info("Breeder Dashboard initialized for production")
