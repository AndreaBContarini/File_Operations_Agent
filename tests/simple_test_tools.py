#!/usr/bin/env python3
"""Test semplice per verificare il miglioramento dell'error handling"""

import sys
from pathlib import Path

# Add the path of the project
sys.path.append(str(Path(__file__).parent.parent))

from agent.tool_registry import ToolRegistry

def test_tool_behavior():
    print("🔧 Testing ToolRegistry behavior...")
    
    tr = ToolRegistry('./test_files')
    
    # Test 1: File di testo normale
    print("\n✅ Reading normal text file:")
    try:
        result = tr.execute_tool('read_file', filename='hello.py')
        print(f"SUCCESS: Content length = {len(result)} chars")
        print(f"Preview: {result[:50]}...")
    except Exception as e:
        print(f"ERROR: {e}")
    
    # Test 2: File binario (PDF)
    print("\n📄 Reading binary PDF file:")
    try:
        result = tr.execute_tool('read_file', filename='test_binary.pdf')
        print(f"UNEXPECTED SUCCESS: {result}")
    except Exception as e:
        print(f"✅ EXPECTED ERROR (improved message): {e}")
    
    # Test 3: File non esistente
    print("\n❌ Reading non-existent file:")
    try:
        result = tr.execute_tool('read_file', filename='nonexistent.txt')
        print(f"UNEXPECTED SUCCESS: {result}")
    except Exception as e:
        print(f"✅ EXPECTED ERROR: {e}")

if __name__ == "__main__":
    test_tool_behavior() 