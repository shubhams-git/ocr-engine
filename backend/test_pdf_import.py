#!/usr/bin/env python3
"""
Test script to verify PDF processing imports work correctly
"""
import sys

def test_imports():
    """Test all imports"""
    print("🧪 Testing PDF Processing Imports")
    print("=" * 40)
    
    # Test basic imports
    try:
        from app.utils.file_utils import PDFProcessor, ImageProcessor, FileValidator
        print("✅ File utilities imported successfully")
    except Exception as e:
        print(f"❌ File utilities import failed: {e}")
        return False
    
    # Test PDF processor specifically
    try:
        processor = PDFProcessor()
        print("✅ PDFProcessor instantiated successfully")
    except Exception as e:
        print(f"❌ PDFProcessor instantiation failed: {e}")
        return False
    
    # Test PyMuPDF import
    try:
        import fitz
        print(f"✅ PyMuPDF imported (version: {fitz.version})")
    except Exception as e:
        print(f"❌ PyMuPDF import failed: {e}")
        return False
    
    # Test PIL import
    try:
        from PIL import Image
        print("✅ PIL/Pillow imported successfully")
    except Exception as e:
        print(f"❌ PIL import failed: {e}")
        return False
    
    print("=" * 40)
    print("🎉 All imports working correctly!")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1) 