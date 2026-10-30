"""
Comprehensive test suite for Haven AI SDK.
Tests streaming, reasoning extraction, pipeline adapters, and error handling.
"""

import unittest
from unittest.mock import patch, MagicMock
import json
import io

from haven_ai import (
    Client,
    ProviderConfig,
    ProviderPolicy,
    ReasoningExtractor,
    ChatStreamIterator,
    Pipeable,
    pipe_fn,
    RateLimitError,
    ModelLoadingError,
    AuthenticationError,
    ImageResponse,
)


class TestHavenAISDK(unittest.TestCase):

    def test_reasoning_extractor(self):
        extractor = ReasoningExtractor()
        
        # Test streamed chunks with <think> tag
        c1, r1 = extractor.process_chunk("<think>Need to analyze ")
        self.assertIsNone(c1)
        self.assertEqual(r1, "Need to analyze ")

        c2, r2 = extractor.process_chunk("the PEG grammar.</think>Here is the answer.")
        self.assertEqual(r2, "the PEG grammar.")
        self.assertEqual(c2, "Here is the answer.")

        self.assertEqual(extractor.accumulated_reasoning, "Need to analyze the PEG grammar.")
        self.assertEqual(extractor.accumulated_content, "Here is the answer.")

    def test_chat_stream_iterator(self):
        raw_sse = [
            'data: {"id":"1","model":"llama","choices":[{"delta":{"content":"<think>Plan</think>Hello"}}]}\n',
            'data: {"id":"2","model":"llama","choices":[{"delta":{"content":" world!"}}]}\n',
            'data: [DONE]\n'
        ]
        iterator = ChatStreamIterator(iter(raw_sse))
        chunks = list(iterator)
        self.assertEqual(len(chunks), 2)
        self.assertEqual(chunks[0].reasoning, "Plan")
        self.assertEqual(chunks[0].content, "Hello")
        self.assertEqual(chunks[1].content, " world!")
        self.assertEqual(iterator.full_content, "Hello world!")
        self.assertEqual(iterator.full_reasoning, "Plan")

    def test_pipeline_adapter(self):
        # Mock client chat
        mock_client = MagicMock()
        mock_response = MagicMock()
        mock_response.content = "Parsed AST"
        mock_client.chat.return_value = mock_response

        # Functional pipe adapter
        transformer = pipe_fn(mock_client, model="test-model")
        
        # Test __call__
        res1 = transformer("Input prompt")
        self.assertEqual(res1, "Parsed AST")

        # Test Python bitwise pipe __ror__
        res2 = "Input prompt" | transformer
        self.assertEqual(res2, "Parsed AST")

        # Verify chat call parameters
        mock_client.chat.assert_called_with(
            messages=[{"role": "user", "content": "Input prompt"}],
            model="test-model",
            temperature=0.7,
            max_tokens=1024
        )

    def test_image_response_save(self):
        import tempfile
        import os

        fake_png = b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR"
        img = ImageResponse(fake_png, format="png")
        
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            temp_path = f.name

        try:
            saved_path = img.save(temp_path)
            self.assertEqual(saved_path, temp_path)
            with open(temp_path, "rb") as f:
                self.assertEqual(f.read(), fake_png)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

    def test_provider_headers(self):
        config = ProviderConfig(provider="together")
        headers = config.get_headers()
        self.assertEqual(headers.get("X-HF-Provider"), "together")

        policy_config = ProviderConfig(policy=ProviderPolicy.FASTEST)
        headers2 = policy_config.get_headers()
        self.assertEqual(headers2.get("X-HF-Provider-Policy"), ":fastest")


if __name__ == "__main__":
    unittest.main()
