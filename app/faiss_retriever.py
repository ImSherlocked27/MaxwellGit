#!/usr/bin/env python3
"""
FAISS-based retriever for Maxwell AI RAG system
Replaces BM25 retriever with Facebook's FAISS for fast vector similarity search
"""

import os
import numpy as np
import pickle
from typing import List, Optional, Dict, Any
from pathlib import Path

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    print("Warning: FAISS not available. Install with: pip install faiss-cpu")
    FAISS_AVAILABLE = False

from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_openai import OpenAIEmbeddings
from langchain_community.embeddings import HuggingFaceEmbeddings
from pydantic import Field


class FAISSRetriever(BaseRetriever):
    """
    FAISS-based retriever for fast vector similarity search.
    Replaces BM25 retriever with dense vector search using Facebook's FAISS.
    """
    
    # Define Pydantic fields
    documents: List[Document] = Field(description="List of documents to index")
    embeddings: Any = Field(description="Embedding model")
    k: int = Field(default=4, description="Number of documents to retrieve")
    index_type: str = Field(default="flat", description="FAISS index type")
    cache_dir: str = Field(default="./faiss_cache", description="Cache directory")
    collection_name: str = Field(default="default", description="Collection name")
    
    # Non-Pydantic fields (initialized after construction)
    index: Optional[Any] = Field(default=None, init=False)
    document_embeddings: Optional[np.ndarray] = Field(default=None, init=False)
    
    class Config:
        arbitrary_types_allowed = True
    
    def __init__(self, **kwargs):
        """Initialize FAISS retriever."""
        super().__init__(**kwargs)
        
        if not FAISS_AVAILABLE:
            raise ImportError("FAISS not available. Install with: pip install faiss-cpu")
        
        # Convert cache_dir to Path object
        self.cache_dir = Path(self.cache_dir)
        
        # Ensure cache directory exists
        self.cache_dir.mkdir(exist_ok=True)
        
        # Initialize FAISS index
        self.index = None
        self.document_embeddings = None
        self._build_or_load_index()
    
    def _get_cache_paths(self):
        """Get paths for cached index and embeddings"""
        base_path = self.cache_dir / f"{self.collection_name}"
        return {
            'index': f"{base_path}_faiss.index",
            'embeddings': f"{base_path}_embeddings.pkl",
            'documents': f"{base_path}_documents.pkl"
        }
    
    def _build_or_load_index(self):
        """Build FAISS index or load from cache"""
        cache_paths = self._get_cache_paths()
        
        # Check if cached index exists
        if (os.path.exists(cache_paths['index']) and 
            os.path.exists(cache_paths['embeddings']) and
            os.path.exists(cache_paths['documents'])):
            
            print(f"Loading cached FAISS index for collection '{self.collection_name}'...")
            self._load_index(cache_paths)
        else:
            print(f"Building new FAISS index for collection '{self.collection_name}'...")
            self._build_index()
            self._save_index(cache_paths)
    
    def _build_index(self):
        """Build FAISS index from documents"""
        if not self.documents:
            raise ValueError("No documents provided for indexing")
        
        print(f"Generating embeddings for {len(self.documents)} documents...")
        
        # Extract text content from documents
        texts = [doc.page_content for doc in self.documents]
        
        # Generate embeddings
        self.document_embeddings = np.array(self.embeddings.embed_documents(texts))
        
        # Get embedding dimension
        embedding_dim = self.document_embeddings.shape[1]
        
        print(f"Embedding dimension: {embedding_dim}")
        print(f"Building {self.index_type.upper()} index...")
        
        # Create FAISS index based on type
        if self.index_type == "flat":
            # Exact search using L2 distance
            self.index = faiss.IndexFlatL2(embedding_dim)
        elif self.index_type == "ivf":
            # Inverted file index for faster approximate search
            nlist = max(1, min(100, len(self.documents) // 10))  # Number of clusters (at least 1)
            quantizer = faiss.IndexFlatL2(embedding_dim)
            self.index = faiss.IndexIVFFlat(quantizer, embedding_dim, nlist)
            # Train the index
            self.index.train(self.document_embeddings)
            # Set nprobe for search (number of clusters to search)
            self.index.nprobe = min(nlist, 10)
        elif self.index_type == "hnsw":
            # Hierarchical Navigable Small World for very fast approximate search
            self.index = faiss.IndexHNSWFlat(embedding_dim, 32)
            self.index.hnsw.efConstruction = 40
        else:
            raise ValueError(f"Unsupported index type: {self.index_type}")
        
        # Add vectors to index
        self.index.add(self.document_embeddings)
        
        print(f"FAISS index built successfully with {self.index.ntotal} vectors")
    
    def _save_index(self, cache_paths):
        """Save FAISS index and metadata to cache"""
        try:
            # Save FAISS index
            faiss.write_index(self.index, cache_paths['index'])
            
            # Save embeddings
            with open(cache_paths['embeddings'], 'wb') as f:
                pickle.dump(self.document_embeddings, f)
            
            # Save documents
            with open(cache_paths['documents'], 'wb') as f:
                pickle.dump(self.documents, f)
            
            print(f"FAISS index cached successfully")
            
        except Exception as e:
            print(f"Warning: Could not cache FAISS index: {e}")
    
    def _load_index(self, cache_paths):
        """Load FAISS index and metadata from cache"""
        try:
            # Load FAISS index
            self.index = faiss.read_index(cache_paths['index'])
            
            # Load embeddings
            with open(cache_paths['embeddings'], 'rb') as f:
                self.document_embeddings = pickle.load(f)
            
            # Load documents
            with open(cache_paths['documents'], 'rb') as f:
                cached_documents = pickle.load(f)
            
            # Verify document consistency
            if len(cached_documents) != len(self.documents):
                print("Warning: Cached documents don't match current documents. Rebuilding index...")
                self._build_index()
                self._save_index(cache_paths)
            else:
                self.documents = cached_documents
                print(f"FAISS index loaded successfully with {self.index.ntotal} vectors")
            
        except Exception as e:
            print(f"Warning: Could not load cached FAISS index: {e}")
            print("Rebuilding index...")
            self._build_index()
            self._save_index(cache_paths)
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Retrieve relevant documents using FAISS similarity search"""
        if not self.index:
            raise ValueError("FAISS index not initialized")
        
        # Generate query embedding
        query_embedding = np.array([self.embeddings.embed_query(query)])
        
        # Search for similar vectors
        scores, indices = self.index.search(query_embedding, self.k)
        
        # Get relevant documents
        relevant_docs = []
        for i, (score, idx) in enumerate(zip(scores[0], indices[0])):
            if idx < len(self.documents):  # Valid index
                doc = self.documents[idx]
                # Add similarity score to metadata
                doc_copy = Document(
                    page_content=doc.page_content,
                    metadata={
                        **doc.metadata,
                        'faiss_score': float(score),
                        'faiss_rank': i + 1
                    }
                )
                relevant_docs.append(doc_copy)
        
        return relevant_docs
    
    @classmethod
    def from_documents(
        cls,
        documents: List[Document],
        embeddings,
        **kwargs
    ) -> "FAISSRetriever":
        """Create FAISS retriever from documents"""
        return cls(documents=documents, embeddings=embeddings, **kwargs)
    
    def clear_cache(self):
        """Clear cached FAISS index"""
        cache_paths = self._get_cache_paths()
        for path in cache_paths.values():
            if os.path.exists(path):
                os.remove(path)
        print(f"FAISS cache cleared for collection '{self.collection_name}'")
    
    def get_index_stats(self) -> Dict[str, Any]:
        """Get statistics about the FAISS index"""
        if not self.index:
            return {"status": "not_initialized"}
        
        return {
            "status": "initialized",
            "index_type": self.index_type,
            "total_vectors": self.index.ntotal,
            "embedding_dim": self.document_embeddings.shape[1] if self.document_embeddings is not None else 0,
            "documents_count": len(self.documents),
            "cache_dir": str(self.cache_dir),
            "collection_name": self.collection_name
        }


class HybridFAISSRetriever(BaseRetriever):
    """
    Hybrid retriever that combines FAISS vector search with ChromaDB vector search.
    Provides ensemble-like functionality with pure vector-based approaches.
    """
    
    # Define Pydantic fields
    faiss_retriever: FAISSRetriever = Field(description="FAISS-based retriever")
    chroma_retriever: Any = Field(description="ChromaDB-based retriever")
    weights: List[float] = Field(default=[0.5, 0.5], description="Weights for combining results")
    k: int = Field(default=4, description="Number of documents to retrieve")
    
    class Config:
        arbitrary_types_allowed = True
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """Retrieve documents using hybrid FAISS + ChromaDB approach"""
        
        # Get results from both retrievers
        faiss_docs = self.faiss_retriever._get_relevant_documents(query, run_manager=run_manager)
        chroma_docs = self.chroma_retriever.get_relevant_documents(query)
        
        # Combine and deduplicate results
        seen_content = set()
        combined_docs = []
        
        # Process FAISS results
        for doc in faiss_docs[:self.k]:
            content_hash = hash(doc.page_content)
            if content_hash not in seen_content:
                doc.metadata['retriever_source'] = 'faiss'
                doc.metadata['retriever_weight'] = self.weights[0]
                combined_docs.append(doc)
                seen_content.add(content_hash)
        
        # Process ChromaDB results
        for doc in chroma_docs[:self.k]:
            content_hash = hash(doc.page_content)
            if content_hash not in seen_content:
                doc.metadata['retriever_source'] = 'chroma'
                doc.metadata['retriever_weight'] = self.weights[1]
                combined_docs.append(doc)
                seen_content.add(content_hash)
        
        # Return top k results
        return combined_docs[:self.k]


def create_faiss_retriever(
    documents: List[Document],
    embeddings,
    k: int = 4,
    index_type: str = "flat",
    collection_name: str = "default"
) -> FAISSRetriever:
    """
    Create a FAISS retriever with the specified configuration.
    
    Args:
        documents: Documents to index
        embeddings: Embedding model
        k: Number of documents to retrieve
        index_type: FAISS index type ("flat", "ivf", "hnsw")
        collection_name: Collection name for caching
    
    Returns:
        Configured FAISS retriever
    """
    if not FAISS_AVAILABLE:
        raise ImportError("FAISS not available. Install with: pip install faiss-cpu")
    
    return FAISSRetriever(
        documents=documents,
        embeddings=embeddings,
        k=k,
        index_type=index_type,
        collection_name=collection_name
    )


def get_optimal_index_type(num_documents: int) -> str:
    """
    Get optimal FAISS index type based on number of documents.
    
    Args:
        num_documents: Number of documents to index
    
    Returns:
        Recommended index type
    """
    if num_documents < 1000:
        return "flat"  # Exact search for small collections
    elif num_documents < 10000:
        return "ivf"   # IVF for medium collections
    else:
        return "hnsw"  # HNSW for large collections 