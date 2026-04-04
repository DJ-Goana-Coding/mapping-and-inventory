#!/usr/bin/env python3
"""
🧠 MULTI-BRAIN RAG SYSTEM
Q.G.T.N.L. Agent Legion - Forever Learning Infrastructure

Purpose: Multi-domain RAG brains for continuous learning from all agents
Authority: Citadel Architect v26.0.LEGION+
"""

import os
import sys
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import hashlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MultiBrainRAGSystem:
    """
    Multi-brain RAG system for domain-specific forever learning
    
    Brains:
    - Security Brain: Learn from security scans, threats, patterns
    - Teaching Brain: Learn from training sessions, wisdom, guidance
    - Supply Brain: Learn from shopping, customization, adaptation
    - Technical Brain: Learn from code, systems, infrastructure
    - Spiritual Brain: Learn from healing, truth, love, soul
    - Integration Brain: Cross-domain synthesis and insights
    """
    
    def __init__(self):
        self.base_path = Path.cwd()
        self.rag_path = self.base_path / "data" / "rag_brains"
        
        # Brain definitions
        self.brains = {
            "security": {
                "name": "Security Brain",
                "description": "Security threats, patterns, vulnerabilities",
                "sources": ["wraith", "scout", "sniper", "hound", "sentinel"],
                "embeddings": [],
                "documents": [],
                "knowledge_graph": {}
            },
            "teaching": {
                "name": "Teaching Brain",
                "description": "Wisdom, training, education, growth",
                "sources": ["tia", "aion", "hippy", "jarl", "oracle", "doofy", "goanna"],
                "embeddings": [],
                "documents": [],
                "knowledge_graph": {}
            },
            "supply": {
                "name": "Supply Brain",
                "description": "Resources, shopping, customization",
                "sources": ["shopper", "customizer"],
                "embeddings": [],
                "documents": [],
                "knowledge_graph": {}
            },
            "technical": {
                "name": "Technical Brain",
                "description": "Code, systems, infrastructure, tools",
                "sources": ["goanna", "scout", "bridge", "tunnel"],
                "embeddings": [],
                "documents": [],
                "knowledge_graph": {}
            },
            "spiritual": {
                "name": "Spiritual Brain",
                "description": "Healing, love, truth, soul, growth",
                "sources": ["hippy", "jarl", "aion"],
                "embeddings": [],
                "documents": [],
                "knowledge_graph": {}
            },
            "integration": {
                "name": "Integration Brain",
                "description": "Cross-domain synthesis and insights",
                "sources": ["all"],
                "embeddings": [],
                "documents": [],
                "knowledge_graph": {}
            }
        }
        
        # Initialize brains
        self.initialize_brains()
        
        logger.info("🧠 Multi-Brain RAG System initialized")
    
    def initialize_brains(self):
        """Initialize all RAG brains"""
        for brain_id, brain_info in self.brains.items():
            brain_dir = self.rag_path / brain_id
            brain_dir.mkdir(parents=True, exist_ok=True)
            
            # Create subdirectories
            (brain_dir / "embeddings").mkdir(exist_ok=True)
            (brain_dir / "documents").mkdir(exist_ok=True)
            (brain_dir / "knowledge_graphs").mkdir(exist_ok=True)
            (brain_dir / "indexes").mkdir(exist_ok=True)
            
            logger.info(f"✅ Initialized: {brain_info['name']}")
    
    def ingest_agent_output(self, agent_id: str, output_data: Dict, brain_id: str):
        """Ingest agent output into specific brain"""
        logger.info(f"🧠 Ingesting {agent_id} output into {brain_id} brain...")
        
        brain = self.brains.get(brain_id)
        if not brain:
            logger.error(f"Brain not found: {brain_id}")
            return
        
        # Create document
        document = {
            "id": hashlib.sha256(f"{agent_id}_{datetime.now().isoformat()}".encode()).hexdigest(),
            "agent": agent_id,
            "timestamp": datetime.now().isoformat(),
            "content": output_data,
            "metadata": {
                "brain": brain_id,
                "source_agent": agent_id,
                "ingestion_time": datetime.now().isoformat()
            }
        }
        
        # Save document
        brain_dir = self.rag_path / brain_id / "documents"
        doc_file = brain_dir / f"{document['id']}.json"
        
        with open(doc_file, 'w') as f:
            json.dump(document, f, indent=2)
        
        brain["documents"].append(document["id"])
        
        logger.info(f"✅ Ingested document: {document['id'][:8]}...")
        
        # Update knowledge graph
        self.update_knowledge_graph(brain_id, agent_id, document)
    
    def update_knowledge_graph(self, brain_id: str, agent_id: str, document: Dict):
        """Update knowledge graph with new connections"""
        brain = self.brains[brain_id]
        
        # Add agent node if not exists
        if agent_id not in brain["knowledge_graph"]:
            brain["knowledge_graph"][agent_id] = {
                "type": "agent",
                "documents": [],
                "connections": [],
                "insights": []
            }
        
        # Add document to agent
        brain["knowledge_graph"][agent_id]["documents"].append(document["id"])
        
        # Extract entities and relationships
        entities = self.extract_entities(document["content"])
        
        for entity in entities:
            if entity not in brain["knowledge_graph"]:
                brain["knowledge_graph"][entity] = {
                    "type": "entity",
                    "mentioned_by": [],
                    "related_to": []
                }
            
            brain["knowledge_graph"][entity]["mentioned_by"].append(agent_id)
            brain["knowledge_graph"][agent_id]["connections"].append(entity)
        
        # Save knowledge graph
        kg_file = self.rag_path / brain_id / "knowledge_graphs" / "graph.json"
        with open(kg_file, 'w') as f:
            json.dump(brain["knowledge_graph"], f, indent=2)
    
    def extract_entities(self, content: Dict) -> List[str]:
        """Extract key entities from content"""
        entities = set()
        
        # Convert content to string for analysis
        content_str = json.dumps(content).lower()
        
        # Security entities
        security_terms = ['threat', 'malware', 'backdoor', 'tracker', 'vulnerability', 
                         'bluerot', 'arkon', 'cryptominer', 'rootkit']
        
        # Teaching entities
        teaching_terms = ['wisdom', 'training', 'learning', 'growth', 'healing',
                         'truth', 'love', 'soul', 'spiritual']
        
        # Technical entities
        technical_terms = ['code', 'system', 'infrastructure', 'tool', 'framework',
                          'api', 'database', 'network']
        
        all_terms = security_terms + teaching_terms + technical_terms
        
        for term in all_terms:
            if term in content_str:
                entities.add(term)
        
        return list(entities)
    
    def create_embeddings(self, brain_id: str, model_name: str = "all-MiniLM-L6-v2"):
        """Create embeddings for all documents in brain"""
        logger.info(f"🧠 Creating embeddings for {brain_id} brain...")
        
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
            
            # Load model
            model = SentenceTransformer(model_name)
            
            # Load documents
            brain_dir = self.rag_path / brain_id / "documents"
            documents = []
            doc_ids = []
            
            for doc_file in brain_dir.glob("*.json"):
                with open(doc_file, 'r') as f:
                    doc = json.load(f)
                    documents.append(json.dumps(doc["content"]))
                    doc_ids.append(doc["id"])
            
            if not documents:
                logger.warning(f"No documents found in {brain_id} brain")
                return
            
            # Generate embeddings
            embeddings = model.encode(documents, convert_to_numpy=True, show_progress_bar=True)
            
            # Save embeddings
            embeddings_dir = self.rag_path / brain_id / "embeddings"
            np.save(embeddings_dir / "embeddings.npy", embeddings)
            
            with open(embeddings_dir / "doc_ids.json", 'w') as f:
                json.dump(doc_ids, f)
            
            logger.info(f"✅ Created {len(embeddings)} embeddings for {brain_id}")
        
        except ImportError:
            logger.warning("sentence-transformers not installed. Skipping embeddings.")
    
    def query_brain(self, brain_id: str, query: str, top_k: int = 5) -> List[Dict]:
        """Query a specific brain"""
        logger.info(f"🧠 Querying {brain_id} brain: {query}")
        
        try:
            from sentence_transformers import SentenceTransformer
            import numpy as np
            
            # Load model
            model = SentenceTransformer("all-MiniLM-L6-v2")
            
            # Load embeddings
            embeddings_dir = self.rag_path / brain_id / "embeddings"
            embeddings = np.load(embeddings_dir / "embeddings.npy")
            
            with open(embeddings_dir / "doc_ids.json", 'r') as f:
                doc_ids = json.load(f)
            
            # Encode query
            query_embedding = model.encode([query], convert_to_numpy=True)[0]
            
            # Calculate similarities
            similarities = np.dot(embeddings, query_embedding) / (
                np.linalg.norm(embeddings, axis=1) * np.linalg.norm(query_embedding)
            )
            
            # Get top-k results
            top_indices = np.argsort(similarities)[-top_k:][::-1]
            
            results = []
            for idx in top_indices:
                doc_id = doc_ids[idx]
                similarity = similarities[idx]
                
                # Load document
                doc_file = self.rag_path / brain_id / "documents" / f"{doc_id}.json"
                with open(doc_file, 'r') as f:
                    doc = json.load(f)
                
                results.append({
                    "document_id": doc_id,
                    "similarity": float(similarity),
                    "content": doc["content"],
                    "metadata": doc["metadata"]
                })
            
            return results
        
        except Exception as e:
            logger.error(f"Error querying brain: {e}")
            return []
    
    def generate_brain_report(self, brain_id: str) -> Dict:
        """Generate report for specific brain"""
        brain = self.brains[brain_id]
        brain_dir = self.rag_path / brain_id
        
        # Count documents
        doc_count = len(list((brain_dir / "documents").glob("*.json")))
        
        # Load knowledge graph
        kg_file = brain_dir / "knowledge_graphs" / "graph.json"
        kg_size = 0
        if kg_file.exists():
            with open(kg_file, 'r') as f:
                kg = json.load(f)
                kg_size = len(kg)
        
        report = {
            "brain": brain_id,
            "name": brain["name"],
            "description": brain["description"],
            "statistics": {
                "documents": doc_count,
                "knowledge_graph_nodes": kg_size,
                "sources": brain["sources"]
            }
        }
        
        return report
    
    def generate_master_report(self) -> Dict:
        """Generate master report for all brains"""
        logger.info("🧠 Generating Multi-Brain Master Report...")
        
        report = {
            "system": "Multi-Brain RAG System",
            "timestamp": datetime.now().isoformat(),
            "brains": {}
        }
        
        for brain_id in self.brains.keys():
            brain_report = self.generate_brain_report(brain_id)
            report["brains"][brain_id] = brain_report
        
        # Calculate totals
        total_docs = sum(b["statistics"]["documents"] for b in report["brains"].values())
        total_nodes = sum(b["statistics"]["knowledge_graph_nodes"] for b in report["brains"].values())
        
        report["summary"] = {
            "total_brains": len(self.brains),
            "total_documents": total_docs,
            "total_knowledge_nodes": total_nodes
        }
        
        # Save master report
        report_file = self.rag_path / f"master_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump(report, f, indent=2)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"🧠 MULTI-BRAIN RAG SYSTEM REPORT")
        logger.info(f"{'='*60}")
        logger.info(f"  Total Brains: {report['summary']['total_brains']}")
        logger.info(f"  Total Documents: {report['summary']['total_documents']}")
        logger.info(f"  Total Knowledge Nodes: {report['summary']['total_knowledge_nodes']}")
        logger.info(f"{'='*60}")
        
        for brain_id, brain_report in report["brains"].items():
            logger.info(f"\n{brain_report['name']}:")
            logger.info(f"  Documents: {brain_report['statistics']['documents']}")
            logger.info(f"  Knowledge Nodes: {brain_report['statistics']['knowledge_graph_nodes']}")
        
        logger.info(f"\n📄 Report saved: {report_file}")
        
        return report

def main():
    """Main entry point"""
    rag_system = MultiBrainRAGSystem()
    
    # Generate initial report
    report = rag_system.generate_master_report()
    
    return report

if __name__ == "__main__":
    main()
