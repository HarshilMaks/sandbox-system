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
    
    def __init__(self, api_key: Optional[str] = None):
        """Initialize Gemini client.
        
        Args:
            api_key: Gemini API key (or use GEMINI_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=self.api_key)
        self.logger = get_logger("provider.gemini")
    
    @with_retry(max_attempts=3, exponential_backoff=True)
    async def chat_completion(
        self,
        messages: List[Dict],
        model: str = "gemini-2.0-flash-exp",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
        stream: bool = False
    ) -> Dict:
        """Get chat completion from Gemini.
        
        Args:
            messages: Conversation messages
            model: Model name (gemini-2.0-flash-exp, gemini-1.5-pro, etc.)
            temperature: Sampling temperature
            max_tokens: Max tokens to generate
            tools: Function calling tools
            stream: Whether to stream response
            
        Returns:
            Response dict with content, tool_calls, usage
        """
        self.logger.info(f"Chat completion: model={model}, messages={len(messages)}")
        
        # Setup generation config
        config = GenerateContentConfig(
            temperature=temperature,
            max_output_tokens=max_tokens or 8192,
        )
        
        # Convert tools to Gemini format
        gemini_tools = None
        if tools:
            gemini_tools = [self._convert_tools(tools)]
        
        # Generate response
        try:
            response = self.client.models.generate_content(
                model=model,
                contents=messages[-1]["content"],  # Use last message
                config=config,
                tools=gemini_tools
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
            messages: OpenAI format messages
            
        Returns:
            Gemini format messages
        """
        gemini_messages = []
        
        for msg in messages:
            role = msg["role"]
            content = msg.get("content", "")
            
            # Skip system messages - Gemini handles them differently
            if role == "system":
                continue
            
            # Map roles
            if role == "assistant":
                gemini_role = "model"
            elif role == "user":
                gemini_role = "user"
            elif role == "tool":
                # Tool results go back as user messages
                gemini_role = "user"
                content = f"Tool result: {content}"
            else:
                continue
            
            if content:
                gemini_messages.append({
                    "role": gemini_role,
                    "parts": [{"text": content}]
                })
        
        return gemini_messages
    
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
    
    def count_tokens(self, text: str, model: str = "gemini-2.0-flash-exp") -> int:
        """Estimate token count for text.
        
        Args:
            text: Text to count
            model: Model name
            
        Returns:
            Token count
        """
        # Rough estimate: 1 token ≈ 4 characters
        return len(text) // 4
