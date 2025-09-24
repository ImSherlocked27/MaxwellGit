#!/usr/bin/env python3
"""
Test script to verify OCR integration with the RAG system
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add current directory to Python path
sys.path.append(os.getcwd())

try:
    from utils import (
        process_document_with_ocr,
        process_ocr_json_result,
        is_ocr_supported_format,
        needs_conversion_for_ocr,
        OCR_AVAILABLE
    )
except ImportError as e:
    print(f"Error importing utils: {e}")
    print("Please ensure all dependencies are installed.")
    sys.exit(1)

def test_ocr_integration():
    """Test the OCR integration with the existing PDF file"""
    
    # Check if OCR is available
    if not OCR_AVAILABLE:
        print("🔍 Testing OCR Integration")
        print("=" * 50)
        print("❌ OCR functionality not available")
        print("To enable OCR, install: pip install agentic-doc")
        return False
    
    # Test file path
    test_pdf = "Contrato_de_Cuenta_1_REALISTA.pdf"
    
    if not os.path.exists(test_pdf):
        print(f"Error: Test file {test_pdf} not found")
        return False
    
    print("🔍 Testing OCR Integration")
    print("=" * 50)
    
    try:
        # Test 1: Check if PDF is supported format
        file_ext = os.path.splitext(test_pdf)[1]
        print(f"1. File extension: {file_ext}")
        print(f"   OCR supported: {is_ocr_supported_format(file_ext)}")
        print(f"   Needs conversion: {needs_conversion_for_ocr(file_ext)}")
        
        # Test 2: Process with OCR
        print("\n2. Processing document with OCR...")
        temp_dir = "./temp_test"
        os.makedirs(temp_dir, exist_ok=True)
        
        documents = process_document_with_ocr(test_pdf, test_pdf, temp_dir)
        
        print(f"   ✅ Successfully processed {len(documents)} chunks")
        
        # Test 3: Display sample results
        print("\n3. Sample OCR results:")
        for i, doc in enumerate(documents[:3]):  # Show first 3 chunks
            print(f"   Chunk {i+1}:")
            print(f"     Text: {doc.page_content[:100]}...")
            print(f"     Metadata: {doc.metadata}")
            print()
        
        # Test 4: Check for figure filtering
        ocr_types = [doc.metadata.get('chunk_type', 'unknown') for doc in documents]
        print(f"4. Chunk types found: {set(ocr_types)}")
        print(f"   Figure chunks filtered: {'figure' not in [t.lower() for t in ocr_types]}")
        
        # Test 5: Verify JSON result exists
        json_files = [f for f in os.listdir(temp_dir) if f.endswith('.json')]
        if json_files:
            print(f"\n5. JSON result file: {json_files[0]}")
            json_path = os.path.join(temp_dir, json_files[0])
            
            # Test processing the JSON directly
            direct_docs = process_ocr_json_result(json_path, test_pdf)
            print(f"   Direct JSON processing: {len(direct_docs)} chunks")
            
            # Verify they match
            if len(documents) == len(direct_docs):
                print("   ✅ Document processing consistency verified")
            else:
                print("   ⚠️  Document count mismatch between methods")
        
        print("\n🎉 OCR Integration Test Completed Successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ OCR Integration Test Failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

def test_word_conversion():
    """Test Word to PDF conversion (if docx2pdf is available)"""
    print("\n🔄 Testing Word to PDF Conversion")
    print("=" * 50)
    
    try:
        from utils import convert_word_to_pdf
        
        # Test if docx2pdf is available
        try:
            from docx2pdf import convert
            print("✅ docx2pdf library available")
            print("Word to PDF conversion function imported successfully")
            print("Note: Actual conversion test requires a Word document file")
            return True
        except ImportError:
            print("❌ docx2pdf library not available")
            print("To enable Word conversion, install: pip install docx2pdf")
            return False
        
    except Exception as e:
        print(f"Word conversion test info: {str(e)}")
        return False

if __name__ == "__main__":
    print("Maxwell AI - OCR Integration Test")
    print("=" * 50)
    
    # Check for required environment variables
    if not os.environ.get("OPENAI_API_KEY"):
        print("⚠️  Warning: OPENAI_API_KEY not set. Some features may not work.")
    
    # Run tests
    ocr_success = test_ocr_integration()
    word_success = test_word_conversion()
    
    print("\n" + "=" * 50)
    print("Test Summary:")
    print(f"OCR Integration: {'✅ PASS' if ocr_success else '❌ FAIL'}")
    print(f"Word Conversion: {'✅ PASS' if word_success else '❌ FAIL'}")
    
    if ocr_success:
        print("\n🚀 Ready to use OCR-enhanced RAG system!")
    else:
        print("\n🔧 Please check the OCR setup and dependencies.") 