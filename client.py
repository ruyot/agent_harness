"""
The LLMClient which acts as an interface for whichever model is used.
"""
from abc import ABC, abstractmethod

# An abstract of what every subclass should have
class LLMClient(ABC):
    @abstractmethod
    def complete(self, prompt: str) -> str:
        """Take a prompt and return the models raw text response"""


class GeminiClient(LLMClient):
    """Using Gemini's free tier API"""
    def __init__(self, model="gemini-3.1-flash-lite"):
        from google import genai
        self.client = genai.Client()
        self.model = model

    def complete(self, prompt: str) -> str:
        response = self.client.models.generate_content(
            model = self.model,
            contents = prompt,
        )
        return response.text
    
class TestingClient(LLMClient):
    """Scripted responses to test generation and loop without API calls"""
    def __init__(self, responses: list[str]):
        self.responses = responses
        self.calls = []

    def complete(self, prompt: str) -> str:
        self.calls.append(prompt)
        return self.responses.pop(0)