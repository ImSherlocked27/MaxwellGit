#!/usr/bin/env python3
"""
Simple test script to verify agentic_doc installation
"""

import sys

def test_agentic_doc_installation():
    """Test if agentic_doc is correctly installed"""
    
    print("🧪 Testing agentic_doc Installation")
    print("=" * 50)
    
    # Test 1: Basic import
    print("\n1️⃣ Testing basic import...")
    try:
        import agentic_doc
        print("✅ agentic_doc package imported successfully")
        print(f"   Package location: {agentic_doc.__file__}")
    except ImportError as e:
        print(f"❌ Failed to import agentic_doc: {e}")
        print("   Install with: pip install agentic-doc")
        return False
    
    # Test 2: Parse function import
    print("\n2️⃣ Testing parse function import...")
    try:
        from agentic_doc.parse import parse
        print("✅ parse function imported successfully")
        print(f"   Function: {parse}")
    except ImportError as e:
        print(f"❌ Failed to import parse function: {e}")
        return False
    
    # Test 3: Check package version (if available)
    print("\n3️⃣ Checking package information...")
    try:
        version = getattr(agentic_doc, '__version__', 'Unknown')
        print(f"✅ agentic_doc version: {version}")
    except:
        print("⚠️  Version information not available")
    
    # Test 4: Test our wrapper function
    print("\n4️⃣ Testing our wrapper function...")
    try:
        import os
        sys.path.append(os.getcwd())
        from utils import parse_pdf_document
        print("✅ parse_pdf_document wrapper function imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import wrapper function: {e}")
        print(f"   Error details: {e}")
        return False
    
    print("\n🎉 All installation tests passed!")
    print("✅ agentic_doc is correctly installed and ready to use")
    
    return True

def show_next_steps():
    """Show what to do after successful installation"""
    
    print("\n📋 Next Steps:")
    print("=" * 30)
    print("1. Set up your OpenAI API key in a .env file:")
    print("   OPENAI_API_KEY=your_api_key_here")
    print("")
    print("2. Test with a PDF document:")
    print("   python test_agentic_doc.py")
    print("")
    print("3. Use the OCR feature in the Maxwell AI interface:")
    print("   - Upload PDF, DOCX, PNG, or JPEG files")
    print("   - Check the 'OCR avanzado' option")
    print("   - Process your documents!")
    
def show_installation_help():
    """Show installation help if tests fail"""
    
    print("\n🔧 Installation Help:")
    print("=" * 30)
    print("1. Install agentic_doc:")
    print("   pip install agentic-doc")
    print("")
    print("2. If you get permission errors on Windows:")
    print("   pip install --user agentic-doc")
    print("")
    print("3. If you're using a virtual environment:")
    print("   Make sure it's activated before installing")
    print("")
    print("4. For other issues, try:")
    print("   pip install --upgrade pip")
    print("   pip install agentic-doc")

def main():
    """Run the simple installation test"""
    
    print("Maxwell AI - agentic_doc Installation Test")
    print("=" * 60)
    
    success = test_agentic_doc_installation()
    
    if success:
        show_next_steps()
        print("\n🚀 Ready to use OCR functionality!")
    else:
        show_installation_help()
        print("\n❌ Please install agentic_doc and try again")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 