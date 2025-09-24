#!/usr/bin/env python3
"""
Test script to verify agentic_doc installation and functionality
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_agentic_doc_import():
    """Test if agentic_doc can be imported successfully"""
    print("📦 Testing agentic_doc Import")
    print("=" * 40)
    
    try:
        from agentic_doc.parse import parse
        print("✅ agentic_doc.parse imported successfully")
        return True, parse
    except ImportError as e:
        print(f"❌ Failed to import agentic_doc: {e}")
        print("Install with: pip install agentic-doc")
        return False, None

def test_environment_variables():
    """Test if required environment variables are set"""
    print("\n🔐 Testing Environment Variables")
    print("=" * 40)
    
    required_vars = ["OPENAI_API_KEY"]
    all_set = True
    
    for var in required_vars:
        if os.environ.get(var):
            print(f"✅ {var} is set")
        else:
            print(f"❌ {var} is not set")
            all_set = False
    
    if not all_set:
        print("\n💡 To set environment variables:")
        print("Create a .env file with:")
        print("OPENAI_API_KEY=your_openai_api_key_here")
    
    return all_set

def test_parse_function():
    """Test the parse function from utils.py"""
    print("\n🔧 Testing OCR Parse Function")
    print("=" * 40)
    
    try:
        # Import the function from utils.py
        sys.path.append(os.getcwd())
        from utils import parse_pdf_document
        print("✅ parse_pdf_document function imported successfully")
        return True
    except ImportError as e:
        print(f"❌ Failed to import parse_pdf_document: {e}")
        return False

def test_pdf_processing():
    """Test actual PDF processing with the sample file"""
    print("\n📄 Testing PDF Processing")
    print("=" * 40)
    
    # Check if sample PDF exists
    test_pdf = "Contrato_de_Cuenta_1_REALISTA.pdf"
    
    if not os.path.exists(test_pdf):
        print(f"❌ Test file {test_pdf} not found")
        print("This test requires the sample PDF file")
        return False
    
    print(f"✅ Test file {test_pdf} found")
    
    # Test environment variables first
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  OPENAI_API_KEY not set - OCR may not work fully")
        print("Set your API key in .env file for complete testing")
        return False
    
    try:
        # Import and test the function
        from utils import parse_pdf_document
        
        print(f"🔄 Processing {test_pdf} with agentic_doc...")
        
        # Create temp directory for results
        temp_dir = "./temp_agentic_test"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Process the PDF
        result = parse_pdf_document(test_pdf, temp_dir)
        
        print("✅ PDF processing completed successfully")
        
        # Check if JSON result was created
        json_files = [f for f in os.listdir(temp_dir) if f.endswith('.json')]
        
        if json_files:
            json_file = json_files[0]
            json_path = os.path.join(temp_dir, json_file)
            
            print(f"✅ JSON result created: {json_file}")
            
            # Analyze the JSON content
            import json
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            chunks = data.get('chunks', [])
            print(f"✅ Found {len(chunks)} chunks in result")
            
            # Check chunk types
            chunk_types = [chunk.get('chunk_type', 'unknown') for chunk in chunks]
            unique_types = set(chunk_types)
            print(f"✅ Chunk types found: {unique_types}")
            
            # Check for figure filtering capability
            figure_count = sum(1 for ct in chunk_types if ct.lower() == 'figure')
            text_count = sum(1 for ct in chunk_types if ct.lower() != 'figure')
            
            print(f"📊 Content breakdown:")
            print(f"   - Text chunks: {text_count}")
            print(f"   - Figure chunks: {figure_count}")
            
            if text_count > 0:
                print("✅ Text chunks available for RAG processing")
            
            # Show sample chunk
            text_chunks = [chunk for chunk in chunks if chunk.get('chunk_type', '').lower() != 'figure']
            if text_chunks:
                sample = text_chunks[0]
                sample_text = sample.get('text', '')[:100]
                print(f"📝 Sample text: {sample_text}...")
            
            return True
        else:
            print("❌ No JSON result file created")
            return False
            
    except Exception as e:
        print(f"❌ PDF processing failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_integration_with_rag():
    """Test integration with RAG workflow"""
    print("\n🔗 Testing RAG Integration")
    print("=" * 40)
    
    try:
        from utils import (
            process_ocr_json_result,
            is_ocr_supported_format,
            needs_conversion_for_ocr
        )
        
        print("✅ OCR utility functions imported successfully")
        
        # Test format detection
        pdf_supported = is_ocr_supported_format('.pdf')
        docx_needs_conversion = needs_conversion_for_ocr('.docx')
        
        print(f"✅ PDF OCR support: {pdf_supported}")
        print(f"✅ DOCX needs conversion: {docx_needs_conversion}")
        
        # Test JSON processing if we have a result file
        temp_dir = "./temp_agentic_test"
        if os.path.exists(temp_dir):
            json_files = [f for f in os.listdir(temp_dir) if f.endswith('.json')]
            if json_files:
                json_path = os.path.join(temp_dir, json_files[0])
                
                print(f"🔄 Testing JSON processing with {json_files[0]}...")
                documents = process_ocr_json_result(json_path, "test.pdf")
                
                print(f"✅ Processed {len(documents)} document chunks")
                
                # Verify figure filtering
                chunk_types = [doc.metadata.get('chunk_type', '') for doc in documents]
                has_figures = any(ct.lower() == 'figure' for ct in chunk_types)
                
                if not has_figures:
                    print("✅ Figure chunks successfully filtered out")
                else:
                    print("⚠️  Figure chunks still present (check filtering logic)")
                
                return True
        
        print("✅ RAG integration functions ready")
        return True
        
    except Exception as e:
        print(f"❌ RAG integration test failed: {str(e)}")
        return False

def cleanup_test_files():
    """Clean up temporary test files"""
    print("\n🧹 Cleaning Up Test Files")
    print("=" * 40)
    
    temp_dir = "./temp_agentic_test"
    if os.path.exists(temp_dir):
        import shutil
        try:
            shutil.rmtree(temp_dir)
            print("✅ Temporary test files cleaned up")
        except Exception as e:
            print(f"⚠️  Could not clean up temp files: {e}")

def main():
    """Run all tests"""
    print("🧪 agentic_doc Installation & Functionality Test")
    print("=" * 60)
    
    # Track test results
    results = {}
    
    # Test 1: Import
    results['import'], parse_func = test_agentic_doc_import()
    
    # Test 2: Environment
    results['environment'] = test_environment_variables()
    
    # Test 3: Parse function
    results['parse_function'] = test_parse_function()
    
    # Test 4: PDF processing (only if previous tests pass)
    if results['import'] and results['environment'] and results['parse_function']:
        results['pdf_processing'] = test_pdf_processing()
    else:
        print("\n📄 Skipping PDF processing test (prerequisites not met)")
        results['pdf_processing'] = False
    
    # Test 5: RAG integration
    results['rag_integration'] = test_integration_with_rag()
    
    # Clean up
    cleanup_test_files()
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 Test Summary")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name.replace('_', ' ').title()}: {status}")
    
    total_tests = len(results)
    passed_tests = sum(results.values())
    
    print(f"\nOverall: {passed_tests}/{total_tests} tests passed")
    
    if passed_tests == total_tests:
        print("\n🎉 All tests passed! agentic_doc is correctly installed and working.")
        print("🚀 Your OCR integration is ready for use!")
    else:
        print(f"\n🔧 {total_tests - passed_tests} test(s) failed. Please check the issues above.")
        
        if not results['import']:
            print("\n💡 Next steps:")
            print("1. Install agentic_doc: pip install agentic-doc")
        elif not results['environment']:
            print("\n💡 Next steps:")
            print("1. Set OPENAI_API_KEY in .env file")
        else:
            print("\n💡 Check the error messages above for specific issues.")
    
    return passed_tests == total_tests

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 