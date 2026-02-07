#!/usr/bin/env python3
"""Test script to verify LLM logging functionality."""

import asyncio
import sys
from pathlib import Path

# Add project to path
sys.path.insert(0, str(Path(__file__).parent))

from nanobot.utils.logging import configure_logging
from nanobot.providers.litellm_provider import LiteLLMProvider


async def test_llm_logging():
    """Test LLM logging with a simple request."""
    
    print("🧪 Testing LLM Logging Functionality\n")
    
    # Configure logging
    print("1. Configuring logging at INFO level...")
    configure_logging(verbose=True, debug=False)
    
    # Create provider (using a mock API key for testing)
    print("2. Creating LiteLLM provider...")
    provider = LiteLLMProvider(
        api_key="test-key",
        default_model="anthropic/claude-opus-4-5"
    )
    
    # Prepare test messages
    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "What is 2+2?"}
    ]
    
    # Prepare test tools
    tools = [
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Perform basic arithmetic",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "operation": {"type": "string", "enum": ["add", "subtract"]},
                        "a": {"type": "number"},
                        "b": {"type": "number"}
                    },
                    "required": ["operation", "a", "b"]
                }
            }
        }
    ]
    
    print("3. Making test LLM call (will fail with test key, but will show logging)...\n")
    print("=" * 80)
    
    # Make the call (will fail but we'll see the logging)
    response = await provider.chat(
        messages=messages,
        tools=tools,
        model="anthropic/claude-opus-4-5",
        max_tokens=100,
        temperature=0.7
    )
    
    print("=" * 80)
    print("\n4. Response received:")
    print(f"   Content: {response.content}")
    print(f"   Finish Reason: {response.finish_reason}")
    print(f"   Tool Calls: {len(response.tool_calls)}")
    print(f"   Usage: {response.usage}")
    
    print("\n✅ Logging test completed!")
    print("\nNote: The API call failed (expected with test key), but you should see:")
    print("  - 🤖 LLM API Request section with model, temperature, messages, tools")
    print("  - 📥 LLM API Response section (showing error)")
    print("\nTo test with real API:")
    print("  1. Set your API key in ~/.nanobot/config.json")
    print("  2. Run: nanobot gateway --verbose")
    print("  3. Send a message through Telegram/Discord/CLI")


async def test_debug_logging():
    """Test DEBUG level logging."""
    
    print("\n" + "=" * 80)
    print("🧪 Testing DEBUG Level Logging\n")
    
    # Configure debug logging
    print("1. Configuring logging at DEBUG level...")
    configure_logging(verbose=False, debug=True)
    
    # Create provider
    provider = LiteLLMProvider(
        api_key="test-key",
        api_base="https://api.example.com/v1",
        default_model="gpt-4"
    )
    
    # Prepare messages with tool calls
    messages = [
        {"role": "system", "content": "You are a helpful assistant with access to tools."},
        {"role": "user", "content": "Search for information about Python"},
        {
            "role": "assistant",
            "content": "I'll search for that.",
            "tool_calls": [
                {
                    "id": "call_123",
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "arguments": '{"query": "Python programming language"}'
                    }
                }
            ]
        },
        {
            "role": "tool",
            "tool_call_id": "call_123",
            "content": "Python is a high-level programming language..."
        }
    ]
    
    print("2. Making test call with complex message history...\n")
    print("=" * 80)
    
    response = await provider.chat(
        messages=messages,
        model="gpt-4",
        max_tokens=200,
        temperature=0.5
    )
    
    print("=" * 80)
    print("\n✅ DEBUG logging test completed!")
    print("\nYou should see detailed message content in the logs above.")


if __name__ == "__main__":
    print("🐈 nanobot LLM Logging Test\n")
    
    # Run tests
    asyncio.run(test_llm_logging())
    asyncio.run(test_debug_logging())
    
    print("\n" + "=" * 80)
    print("📚 Next Steps:")
    print("=" * 80)
    print("1. Review the log output above")
    print("2. Try with real API: nanobot gateway --verbose")
    print("3. Read documentation: cat LLM_LOGGING.md")
    print("4. Enable file logging: nanobot gateway --verbose --log-file llm.log")

