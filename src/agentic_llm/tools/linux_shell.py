from agentic_llm.tools.base import ToolABC
from agentic_llm.utils.docker import DockerInterface


class LinuxShell(ToolABC):
    name = "Linux Shell"
    usage = (
        "A Linux Shell. Use this to execute Linux commands. "
        "Input should be valid Linux commands. "
        "Chain several commands together with semicolon. "
        "Missing packages can be installed with `apk add ...` "
    )

    def __init__(
        self,
        container_name: str = "linux_repl",
        image: str = "alpine:3.14",
        image_name: str = "agentic_llm_linux",
        persistent_container: bool = True,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.backend = DockerInterface(
            container_name=container_name,
            image=image,
            image_name=image_name,
            persistent_container=persistent_container,
        )

    def __call__(self, prompt: str) -> str:
        prompt = f'sh -c "{prompt}"'
        return self.backend.exec(prompt)
