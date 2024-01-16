# system prompt and main loop for ReAct adapted from
# https://github.com/mpaepper/llm_agents/blob/main/llm_agents/agent.py
import datetime
import re
import typing

from agentic_llm.llms import GPT4All_LLM
from agentic_llm.tools import (
    DDGSearch,
    LinuxShell,
    PythonInterpreter,
    WikipediaSummary,
)


def get_default_cfg() -> dict:
    return {
        "agent_config": {
            "max_iter": 5,
            "verbose": False,
            "system_prompt": """
Today is {today} and you can use tools to get new information.
Answer the question as best as you can using the following tools:

{tool_description}


Use the following format:

Question: the input question you must answer
Thought: comment on what you want to do next
Action: the action to take, exactly one element of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
... (this Thought/Action/Action Input/Observation repeats N times,
 use it until you are sure of the answer)
Thought: I now know the final answer
Final Answer: your final answer to the original input question

Begin!

Question: {question}
Thought: {previous_responses}
            """,
        },
        "llm_config": {
            "model_type": "GPT4ALL",
            "model_name": "mistral-7b-instruct-v0.1.Q4_0.gguf",
            "model_path": "./models/",
            "temperature": 0,
            "top_p": 0.4,
            "top_k": 40,
            "max_tokens": 200,
            "allow_download": False,
            "device": "cpu",
            "context_length": 4096,
            "verbose": False,
            "stop": "Observation",
            "always_prepend_system_prompt": True,
            "prompt_template": None,
        },
        "tools_config": {
            "DuckDuckGo Search": {
                "max_results": 3,
                "instant_answers": False,
                "safe_search": True,
                "time_limit": True,
                "add_url": False,
            },
            "Linux Shell": {
                "container_name": "linux_repl",
                "image": "alpine:3.14",
                "image_name": "agentic_llm_linux",
                "persistent_container": True,
            },
            "Python Interpreter": {
                "container_name": "python_repl",
                "image": "python:3.9-slim-bookworm",
                "image_name": "agentic_llm_python",
                "persistent_container": True,
            },
            "Wikipedia": {
                "max_results": 1,
                "language": "en",
            },
        },
    }


class LLMAgent:
    available_tools = {
        "DuckDuckGo Search": DDGSearch,
        "Linux Shell": LinuxShell,
        "Python Interpreter": PythonInterpreter,
        "Wikipedia": WikipediaSummary,
    }

    def __init__(
        self,
        cfg: typing.Union[None, dict] = None,
    ):
        if cfg is None:
            cfg = get_default_cfg()
        assert cfg["llm_config"]["model_type"] == "GPT4ALL"
        for k, v in cfg["agent_config"].items():
            setattr(self, k, v)
        print(
            "initialising "
            f"{cfg['llm_config']['model_name'].split('.gguf')[0]}..."
        )
        self.llm = GPT4All_LLM(**cfg["llm_config"])
        print("...done!")
        self.tools = {
            tool_name: self.available_tools[tool_name](**tool_cfg)
            for tool_name, tool_cfg in cfg["tools_config"].items()
        }

        self._tool_usage = "\n".join(
            [f"{tool.name}: {tool.usage}" for tool in self.tools.values()]
        )
        self._tool_names = ", ".join(list(self.tools.keys()))

    def answer(self, prompt: str) -> str:
        prompt_history = []

        system_prompt = self.system_prompt.format(
            today=datetime.date.today(),
            tool_description=self._tool_usage,
            tool_names=self._tool_names,
            question=prompt,
            previous_responses="{previous_responses}",
        )
        if self.verbose:
            print(system_prompt.format(previous_responses=""))
        n_iter = 0
        while n_iter < self.max_iter:
            n_iter += 1
            this_prompt = system_prompt.format(
                previous_responses="\n".join(prompt_history)
            )
            response = self.llm.generate(this_prompt)
            try:
                action, action_value = self._parse_response(response)
            except ValueError:
                self._shutdown_docker()
                return response
            if action == "Final Answer:":
                self._shutdown_docker()
                return response
            assert action in list(
                self.tools.keys()
            ), f"LLM requested tool that is not available: {action}"
            # consult tool:
            result = self.tools[action](action_value)
            response += f"\nObservation: {result}\nThought:"
            print(response)
            prompt_history.append(response)
        # shutdown and remove containers
        self._shutdown_docker()
        return response

    def _parse_response(self, response: str) -> typing.Tuple[str, str]:
        if "Final Answer:" in response:
            return "Final Answer:", response.split("Final Answer:")[-1].strip()
        match = re.search(
            r"Action: [\[]?(.*?)[\]]?[\n]*Action Input:[\s]*(.*)",
            response,
            re.DOTALL,
        )
        if not match:
            raise ValueError(f"Can't interpret LLM's response: {response}")
        action = match.group(1).strip()
        action_value = match.group(2)
        return action, action_value.strip(" ").strip('"').replace("`", "")

    def _shutdown_docker(self):
        python_repl = self.tools.get("Python Interpreter", None)
        if python_repl is not None:
            python_repl.backend.stop()
            python_repl.backend.remove()
        linux_shell = self.tools.get("Linux Shell", None)
        if linux_shell is not None:
            linux_shell.backend.stop()
            linux_shell.backend.remove()
