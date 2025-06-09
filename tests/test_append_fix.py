#!/usr/bin/env python3
"""
Test script per verificare che il fix dell'append multiplo funzioni.
"""
import asyncio
import os
import sys
from pathlib import Path
import pytest

# Add the path of the project
sys.path.append(str(Path(__file__).parent.parent))

from agent import LLMFileAgent

@pytest.mark.asyncio
async def test_append_single():
    """Test che l'append avvenga una sola volta."""
    
    # Setup
    test_dir = "./test_files"
    test_file = "test_append.txt"
    test_path = Path(test_dir) / test_file
    
    # Cleanup iniziale
    if test_path.exists():
        test_path.unlink()
    
    # Crea file iniziale
    test_path.write_text("iniziale")
    print(f"✅ File creato: {test_path.read_text()}")
    
    # Crea agent
    openai_key = os.getenv("OPENAI_API_KEY")
    groq_key = os.getenv("GROQ_API_KEY")
    
    if not openai_key:
        print("❌ OPENAI_API_KEY mancante")
        return False
    
    agent = LLMFileAgent(
        base_directory=test_dir,
        openai_api_key=openai_key,
        groq_api_key=groq_key,
        verbose=True
    )
    
    # Test append
    print("\n🧪 Testing append operation...")
    result = await agent.process_query('append " test" to test_append.txt')
    
    # Verifica risultato
    final_content = test_path.read_text()
    print(f"📄 Contenuto finale: '{final_content}'")
    
    expected = "iniziale test"
    success = final_content == expected
    
    if success:
        print("✅ Test PASSED: append eseguito una sola volta")
    else:
        print(f"❌ Test FAILED: expected '{expected}', got '{final_content}'")
        print(f"🔍 Lunghezza: expected {len(expected)}, got {len(final_content)}")
    
    # Cleanup
    if test_path.exists():
        test_path.unlink()
    
    return success

if __name__ == "__main__":
    success = asyncio.run(test_append_single())
    sys.exit(0 if success else 1) 