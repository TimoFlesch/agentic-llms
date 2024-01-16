import pytest

from agentic_llm.llms.gpt4all import GPT4All_LLM


# just a smoke test
class TestLLM:
    def test_init_gpt4all(self):
        model = GPT4All_LLM(model_path="./models/")
        result = model.generate("What is Berlin?")
        assert len(result)
        print(result)
