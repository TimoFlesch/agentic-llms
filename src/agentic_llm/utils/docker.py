from io import BytesIO

import docker


class DockerInterface:
    dockerfile_template = """
        FROM {image}
        WORKDIR /workspace
        """

    def __init__(
        self,
        image_name: str = "agentic_llm_python",
        image: str = "python:3.9-alpine",
        container_name: str = "python_repl",
        persistent_container: bool = True,
    ):
        self.image_name = image_name
        self.dockerfile = BytesIO(
            self.dockerfile_template.format(image=image).encode("utf-8")
        )
        self.container_name = container_name
        self.persistent_container = persistent_container

        try:
            self.client = docker.from_env()
        except docker.errors.DockerException:
            print("make sure that the Docker engine is running!")
            raise

        try:
            self.client.images.get(self.image_name)
        except docker.errors.ImageNotFound:
            self._create_image(tag=self.image_name)

        try:
            self.container = self.client.containers.get(self.container_name)
            self.start()
        except Exception:
            self._run_container(name=self.container_name)

    def _create_image(self, tag: str = "sandbox"):
        print(f"creating docker image {tag} ...")
        self.client.images.build(fileobj=self.dockerfile, tag=tag)
        print("...done!")

    def _run_container(self, name: str = "python_repl"):
        print(f"running docker container {name}...")
        self.container = self.client.containers.run(
            self.image_name, detach=True, tty=True, name=name
        )
        print("...done!")

    def start(self):
        print(f"starting container {self.container_name}...")
        self.container.start()
        print("...done!")

    def stop(self):
        print(f"stopping container {self.container_name}...")
        self.container.stop()
        print("...done!")

    def remove(self):
        self.container.remove()

    def exec(self, command: str):
        if not self.persistent_container:
            self.start()

        result = self.container.exec_run(command)
        if not self.persistent_container:
            self.stop()
        if result.exit_code == 0:
            return result.output.decode("utf-8")
        elif result.exit_code == 1:
            return f"Execution Failed! {result.output.decode('utf-8')}"
