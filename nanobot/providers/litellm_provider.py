"""LiteLLM provider implementation for multi-provider support."""

import os
import json
from typing import Any

import litellm
from litellm import acompletion
from loguru import logger

from nanobot.providers.base import LLMProvider, LLMResponse, ToolCallRequest


class LiteLLMProvider(LLMProvider):
    """
    LLM provider using LiteLLM for multi-provider support.
    
    Supports OpenRouter, Anthropic, OpenAI, Gemini, and many other providers through
    a unified interface.
    """
    
    def __init__(
        self, 
        api_key: str | None = None, 
        api_base: str | None = None,
        default_model: str = "anthropic/claude-opus-4-5"
    ):
        super().__init__(api_key, api_base)
        self.default_model = default_model
        
        # Detect OpenRouter by api_key prefix or explicit api_base
        self.is_openrouter = (
            (api_key and api_key.startswith("sk-or-")) or
            (api_base and "openrouter" in api_base)
        )
        
        # Track if using custom endpoint (vLLM, etc.)
        self.is_vllm = bool(api_base) and not self.is_openrouter
        
        # Configure LiteLLM based on provider
        if api_key:
            if self.is_openrouter:
                # OpenRouter mode - set key
                os.environ["OPENROUTER_API_KEY"] = api_key
            elif self.is_vllm:
                # vLLM/custom endpoint - uses OpenAI-compatible API
                os.environ["HOSTED_VLLM_API_KEY"] = api_key
            elif "deepseek" in default_model:
                os.environ.setdefault("DEEPSEEK_API_KEY", api_key)
            elif "anthropic" in default_model:
                os.environ.setdefault("ANTHROPIC_API_KEY", api_key)
            elif "openai" in default_model or "gpt" in default_model:
                os.environ.setdefault("OPENAI_API_KEY", api_key)
            elif "gemini" in default_model.lower():
                os.environ.setdefault("GEMINI_API_KEY", api_key)
            elif "zhipu" in default_model or "glm" in default_model or "zai" in default_model:
                os.environ.setdefault("ZAI_API_KEY", api_key)
            elif "dashscope" in default_model or "qwen" in default_model.lower():
                os.environ.setdefault("DASHSCOPE_API_KEY", api_key)
            elif "groq" in default_model:
                os.environ.setdefault("GROQ_API_KEY", api_key)
            elif "moonshot" in default_model or "kimi" in default_model:
                os.environ.setdefault("MOONSHOT_API_KEY", api_key)
                os.environ.setdefault("MOONSHOT_API_BASE", api_base or "https://api.moonshot.cn/v1")
        
        if api_base:
            litellm.api_base = api_base
        
        # Disable LiteLLM logging noise
        litellm.suppress_debug_info = True
    
    async def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
        model: str | None = None,
        max_tokens: int = 4096,
        temperature: float = 0.7,
    ) -> LLMResponse:
        """
        Send a chat completion request via LiteLLM.
        
        Args:
            messages: List of message dicts with 'role' and 'content'.
            tools: Optional list of tool definitions in OpenAI format.
            model: Model identifier (e.g., 'anthropic/claude-sonnet-4-5').
            max_tokens: Maximum tokens in response.
            temperature: Sampling temperature.
        
        Returns:
            LLMResponse with content and/or tool calls.
        """
        model = model or self.default_model
        
        # For OpenRouter, prefix model name if not already prefixed
        if self.is_openrouter and not model.startswith("openrouter/"):
            model = f"openrouter/{model}"
        
        # For Zhipu/Z.ai, ensure prefix is present
        # Handle cases like "glm-4.7-flash" -> "zai/glm-4.7-flash"
        if ("glm" in model.lower() or "zhipu" in model.lower()) and not (
            model.startswith("zhipu/") or 
            model.startswith("zai/") or 
            model.startswith("openrouter/")
        ):
            model = f"zai/{model}"

        # For DashScope/Qwen, ensure dashscope/ prefix
        if ("qwen" in model.lower() or "dashscope" in model.lower()) and not (
            model.startswith("dashscope/") or
            model.startswith("openrouter/")
        ):
            model = f"dashscope/{model}"

        # For Moonshot/Kimi, ensure moonshot/ prefix (before vLLM check)
        if ("moonshot" in model.lower() or "kimi" in model.lower()) and not (
            model.startswith("moonshot/") or model.startswith("openrouter/")
        ):
            model = f"moonshot/{model}"

        # For Gemini, ensure gemini/ prefix if not already present
        if "gemini" in model.lower() and not model.startswith("gemini/"):
            model = f"gemini/{model}"


        # For vLLM, use hosted_vllm/ prefix per LiteLLM docs
        # Convert openai/ prefix to hosted_vllm/ if user specified it
        if self.is_vllm:
            model = f"hosted_vllm/{model}"
        
        # kimi-k2.5 only supports temperature=1.0
        if "kimi-k2.5" in model.lower():
            temperature = 1.0

        kwargs: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "temperature": temperature,
        }
        
        # Pass api_base directly for custom endpoints (vLLM, etc.)
        if self.api_base:
            kwargs["api_base"] = self.api_base
        
        if tools:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = "auto"

        # Log request details
        self._log_request(kwargs, messages, tools)

        try:
            response = await acompletion(**kwargs)
            llm_response = self._parse_response(response)

            # Log response details
            self._log_response(llm_response, response)

            return llm_response
        except Exception as e:
            logger.error(f"LLM API call failed: {str(e)}")
            # Return error as content for graceful handling
            return LLMResponse(
                content=f"Error calling LLM: {str(e)}",
                finish_reason="error",
            )
    
    def _parse_response(self, response: Any) -> LLMResponse:
        """Parse LiteLLM response into our standard format."""
        choice = response.choices[0]
        message = choice.message
        
        tool_calls = []
        if hasattr(message, "tool_calls") and message.tool_calls:
            for tc in message.tool_calls:
                # Parse arguments from JSON string if needed
                args = tc.function.arguments
                if isinstance(args, str):
                    import json
                    try:
                        args = json.loads(args)
                    except json.JSONDecodeError:
                        args = {"raw": args}
                
                tool_calls.append(ToolCallRequest(
                    id=tc.id,
                    name=tc.function.name,
                    arguments=args,
                ))
        
        usage = {}
        if hasattr(response, "usage") and response.usage:
            usage = {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            }
        
        return LLMResponse(
            content=message.content,
            tool_calls=tool_calls,
            finish_reason=choice.finish_reason or "stop",
            usage=usage,
        )
    
    def get_default_model(self) -> str:
        """Get the default model."""
        return self.default_model

    def _log_request(
        self,
        kwargs: dict[str, Any],
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None
    ) -> None:
        """Log LLM request details."""
        logger.info("=" * 80)
        logger.info("🤖 LLM API Request")
        logger.info("=" * 80)
        logger.info(f"Model: {kwargs['model']}")
        logger.info(f"Temperature: {kwargs['temperature']}")
        logger.info(f"Max Tokens: {kwargs['max_tokens']}")

        if self.api_base:
            logger.info(f"API Base: {self.api_base}")

        # Log message count and summary
        logger.info(f"Messages: {len(messages)} total")
        for i, msg in enumerate(messages):
            role = msg.get('role', 'unknown')
            content = msg.get('content', '')

            # Handle different content types
            if isinstance(content, list):
                # Multi-modal content (text + images)
                text_parts = [p.get('text', '') for p in content if isinstance(p, dict) and p.get('type') == 'text']
                content_preview = ' '.join(text_parts)[:100]
                has_images = any(isinstance(p, dict) and p.get('type') == 'image_url' for p in content)
                image_info = " [+images]" if has_images else ""
                logger.debug(f"  [{i}] {role}: {content_preview}...{image_info}")
            elif content:
                content_preview = str(content)[:100]
                logger.debug(f"  [{i}] {role}: {content_preview}...")
            else:
                # Tool call message
                if 'tool_calls' in msg:
                    tool_names = [tc.get('function', {}).get('name', 'unknown') for tc in msg.get('tool_calls', [])]
                    logger.debug(f"  [{i}] {role}: [tool_calls: {', '.join(tool_names)}]")
                else:
                    logger.debug(f"  [{i}] {role}: [no content]")

        # Log tools
        if tools:
            tool_names = [t.get('function', {}).get('name', 'unknown') for t in tools]
            logger.info(f"Tools: {len(tools)} available - {', '.join(tool_names)}")
            logger.debug("Tool definitions:")
            for tool in tools:
                func = tool.get('function', {})
                logger.debug(f"  - {func.get('name')}: {func.get('description', 'No description')}")
        else:
            logger.info("Tools: None")

        logger.info("-" * 80)

    def _log_response(self, llm_response: LLMResponse, raw_response: Any) -> None:
        """Log LLM response details."""
        logger.info("📥 LLM API Response")
        logger.info("=" * 80)

        # Log finish reason
        logger.info(f"Finish Reason: {llm_response.finish_reason}")

        # Log token usage
        if llm_response.usage:
            logger.info(f"Token Usage:")
            logger.info(f"  - Prompt: {llm_response.usage.get('prompt_tokens', 0)}")
            logger.info(f"  - Completion: {llm_response.usage.get('completion_tokens', 0)}")
            logger.info(f"  - Total: {llm_response.usage.get('total_tokens', 0)}")

        # Log content
        if llm_response.content:
            content_preview = llm_response.content[:200]
            if len(llm_response.content) > 200:
                content_preview += "..."
            logger.info(f"Content: {content_preview}")
            logger.debug(f"Full content:\n{llm_response.content}")
        else:
            logger.info("Content: None")

        # Log tool calls
        if llm_response.tool_calls:
            logger.info(f"Tool Calls: {len(llm_response.tool_calls)}")
            for i, tc in enumerate(llm_response.tool_calls):
                logger.info(f"  [{i}] {tc.name}")
                logger.debug(f"      ID: {tc.id}")
                logger.debug(f"      Arguments: {json.dumps(tc.arguments, indent=2)}")
        else:
            logger.info("Tool Calls: None")

        # Log model info from response
        if hasattr(raw_response, 'model'):
            logger.debug(f"Response Model: {raw_response.model}")

        logger.info("=" * 80)
