import pytest

from agentic_llm.agent import LLMAgent, get_default_cfg


class TestAgent:
    def test_agent_smoke(self):
        cfg = get_default_cfg()
        cfg["agent_config"]["max_iter"] = 1
        agent = LLMAgent(cfg)
        response = agent.answer("use python to calculate 2*2")
        assert response is not None
        print(response)
