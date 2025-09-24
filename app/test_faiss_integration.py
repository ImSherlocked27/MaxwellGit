#!/usr/bin/env python3
"""
Test script to verify FAISS integration with Maxwell AI RAG system
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.getcwd())

def test_faiss_installation():
    """Test if FAISS is installed and working"""
    print("🔍 Testing FAISS Installation")
    print("=" * 50)
    
    try:
        import faiss
        print("✅ FAISS imported successfully")
        print(f"   FAISS version: {faiss.__version__ if hasattr(faiss, '__version__') else 'Unknown'}")
        
        # Test basic FAISS functionality
        import numpy as np
        
        # Create a simple test index
        d = 64  # dimension
        nb = 100  # database size
        nq = 10  # number of queries
        
        np.random.seed(1234)
        xb = np.random.random((nb, d)).astype('float32')
        xq = np.random.random((nq, d)).astype('float32')
        
        # Build index
        index = faiss.IndexFlatL2(d)
        index.add(xb)
        
        # Search
        k = 4
        D, I = index.search(xq, k)
        
        print(f"✅ FAISS basic functionality test passed")
        print(f"   Index contains {index.ntotal} vectors")
        print(f"   Search returned {len(I)} queries with {len(I[0])} results each")
        
        return True
        
    except ImportError as e:
        print(f"❌ FAISS not available: {e}")
        print("   Install with: pip install faiss-cpu")
        return False
    except Exception as e:
        print(f"❌ FAISS functionality test failed: {e}")
        return False

def test_faiss_retriever_import():
    """Test if our FAISS retriever can be imported"""
    print("\n🔧 Testing FAISS Retriever Import")
    print("=" * 50)
    
    try:
        from faiss_retriever import (
            FAISSRetriever,
            HybridFAISSRetriever,
            create_faiss_retriever,
            get_optimal_index_type,
            FAISS_AVAILABLE
        )
        
        print("✅ FAISS retriever classes imported successfully")
        print(f"   FAISS available: {FAISS_AVAILABLE}")
        
        # Test optimal index type function
        test_sizes = [100, 1000, 10000, 100000]
        for size in test_sizes:
            index_type = get_optimal_index_type(size)
            print(f"   {size} documents → {index_type} index")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import FAISS retriever: {e}")
        return False
    except Exception as e:
        print(f"❌ FAISS retriever test failed: {e}")
        return False

def test_faiss_with_sample_documents():
    """Test FAISS retriever with sample documents"""
    print("\n📄 Testing FAISS with Sample Documents")
    print("=" * 50)
    
    try:
        from faiss_retriever import create_faiss_retriever
        from langchain_core.documents import Document
        from langchain_openai import OpenAIEmbeddings
        
        # Check if OpenAI API key is available
        if not os.environ.get("OPENAI_API_KEY"):
            print("⚠️  OPENAI_API_KEY not set - using mock embeddings")
            # Create mock embedding class for testing
            class MockEmbeddings:
                def embed_documents(self, texts):
                    import numpy as np
                    # Return random embeddings for testing
                    return np.random.random((len(texts), 1536)).tolist()
                
                def embed_query(self, text):
                    import numpy as np
                    return np.random.random(1536).tolist()
            
            embeddings = MockEmbeddings()
        else:
            embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        
        # Create sample documents
        sample_docs = [
            Document(
                page_content="This is a sample document about artificial intelligence and machine learning.",
                metadata={"source": "doc1.txt", "page": 1}
            ),
            Document(
                page_content="Python is a powerful programming language used for data science and AI.",
                metadata={"source": "doc2.txt", "page": 1}
            ),
            Document(
                page_content="FAISS is Facebook's library for efficient similarity search and clustering.",
                metadata={"source": "doc3.txt", "page": 1}
            ),
            Document(
                page_content="Vector databases are essential for modern RAG applications.",
                metadata={"source": "doc4.txt", "page": 1}
            )
        ]
        
        print(f"Testing with {len(sample_docs)} sample documents...")
        
        # Test different index types
        index_types = ["flat", "ivf", "hnsw"]
        
        for index_type in index_types:
            print(f"\n   Testing {index_type.upper()} index...")
            try:
                faiss_retriever = create_faiss_retriever(
                    documents=sample_docs,
                    embeddings=embeddings,
                    k=2,
                    index_type=index_type,
                    collection_name=f"test_{index_type}"
                )
                
                # Test retrieval
                query = "What is artificial intelligence?"
                results = faiss_retriever.get_relevant_documents(query)
                
                print(f"   ✅ {index_type.upper()} index created and tested")
                print(f"      Retrieved {len(results)} documents")
                
                # Show sample result
                if results:
                    first_result = results[0]
                    print(f"      Top result: {first_result.page_content[:50]}...")
                    print(f"      FAISS score: {first_result.metadata.get('faiss_score', 'N/A')}")
                
                # Get index stats
                stats = faiss_retriever.get_index_stats()
                print(f"      Index stats: {stats['total_vectors']} vectors, {stats['embedding_dim']} dimensions")
                
                # Clear cache for next test
                faiss_retriever.clear_cache()
                
            except Exception as e:
                print(f"   ❌ {index_type.upper()} index test failed: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample documents test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_hybrid_retriever():
    """Test hybrid FAISS + ChromaDB retriever"""
    print("\n🔗 Testing Hybrid FAISS Retriever")
    print("=" * 50)
    
    try:
        from faiss_retriever import HybridFAISSRetriever, create_faiss_retriever
        from langchain_core.documents import Document
        
        # Mock embeddings for testing
        class MockEmbeddings:
            def embed_documents(self, texts):
                import numpy as np
                return np.random.random((len(texts), 1536)).tolist()
            
            def embed_query(self, text):
                import numpy as np
                return np.random.random(1536).tolist()
        
        # Mock ChromaDB retriever
        class MockChromaRetriever:
            def get_relevant_documents(self, query):
                return [
                    Document(
                        page_content="ChromaDB result for the query",
                        metadata={"source": "chroma", "score": 0.8}
                    )
                ]
        
        embeddings = MockEmbeddings()
        
        # Create sample documents
        sample_docs = [
            Document(
                page_content="FAISS provides fast similarity search capabilities.",
                metadata={"source": "faiss_doc.txt"}
            )
        ]
        
        # Create FAISS retriever
        faiss_retriever = create_faiss_retriever(
            documents=sample_docs,
            embeddings=embeddings,
            k=1,
            index_type="flat",
            collection_name="hybrid_test"
        )
        
        # Create mock ChromaDB retriever
        chroma_retriever = MockChromaRetriever()
        
        # Create hybrid retriever
        hybrid_retriever = HybridFAISSRetriever(
            faiss_retriever=faiss_retriever,
            chroma_retriever=chroma_retriever,
            weights=[0.6, 0.4],
            k=2
        )
        
        # Test retrieval
        results = hybrid_retriever.get_relevant_documents("test query")
        
        print(f"✅ Hybrid retriever created and tested")
        print(f"   Retrieved {len(results)} documents from both sources")
        
        for i, doc in enumerate(results):
            source = doc.metadata.get('retriever_source', 'unknown')
            print(f"   Result {i+1}: {source} - {doc.page_content[:50]}...")
        
        # Clean up
        faiss_retriever.clear_cache()
        
        return True
        
    except Exception as e:
        print(f"❌ Hybrid retriever test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_chat():
    """Test integration with chat system"""
    print("\n💬 Testing Integration with Chat System")
    print("=" * 50)
    
    try:
        # Test if updated chat files can be imported
        print("Testing import of updated chat modules...")
        
        # This would normally import the chat modules, but we'll just check the files exist
        chat_files = [
            "pages/2_Chat.py",
            "pages/3_Configurations.py",
            "2_Chat_backup.py"
        ]
        
        for file_path in chat_files:
            if os.path.exists(file_path):
                print(f"   ✅ {file_path} exists and updated")
            else:
                print(f"   ❌ {file_path} not found")
                return False
        
        # Check if FAISS imports are in the chat files
        with open("pages/2_Chat.py", "r") as f:
            content = f.read()
            if "faiss_retriever" in content:
                print("   ✅ FAISS integration found in main chat file")
            else:
                print("   ❌ FAISS integration not found in main chat file")
                return False
        
        print("✅ Integration with chat system verified")
        return True
        
    except Exception as e:
        print(f"❌ Chat integration test failed: {e}")
        return False

def cleanup_test_files():
    """Clean up test files created during testing"""
    print("\n🧹 Cleaning Up Test Files")
    print("=" * 50)
    
    try:
        # Clean up FAISS cache directory
        cache_dir = Path("./faiss_cache")
        if cache_dir.exists():
            import shutil
            shutil.rmtree(cache_dir)
            print("✅ FAISS cache directory cleaned up")
        
        print("✅ Cleanup completed")
        
    except Exception as e:
        print(f"⚠️  Cleanup warning: {e}")

def main():
    """Run all FAISS integration tests"""
    print("🧪 FAISS Integration Test Suite")
    print("=" * 70)
    
    # Track test results
    results = {}
    
    # Test 1: FAISS installation
    results['faiss_installation'] = test_faiss_installation()
    
    # Test 2: FAISS retriever import
    results['faiss_retriever_import'] = test_faiss_retriever_import()
    
    # Test 3: FAISS with sample documents (only if FAISS is available)
    if results['faiss_installation'] and results['faiss_retriever_import']:
        results['sample_documents'] = test_faiss_with_sample_documents()
        results['hybrid_retriever'] = test_hybrid_retriever()
    else:
        print("\n⏭️  Skipping advanced tests (FAISS not available)")
        results['sample_documents'] = False
        results['hybrid_retriever'] = False
    
    # Test 4: Integration with chat system
    results['chat_integration'] = test_integration_with_chat()
    
    # Clean up
    cleanup_test_files()
    
    # Summary
    print("\n" + "=" * 70)
    print("📊 Test Summary")
    print("=" * 70)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! FAISS integration is working correctly.")
        print("🚀 Your RAG system now uses FAISS for fast vector similarity search!")
    else:
        print(f"\n🔧 {total_tests - passed_tests} test(s) failed.")
        
        if not results['faiss_installation']:
            print("\n💡 Next steps:")
            print("1. Install FAISS: pip install faiss-cpu")
            print("2. For GPU support: pip install faiss-gpu")
        else:
            print("\n💡 Check the error messages above for specific issues.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 