"""
The LLMClient which acts as an interface for whichever model is used.
"""
from abc import ABC, abstractmethod

# An abstract of what every subclass should have
class LLMClient(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Take a prompt and return the models raw text response"""

# Gemini
class GeminiClient(LLMClient):
    """Using Gemini's free tier API"""
    def __init__(self, model="gemini-3.5-flash"):
        from google import genai
        self.client = genai.Client()
        self.model = model

    def complete(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model = self.model,
            contents = prompt,
        )
        return response.text

# Anthropic
class AnthropicClient(LLMClient):
    def __init__(self, model="claude-sonnet-4-6"):
        import anthropic
        self.client = anthropic.Anthropic()
        self.model = model
    
    def complete(self, prompt: str) -> str:
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        return msg.content[0].text

class TestingClient(LLMClient):
    """Scripted responses to test generation and loop without API calls"""
    def __init__(self, responses: list[str]):
        self.responses = responses
        self.calls = []

    def complete(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.responses.pop(0)