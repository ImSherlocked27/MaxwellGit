#!/usr/bin/env python3
"""
Installation and test script for OCR dependencies
"""

import subprocess
import sys
import os

def install_dependencies():
    """Install required OCR dependencies"""
    
    print("📦 Installing OCR Dependencies")
    print("=" * 50)
    
    dependencies = [
        "agentic-doc",
        "docx2pdf", 
        "pathlib2",
        "python-dotenv"
    ]
    
    success = True
    
    for dep in dependencies:
        print(f"\n🔄 Installing {dep}...")
        try:
            result = subprocess.run([
                sys.executable, "-m", "pip", "install", dep
            ], capture_output=True, text=True, check=True)
            
            print(f"✅ {dep} installed successfully")
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to install {dep}")
            print(f"   Error: {e.stderr}")
            success = False
        except Exception as e:
            print(f"❌ Unexpected error installing {dep}: {e}")
            success = False
    
    return success

def test_installation():
    """Test the installed dependencies"""
    
    print("\n🧪 Testing Installation")
    print("=" * 50)
    
    # Test agentic_doc
    print("\n1️⃣ Testing agentic_doc...")
    try:
        from agentic_doc.parse import parse
        print("✅ agentic_doc imported successfully")
    except ImportError as e:
        print(f"❌ agentic_doc import failed: {e}")
        return False
    
    # Test docx2pdf
    print("\n2️⃣ Testing docx2pdf...")
    try:
        from docx2pdf import convert
        print("✅ docx2pdf imported successfully")
    except ImportError as e:
        print(f"❌ docx2pdf import failed: {e}")
        return False
    
    # Test our wrapper function
    print("\n3️⃣ Testing wrapper functions...")
    try:
        from utils import parse_pdf_document, convert_word_to_pdf
        print("✅ Wrapper functions imported successfully")
    except ImportError as e:
        print(f"❌ Wrapper function import failed: {e}")
        return False
    
    print("\n✅ All tests passed!")
    return True

def create_env_template():
    """Create a .env template file if it doesn't exist"""
    
    print("\n📝 Setting up environment file...")
    
    env_file = ".env"
    
    if not os.path.exists(env_file):
        with open(env_file, 'w') as f:
            f.write("# Maxwell AI Environment Variables\n")
            f.write("# Replace 'your_openai_api_key_here' with your actual OpenAI API key\n")
            f.write("OPENAI_API_KEY=your_openai_api_key_here\n")
        
        print(f"✅ Created {env_file} template")
        print("   Please edit it and add your OpenAI API key")
    else:
        print(f"✅ {env_file} already exists")

def show_success_message():
    """Show success message and next steps"""
    
    print("\n🎉 OCR Installation Complete!")
    print("=" * 50)
    print("✅ agentic_doc installed and working")
    print("✅ docx2pdf installed and working") 
    print("✅ All wrapper functions ready")
    print("✅ Environment template created")
    
    print("\n📋 Next Steps:")
    print("1. Edit the .env file and add your OpenAI API key")
    print("2. Run: python test_agentic_doc.py (for full testing)")
    print("3. Start Maxwell AI: streamlit run app.py")
    print("4. Use the OCR checkbox when uploading documents!")
    
    print("\n🚀 Your OCR-enhanced RAG system is ready!")

def main():
    """Main installation and test workflow"""
    
    print("Maxwell AI - OCR Installation & Test Script")
    print("=" * 60)
    
    # Step 1: Install dependencies
    if not install_dependencies():
        print("\n❌ Installation failed. Please check the errors above.")
        return False
    
    # Step 2: Test installation
    if not test_installation():
        print("\n❌ Testing failed. Please check the errors above.")
        return False
    
    # Step 3: Create environment template
    create_env_template()
    
    # Step 4: Show success message
    show_success_message()
    
    return True

if __name__ == "__main__":
    success = main()
    
    if not success:
        print("\n🔧 Installation incomplete. Please resolve the issues above.")
        sys.exit(1)
    else:
        print("\n✨ Installation successful!")
        sys.exit(0) 