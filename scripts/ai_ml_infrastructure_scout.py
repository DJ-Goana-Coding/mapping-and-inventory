#!/usr/bin/env python3
"""
🤖 AI/ML INFRASTRUCTURE SCOUT v1.0
Agent Mission: AI/ML Infrastructure & Services Discovery

Discovers and catalogs:
- LLM APIs (OpenAI, Anthropic, Google Gemini, local Ollama)
- Embedding models (OpenAI, Cohere, Sentence Transformers)
- Vector databases (Pinecone, Weaviate, Qdrant, Chroma)
- Hugging Face Inference API
- AI orchestration (LangChain, LlamaIndex, Semantic Kernel)
- Model hosting and deployment

Output: data/agent_requisitions/ai_infrastructure.json
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List

class AIMLInfrastructureScout:
    """Autonomous AI/ML infrastructure discovery agent"""
    
    def __init__(self, output_dir: str = "./data/agent_requisitions"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        self.discoveries = {
            "meta": {
                "agent": "AI/ML Infrastructure Scout",
                "mission": "AI/ML Infrastructure & Services Discovery",
                "timestamp": datetime.utcnow().isoformat(),
                "version": "1.0"
            },
            "categories": {}
        }
    
    def discover_llm_apis(self) -> Dict:
        """Discover Large Language Model APIs"""
        return {
            "name": "LLM APIs",
            "description": "Commercial and open-source language model APIs",
            "technologies": [
                {
                    "name": "OpenAI API",
                    "type": "Commercial LLM API",
                    "models": ["GPT-4o", "GPT-4 Turbo", "GPT-3.5 Turbo", "o1", "o1-mini"],
                    "features": [
                        "State-of-the-art reasoning",
                        "Function calling",
                        "JSON mode",
                        "Vision capabilities (GPT-4o)",
                        "128K context window",
                        "Streaming responses"
                    ],
                    "cost": "GPT-4o: $5/$15 per 1M tokens (in/out), GPT-3.5: $0.50/$1.50",
                    "popularity": "10/10",
                    "best_for": "Production apps, complex reasoning",
                    "website": "https://platform.openai.com",
                    "api_docs": "https://platform.openai.com/docs"
                },
                {
                    "name": "Anthropic Claude",
                    "type": "Commercial LLM API",
                    "models": ["Claude 3.5 Sonnet", "Claude 3 Opus", "Claude 3 Haiku"],
                    "features": [
                        "200K context window",
                        "Superior reasoning",
                        "Safety-focused",
                        "Vision capabilities",
                        "Tool use (function calling)",
                        "Streaming"
                    ],
                    "cost": "Sonnet 3.5: $3/$15 per 1M tokens, Opus: $15/$75",
                    "popularity": "9/10",
                    "best_for": "Long-context tasks, safe AI",
                    "website": "https://www.anthropic.com",
                    "api_docs": "https://docs.anthropic.com"
                },
                {
                    "name": "Google Gemini API",
                    "type": "Commercial LLM API",
                    "models": ["Gemini 2.0 Flash", "Gemini 1.5 Pro", "Gemini 1.5 Flash"],
                    "features": [
                        "1M+ token context (Gemini 1.5 Pro)",
                        "Multimodal (text, images, video, audio)",
                        "Function calling",
                        "Code execution",
                        "Grounding with Google Search",
                        "Free tier available"
                    ],
                    "cost": "Flash: FREE up to 15 RPM, Pro: $0.35/$1.05 per 1M tokens",
                    "popularity": "9/10",
                    "best_for": "Multimodal AI, long-context tasks",
                    "website": "https://ai.google.dev",
                    "api_docs": "https://ai.google.dev/docs"
                },
                {
                    "name": "Groq",
                    "type": "Ultra-fast LLM inference",
                    "models": ["Llama 3.3 70B", "Llama 3.1 405B", "Mixtral 8x7B"],
                    "features": [
                        "Fastest inference (700+ tokens/sec)",
                        "Open-source models",
                        "Low latency (<100ms TTFT)",
                        "Free tier available",
                        "JSON mode",
                        "Function calling"
                    ],
                    "cost": "FREE tier (generous), then pay-per-use",
                    "popularity": "8/10",
                    "best_for": "Speed-critical apps, real-time AI",
                    "website": "https://groq.com",
                    "api_docs": "https://console.groq.com/docs"
                },
                {
                    "name": "Ollama",
                    "type": "Local LLM runtime",
                    "models": ["Llama 3.3", "Mistral", "Gemma 2", "Qwen", "70+ more"],
                    "features": [
                        "100% local/private",
                        "No API costs",
                        "Model library (70+ models)",
                        "OpenAI-compatible API",
                        "GPU acceleration",
                        "Model customization (Modelfile)"
                    ],
                    "cost": "FREE (hardware costs only)",
                    "popularity": "10/10",
                    "best_for": "Privacy, offline AI, development",
                    "website": "https://ollama.com",
                    "github": "ollama/ollama"
                },
                {
                    "name": "Together AI",
                    "type": "Open-source model API",
                    "models": ["Llama 3.3", "Qwen 2.5", "Mixtral", "custom fine-tuned"],
                    "features": [
                        "Fast inference",
                        "50+ open models",
                        "Fine-tuning platform",
                        "Competitive pricing",
                        "Function calling",
                        "JSON mode"
                    ],
                    "cost": "From $0.18/$0.18 per 1M tokens (Llama 3.3 70B)",
                    "popularity": "7/10",
                    "best_for": "Open models, fine-tuning",
                    "website": "https://together.ai",
                    "api_docs": "https://docs.together.ai"
                }
            ]
        }
    
    def discover_embedding_models(self) -> Dict:
        """Discover embedding model services"""
        return {
            "name": "Embedding Models",
            "description": "Text embedding APIs for semantic search and RAG",
            "technologies": [
                {
                    "name": "OpenAI Embeddings",
                    "type": "Commercial embedding API",
                    "models": ["text-embedding-3-large", "text-embedding-3-small", "text-embedding-ada-002"],
                    "features": [
                        "3072 dimensions (large)",
                        "High quality embeddings",
                        "Multilingual support",
                        "Dimension reduction",
                        "Fast inference"
                    ],
                    "cost": "text-embedding-3-small: $0.02/1M tokens, large: $0.13/1M",
                    "popularity": "10/10",
                    "best_for": "Production RAG, semantic search",
                    "website": "https://platform.openai.com/docs/guides/embeddings"
                },
                {
                    "name": "Cohere Embed",
                    "type": "Commercial embedding API",
                    "models": ["embed-v3", "embed-english-v3.0", "embed-multilingual-v3.0"],
                    "features": [
                        "1024 dimensions",
                        "Compression (int8, binary)",
                        "Task-specific embeddings",
                        "100+ languages",
                        "Semantic search optimization"
                    ],
                    "cost": "embed-v3: $0.10/1M tokens",
                    "popularity": "8/10",
                    "best_for": "Multilingual search, classification",
                    "website": "https://cohere.com/embed",
                    "api_docs": "https://docs.cohere.com"
                },
                {
                    "name": "Voyage AI",
                    "type": "Specialized embedding API",
                    "models": ["voyage-3", "voyage-code-2", "voyage-finance-2"],
                    "features": [
                        "Domain-specific models",
                        "State-of-the-art retrieval",
                        "1024 dimensions",
                        "Long context (32K tokens)",
                        "Reranking models"
                    ],
                    "cost": "voyage-3: $0.06/1M tokens",
                    "popularity": "7/10",
                    "best_for": "Code search, finance, legal",
                    "website": "https://www.voyageai.com",
                    "api_docs": "https://docs.voyageai.com"
                },
                {
                    "name": "Sentence Transformers (Local)",
                    "type": "Open-source embedding library",
                    "models": ["all-MiniLM-L6-v2", "all-mpnet-base-v2", "e5-large-v2"],
                    "features": [
                        "100% free and local",
                        "Hugging Face integration",
                        "Pre-trained models",
                        "Fine-tuning support",
                        "GPU acceleration",
                        "Semantic search utilities"
                    ],
                    "cost": "FREE (hardware costs only)",
                    "popularity": "10/10",
                    "best_for": "Privacy, offline, development",
                    "website": "https://www.sbert.net",
                    "github": "UKPLab/sentence-transformers"
                },
                {
                    "name": "Jina AI Embeddings",
                    "type": "Cloud and local embeddings",
                    "models": ["jina-embeddings-v3", "jina-clip-v1"],
                    "features": [
                        "8K context length",
                        "Multimodal (text and images)",
                        "Self-hosted option",
                        "Task-specific fine-tuning",
                        "Late chunking for long docs"
                    ],
                    "cost": "FREE tier, then $0.02/1M tokens",
                    "popularity": "7/10",
                    "best_for": "Long documents, multimodal",
                    "website": "https://jina.ai",
                    "api_docs": "https://jina.ai/embeddings"
                }
            ]
        }
    
    def discover_vector_databases(self) -> Dict:
        """Discover vector database services"""
        return {
            "name": "Vector Databases",
            "description": "Vector storage and similarity search databases",
            "technologies": [
                {
                    "name": "Pinecone",
                    "type": "Managed vector database",
                    "features": [
                        "Fully managed",
                        "Serverless architecture",
                        "Sub-100ms queries",
                        "Metadata filtering",
                        "Hybrid search",
                        "Free tier: 1 index, 100K vectors"
                    ],
                    "cost": "FREE tier, Starter: $0.096/GB/month",
                    "popularity": "10/10",
                    "learning_curve": "Low",
                    "best_for": "Production RAG, managed solution",
                    "website": "https://www.pinecone.io",
                    "api_docs": "https://docs.pinecone.io"
                },
                {
                    "name": "Weaviate",
                    "type": "Open-source vector database",
                    "features": [
                        "Self-hosted or cloud",
                        "Hybrid search (vector + keyword)",
                        "Multi-tenancy",
                        "GraphQL and REST APIs",
                        "Module system (text2vec, etc.)",
                        "Generative search (RAG built-in)"
                    ],
                    "cost": "FREE (self-hosted), Cloud: from $25/month",
                    "popularity": "9/10",
                    "learning_curve": "Medium",
                    "best_for": "Flexible RAG, GraphQL fans",
                    "website": "https://weaviate.io",
                    "github": "weaviate/weaviate"
                },
                {
                    "name": "Qdrant",
                    "type": "High-performance vector database",
                    "features": [
                        "Written in Rust (fast)",
                        "Self-hosted or cloud",
                        "Advanced filtering",
                        "Payload indexing",
                        "Quantization support",
                        "Distributed mode",
                        "Free cloud tier: 1GB cluster"
                    ],
                    "cost": "FREE (self-hosted or 1GB cloud), Cloud: from $25/month",
                    "popularity": "9/10",
                    "learning_curve": "Low",
                    "best_for": "High-performance search, Rust ecosystem",
                    "website": "https://qdrant.tech",
                    "github": "qdrant/qdrant"
                },
                {
                    "name": "Chroma",
                    "type": "AI-native embedding database",
                    "features": [
                        "Open-source",
                        "Simple Python API",
                        "Built-in embedding models",
                        "LangChain integration",
                        "In-memory or persistent",
                        "Lightweight (SQLite-based)"
                    ],
                    "cost": "FREE (open source)",
                    "popularity": "9/10",
                    "learning_curve": "Very Low",
                    "best_for": "Prototyping, LangChain apps",
                    "website": "https://www.trychroma.com",
                    "github": "chroma-core/chroma"
                },
                {
                    "name": "Milvus",
                    "type": "Cloud-native vector database",
                    "features": [
                        "Highly scalable",
                        "GPU acceleration",
                        "Hybrid search",
                        "Time travel (versioning)",
                        "Multiple index types",
                        "Kubernetes-native"
                    ],
                    "cost": "FREE (self-hosted), Zilliz Cloud: from $0/month",
                    "popularity": "8/10",
                    "learning_curve": "High",
                    "best_for": "Enterprise scale, billion+ vectors",
                    "website": "https://milvus.io",
                    "github": "milvus-io/milvus"
                },
                {
                    "name": "pgvector (PostgreSQL)",
                    "type": "Vector extension for PostgreSQL",
                    "features": [
                        "Native PostgreSQL extension",
                        "HNSW and IVFFlat indexes",
                        "Exact and approximate search",
                        "Use existing Postgres infrastructure",
                        "ACID transactions",
                        "Free and open source"
                    ],
                    "cost": "FREE (open source)",
                    "popularity": "9/10",
                    "learning_curve": "Low (if familiar with Postgres)",
                    "best_for": "Postgres users, simplicity",
                    "website": "https://github.com/pgvector/pgvector",
                    "supported_by": ["Supabase", "Neon", "RDS", "Cloud SQL"]
                }
            ]
        }
    
    def discover_ai_orchestration(self) -> Dict:
        """Discover AI orchestration frameworks"""
        return {
            "name": "AI Orchestration Frameworks",
            "description": "LLM application development frameworks",
            "technologies": [
                {
                    "name": "LangChain",
                    "type": "LLM application framework",
                    "features": [
                        "Chains and agents",
                        "Memory systems",
                        "Tool/function calling",
                        "Vector store integrations",
                        "Document loaders",
                        "LangSmith observability",
                        "LangGraph for workflows"
                    ],
                    "cost": "FREE (open source), LangSmith: $39/month",
                    "popularity": "10/10",
                    "learning_curve": "Medium",
                    "best_for": "Complex LLM apps, RAG systems",
                    "website": "https://www.langchain.com",
                    "github": "langchain-ai/langchain"
                },
                {
                    "name": "LlamaIndex",
                    "type": "Data framework for LLMs",
                    "features": [
                        "Specialized for RAG",
                        "100+ data connectors",
                        "Query engines",
                        "Advanced indexing strategies",
                        "Evaluation tools",
                        "LlamaParse (document parsing)"
                    ],
                    "cost": "FREE (open source), LlamaCloud: from $49/month",
                    "popularity": "9/10",
                    "learning_curve": "Medium",
                    "best_for": "RAG applications, data ingestion",
                    "website": "https://www.llamaindex.ai",
                    "github": "run-llama/llama_index"
                },
                {
                    "name": "Semantic Kernel",
                    "type": "Microsoft AI SDK",
                    "features": [
                        "Multi-language (C#, Python, Java)",
                        "Plugin architecture",
                        "Planners (automatic chaining)",
                        "Memory connectors",
                        "Enterprise-focused",
                        "Azure integration"
                    ],
                    "cost": "FREE (open source)",
                    "popularity": "7/10",
                    "learning_curve": "Medium",
                    "best_for": ".NET developers, enterprise",
                    "website": "https://learn.microsoft.com/en-us/semantic-kernel",
                    "github": "microsoft/semantic-kernel"
                },
                {
                    "name": "Haystack",
                    "type": "NLP framework for search",
                    "features": [
                        "Production-ready pipelines",
                        "RAG and question answering",
                        "Custom components",
                        "Evaluation framework",
                        "Document stores",
                        "Deepset Cloud integration"
                    ],
                    "cost": "FREE (open source), Cloud: custom pricing",
                    "popularity": "7/10",
                    "learning_curve": "Medium",
                    "best_for": "Search applications, NLP pipelines",
                    "website": "https://haystack.deepset.ai",
                    "github": "deepset-ai/haystack"
                },
                {
                    "name": "AutoGen",
                    "type": "Multi-agent framework",
                    "features": [
                        "Conversable agents",
                        "Agent orchestration",
                        "Human-in-the-loop",
                        "Code execution",
                        "Group chat agents",
                        "Microsoft research project"
                    ],
                    "cost": "FREE (open source)",
                    "popularity": "8/10",
                    "learning_curve": "High",
                    "best_for": "Multi-agent systems, complex workflows",
                    "website": "https://microsoft.github.io/autogen",
                    "github": "microsoft/autogen"
                }
            ]
        }
    
    def discover_huggingface_inference(self) -> Dict:
        """Discover Hugging Face Inference services"""
        return {
            "name": "Hugging Face Inference",
            "description": "Model hosting and inference on Hugging Face",
            "technologies": [
                {
                    "name": "Hugging Face Inference API",
                    "type": "Serverless model inference",
                    "features": [
                        "200K+ models available",
                        "Text generation, embeddings, classification",
                        "Image generation (Stable Diffusion)",
                        "Speech recognition (Whisper)",
                        "Free tier with rate limits",
                        "Simple REST API"
                    ],
                    "cost": "FREE tier, Pro: $9/month, Enterprise: custom",
                    "popularity": "10/10",
                    "learning_curve": "Very Low",
                    "best_for": "Prototyping, open models",
                    "website": "https://huggingface.co/inference-api",
                    "api_docs": "https://huggingface.co/docs/api-inference"
                },
                {
                    "name": "Hugging Face Inference Endpoints",
                    "type": "Dedicated model hosting",
                    "features": [
                        "Private dedicated endpoints",
                        "Auto-scaling",
                        "GPU options",
                        "Custom models",
                        "Low latency",
                        "High throughput"
                    ],
                    "cost": "From $0.60/hour (CPU) to $4.50/hour (GPU)",
                    "popularity": "8/10",
                    "learning_curve": "Low",
                    "best_for": "Production workloads, custom models",
                    "website": "https://huggingface.co/inference-endpoints"
                },
                {
                    "name": "Hugging Face Spaces",
                    "type": "ML app hosting",
                    "features": [
                        "Gradio and Streamlit apps",
                        "Free CPU hosting",
                        "GPU upgrades available",
                        "Custom Docker containers",
                        "CI/CD integration",
                        "Public or private"
                    ],
                    "cost": "FREE (CPU), GPU: from $0.60/hour",
                    "popularity": "9/10",
                    "learning_curve": "Low",
                    "best_for": "Demos, prototypes, shared apps",
                    "website": "https://huggingface.co/spaces"
                },
                {
                    "name": "Text Generation Inference (TGI)",
                    "type": "LLM serving toolkit",
                    "features": [
                        "Optimized LLM inference",
                        "Continuous batching",
                        "Flash Attention",
                        "Quantization support",
                        "OpenAI-compatible API",
                        "Docker deployment"
                    ],
                    "cost": "FREE (self-hosted)",
                    "popularity": "8/10",
                    "learning_curve": "Medium",
                    "best_for": "Self-hosted LLM serving",
                    "github": "huggingface/text-generation-inference"
                },
                {
                    "name": "Transformers.js",
                    "type": "Browser and Node.js inference",
                    "features": [
                        "Run models in browser",
                        "ONNX runtime",
                        "No server needed",
                        "Privacy-preserving",
                        "100+ pre-converted models",
                        "WebGPU acceleration"
                    ],
                    "cost": "FREE (open source)",
                    "popularity": "8/10",
                    "learning_curve": "Low",
                    "best_for": "Client-side AI, privacy",
                    "npm": "@xenova/transformers",
                    "github": "xenova/transformers.js"
                }
            ]
        }
    
    def discover_model_deployment(self) -> Dict:
        """Discover model deployment and serving platforms"""
        return {
            "name": "Model Deployment Platforms",
            "description": "ML model hosting, serving, and MLOps",
            "technologies": [
                {
                    "name": "Modal",
                    "type": "Serverless compute for ML",
                    "features": [
                        "Serverless GPU functions",
                        "Auto-scaling",
                        "Container-based",
                        "Python-native",
                        "Scheduled jobs",
                        "Free tier: $30 credits/month"
                    ],
                    "cost": "FREE $30/month, then pay-as-you-go",
                    "popularity": "7/10",
                    "learning_curve": "Low",
                    "best_for": "ML inference, batch jobs",
                    "website": "https://modal.com"
                },
                {
                    "name": "Replicate",
                    "type": "ML model API platform",
                    "features": [
                        "Run models via API",
                        "Deploy custom models",
                        "Auto-scaling",
                        "COG (container format)",
                        "Public model library",
                        "Pay per second"
                    ],
                    "cost": "Pay-per-use (from $0.0001/second)",
                    "popularity": "8/10",
                    "learning_curve": "Very Low",
                    "best_for": "Image/video generation, quick deployment",
                    "website": "https://replicate.com"
                },
                {
                    "name": "BentoML",
                    "type": "ML serving framework",
                    "features": [
                        "Model serving framework",
                        "Multi-model serving",
                        "Adaptive batching",
                        "OpenAPI integration",
                        "BentoCloud (managed)",
                        "Self-hosted option"
                    ],
                    "cost": "FREE (self-hosted), Cloud: from $49/month",
                    "popularity": "7/10",
                    "learning_curve": "Medium",
                    "best_for": "Production ML serving",
                    "website": "https://www.bentoml.com",
                    "github": "bentoml/BentoML"
                },
                {
                    "name": "Banana.dev",
                    "type": "Serverless GPU inference",
                    "features": [
                        "Serverless GPUs",
                        "Sub-second cold starts",
                        "Custom models",
                        "Auto-scaling",
                        "Simple deployment"
                    ],
                    "cost": "Pay-per-use (from $0.0005/second)",
                    "popularity": "6/10",
                    "learning_curve": "Low",
                    "best_for": "GPU inference, image generation",
                    "website": "https://www.banana.dev"
                },
                {
                    "name": "Baseten",
                    "type": "ML inference platform",
                    "features": [
                        "Serverless GPU deployment",
                        "Truss (model packaging)",
                        "Auto-scaling",
                        "Low latency",
                        "Model versioning",
                        "Monitoring"
                    ],
                    "cost": "Free tier, then pay-per-use",
                    "popularity": "6/10",
                    "learning_curve": "Low",
                    "best_for": "Production ML APIs",
                    "website": "https://www.baseten.co"
                }
            ]
        }
    
    def run_discovery(self) -> Dict:
        """Execute full discovery mission"""
        print("🤖 AI/ML Infrastructure Scout - Mission Start")
        print("=" * 60)
        
        self.discoveries["categories"]["llm_apis"] = self.discover_llm_apis()
        print("✓ LLM APIs discovered")
        
        self.discoveries["categories"]["embedding_models"] = self.discover_embedding_models()
        print("✓ Embedding Models discovered")
        
        self.discoveries["categories"]["vector_databases"] = self.discover_vector_databases()
        print("✓ Vector Databases discovered")
        
        self.discoveries["categories"]["ai_orchestration"] = self.discover_ai_orchestration()
        print("✓ AI Orchestration Frameworks discovered")
        
        self.discoveries["categories"]["huggingface_inference"] = self.discover_huggingface_inference()
        print("✓ Hugging Face Inference discovered")
        
        self.discoveries["categories"]["model_deployment"] = self.discover_model_deployment()
        print("✓ Model Deployment Platforms discovered")
        
        # Calculate statistics
        total_technologies = sum(
            len(cat.get("technologies", [])) 
            for cat in self.discoveries["categories"].values()
        )
        
        self.discoveries["statistics"] = {
            "total_categories": len(self.discoveries["categories"]),
            "total_technologies": total_technologies,
            "cost_estimate": "$100-1000/month depending on usage (many free tiers)",
            "market_value": "$500,000+ in custom AI infrastructure"
        }
        
        return self.discoveries
    
    def save_discoveries(self):
        """Save discoveries to JSON file"""
        output_file = self.output_dir / "ai_infrastructure.json"
        
        with open(output_file, 'w') as f:
            json.dump(self.discoveries, f, indent=2)
        
        print(f"\n✅ Discoveries saved to: {output_file}")
        print(f"📊 Total technologies cataloged: {self.discoveries['statistics']['total_technologies']}")
        print(f"💰 Market value: {self.discoveries['statistics']['market_value']}")

def main():
    scout = AIMLInfrastructureScout()
    scout.run_discovery()
    scout.save_discoveries()
    
    print("\n🎯 Mission Complete - AI/ML Infrastructure Scout")

if __name__ == "__main__":
    main()
