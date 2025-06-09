#!/usr/bin/env python3
"""Test end-to-end del comportamento migliorato per file binari"""

import sys
from pathlib import Path
import pytest

# Add the path of the project
sys.path.append(str(Path(__file__).parent.parent))

from agent.llm_agent import LLMFileAgent
import asyncio
import os

@pytest.mark.asyncio
async def test_binary_file_handling():
    print("🧪 Testing improved binary file handling...")
    
    agent = LLMFileAgent('./test_files', 'fake-key', verbose=False)
    
    # Test 1: PDF file
    print("\n1️⃣ Testing PDF file:")
    try:
        result = await agent.process_query('read test_binary.pdf')
        print('✅ Success:', result.get('message', 'No message')[:100] + '...')
    except Exception as e:
        print('❌ Error:', str(e))
    
    # Test 2: Normal text file
    print("\n2️⃣ Testing normal text file:")
    try:
        result = await agent.process_query('read hello.py')
        print('✅ Success:', result.get('message', 'No message')[:100] + '...')
    except Exception as e:
        print('❌ Error:', str(e))
    
    # Test 3: File analysis with improved error handling
    print("\n3️⃣ Testing file analysis of PDF:")
    try:
        result = await agent.process_query('cosa fa test_binary.pdf?')
        print('✅ Success:', result.get('message', 'No message')[:150] + '...')
    except Exception as e:
        print('❌ Error:', str(e))

if __name__ == "__main__":
    asyncio.run(test_binary_file_handling()) 