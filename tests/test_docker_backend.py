import pytest

from agentic_llm.utils.docker import DockerInterface

# just a smoke test


class TestDocker:
    def test_docker_init(self):
        docker = DockerInterface(
            container_name="linux_repl_test",
            image="alpine:3.14",
            image_name="agentic_llm_linux",
            persistent_container=True,
        )
        docker.exec("echo hello world")
        docker.stop()
        docker.remove()
