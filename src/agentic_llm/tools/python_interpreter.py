from agentic_llm.tools.base import ToolABC
from agentic_llm.utils.docker import DockerInterface
from agentic_llm.utils.prompt import convert_to_single_line


class PythonInterpreter(ToolABC):
    name = "Python Interpreter"
    usage = (
        "A Python interpreter. Use this to execute python code. "
        "Input should be valid python code. "
        "If you want to see the output of a value, you should "
        "print it out with `print(...)`"
    )

    def __init__(
        self,
        container_name: str = "python_repl",
        image_name: str = "agentic_llm_python",
        image: str = "python:3.9-slim-bookworm",
        persistent_container: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.backend = DockerInterface(
            container_name=container_name,
            image_name=image_name,
            image=image,
            persistent_container=persistent_container,
        )

    def __call__(self, prompt):
        prompt = self._convert_to_single_line(prompt)
        return self.backend.exec(prompt)

    def _convert_to_single_line(self, code_snippet: str) -> str:
        return convert_to_single_line(code_snippet)
