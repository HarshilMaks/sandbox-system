"""Google Gemini provider for AI agent system."""
import os
from typing import List, Dict, Optional, AsyncIterator
from google import genai
from google.genai.types import GenerateContentConfig, Tool, FunctionDeclaration
import json

from orchestrator.utils.logging import get_logger
from orchestrator.utils.retry import with_retry


class GeminiProvider:
    """Production Gemini provider with async support."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize Gemini client.
        
        Args:
            api_key: Gemini API key (or use GEMINI_API_KEY env var)
            model: Gemini model name (or use GEMINI_MODEL env var)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Gemini API key is required. Set GEMINI_API_KEY env var or pass api_key."
            )
        self.model = model or os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        self.client = genai.Client(api_key=self.api_key)
        self.logger = get_logger("provider.gemini")
        self.logger.info(f"Initialized Gemini with model: {self.model}")
    
    @with_retry(max_attempts=3, exponential_backoff=True)
    async def chat_completion(
        self,
        messages: List[Dict],
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        stream: bool = False
    ) -> Dict:
        """Get chat completion from Gemini.
        
        Args:
            messages: Conversation messages
            model: Model name (defaults to instance model from env/init)
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            tools: Function calling tools
            stream: Whether to stream response
            
        Returns:
            Response dict with content, tool_calls, usage
        """
        model = model or self.model
        self.logger.info(f"Chat completion: model={model}, messages={len(messages)}")
        
        # Convert tools to Gemini format
        gemini_tools = None
        if tools:
            gemini_tools = [self._convert_tools(tools)]
        
        # Setup generation config
        config_params = {
            "temperature": temperature,
            "max_output_tokens": max_tokens or 8192,
        }
        
        if gemini_tools:
            config_params["tools"] = gemini_tools
        
        # Extract system instruction and filter it from contents
        system_instruction = None
        filtered = []
        for msg in messages:
            if msg["role"] == "system":
                system_instruction = msg["content"]
            else:
                filtered.append(msg)
        
        if system_instruction:
            config_params["system_instruction"] = system_instruction
        
        config = GenerateContentConfig(**config_params)
        
        # Convert messages to Gemini format
        contents = self._convert_messages(filtered)
        
        # Generate response
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=contents,
                config=config
            )
            
            result = {
                "content": "",
                "role": "assistant",
                "tool_calls": [],
                "usage": {
                    "prompt_tokens": 0,
                    "completion_tokens": 0,
                    "total_tokens": 0
                }
            }
            
            # Extract content
            if response.text:
                result["content"] = response.text
            
            # Extract function calls
            if response.candidates:
                for candidate in response.candidates:
                    if candidate.content and candidate.content.parts:
                        for part in candidate.content.parts:
                            if part.function_call:
                                fc = part.function_call
                                result["tool_calls"].append({
                                    "id": f"call_{hash(fc.name)}",
                                    "function": {
                                        "name": fc.name,
                                        "arguments": json.dumps(dict(fc.args))
                                    }
                                })
            
            if result["tool_calls"]:
                self.logger.info(f"Tool calls: {len(result['tool_calls'])}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Gemini API error: {e}")
            raise
    
    async def stream_completion(
        self,
        messages: List[Dict],
        model: str = "gemini-2.0-flash-exp",
        temperature: float = 0.7
    ) -> AsyncIterator[str]:
        """Stream chat completion.
        
        Args:
            messages: Conversation messages
            model: Model name
            temperature: Sampling temperature
            
        Yields:
            Content chunks
        """
        self.logger.info(f"Streaming completion: model={model}")
        
        config = GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=8192,
        )
        
        response = self.client.models.generate_content_stream(
            model=model,
            contents=messages[-1]["content"],
            config=config
        )
        
        for chunk in response:
            if chunk.text:
                yield chunk.text
    
    def _convert_messages(self, messages: List[Dict]) -> List:
        """Convert OpenAI message format to Gemini format.
        
        Args:
            messages: OpenAI format messages (system messages pre-filtered)
            
        Returns:
            Gemini format contents list
        """
        contents = []
        
        for msg in messages:
            role = msg["role"]
            
            if role == "user":
                contents.append({
                    "role": "user",
                    "parts": [{"text": msg.get("content", "")}]
                })
            elif role == "assistant":
                parts = []
                if msg.get("content"):
                    parts.append({"text": msg["content"]})
                if msg.get("tool_calls"):
                    for tc in msg["tool_calls"]:
                        parts.append({
                            "function_call": {
                                "name": tc["function"]["name"],
                                "args": json.loads(tc["function"]["arguments"])
                            }
                        })
                if parts:
                    contents.append({
                        "role": "model",
                        "parts": parts
                    })
            elif role == "tool":
                contents.append({
                    "role": "user",
                    "parts": [{"text": f"Tool result: {msg.get('content', '')}"}]
                })
        
        return contents
    
    def _convert_tools(self, tools: List[Dict]) -> List:
        """Convert OpenAI tools format to Gemini format.
        
        Args:
            tools: OpenAI format tools
            
        Returns:
            Gemini format Tool object
        """
        function_declarations = []
        
        for tool in tools:
            if tool["type"] == "function":
                func = tool["function"]
                
                # Convert parameters
                parameters = func.get("parameters", {})
                
                fd = FunctionDeclaration(
                    name=func["name"],
                    description=func["description"],
                    parameters=parameters
                )
                
                function_declarations.append(fd)
        
        return Tool(function_declarations=function_declarations) if function_declarations else None
