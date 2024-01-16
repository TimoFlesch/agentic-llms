import typing

from gpt4all import GPT4All


class GPT4All_LLM:
    def __init__(
        self,
        model_type: str = "GPT4ALL",
        model_name: str = "mistral-7b-instruct-v0.1.Q4_0.gguf",
        model_path: typing.Union[None, str] = None,
        temperature: float = 0.7,
        top_p: float = 0.4,
        top_k: int = 40,
        max_tokens: int = 200,
        allow_download: bool = False,
        device: str = "cpu",
        context_length: int = 4096,
        verbose: bool = False,
        stop: str = "Observation:",
        system_prompt: typing.Union[None, str] = (
            "A chat between a curious user and "
            "an artificial intelligence assistant."
        ),
        prompt_template: typing.Union[None, str] = "USER: {0}\nASSISTANT:",
        always_prepend_system_prompt: bool = False,
        use_default_system_prompt: bool = False,
        use_default_prompt_template: bool = False,
        **kwargs
    ):
        self.model_type = model_type
        assert model_name is not None, (
            "No model name provided. Please see "
            "the following link for supported models (use 'filename'):\n"
            "https://github.com/nomic-ai/gpt4all/blob/main/"
            "gpt4all-chat/metadata/models2.json"
        )
        self.model_name = model_name
        if model_path is None:
            assert allow_download is True, (
                "No model path provided,"
                "Please provide a model path, or"
                " enable automatic download of missing model file."
            )
        self.model_path = model_path
        init_params = {
            "model_name": model_name,
            "model_path": model_path,
            "allow_download": allow_download,
            "device": device,
            "verbose": verbose,
            "n_ctx": context_length,
        }
        generate_params = {
            "temp": temperature,
            "top_p": top_p,
            "top_k": top_k,
            "max_tokens": max_tokens,
        }
        model_params = {
            "init_params": init_params,
            "generate_params": generate_params,
            "stop": stop,
        }
        self.model_params = model_params

        self.context_length = context_length
        self.system_prompt = system_prompt or ""
        self.prompt_template = prompt_template or "{0}"
        self.always_prepend_system_prompt = always_prepend_system_prompt
        self.use_default_prompt_template = use_default_prompt_template
        self.use_default_system_prompt = use_default_system_prompt

        self._iter = 0

        self.llm = self._load_llm(model_params["init_params"])

    def generate(
        self, prompt: str, temp: typing.Union[None, float] = None
    ) -> str:
        if temp is not None:
            self.model_params["generate_params"]["temp"] = temp
        prompt = self._preprocess_prompt(prompt)
        # for some reason, the kernel kept crashing with the snippet below
        # (context window exceeded ?!)
        # tokens = []
        # for token in self.llm.generate(
        #     prompt, streaming=True, **self.model_params["generate_params"]
        # ):
        #     tokens.append(token)

        #     response = "".join(tokens)
        #     if self.model_params["stop"] in response:
        #         break
        response = self.llm.generate(
            prompt, **self.model_params["generate_params"]
        )
        response = response.split(self.model_params["stop"])[0].replace(
            self.model_params["stop"], ""
        )
        return response

    def _load_llm(self, model_params) -> GPT4All:
        model = GPT4All(
            **model_params,
        )
        if self.use_default_system_prompt:
            self.system_prompt = repr(model.config["systemPrompt"])
        if self.use_default_prompt_template:
            self.prompt_template = repr(model.config["promptTemplate"])
        return model

    def _preprocess_prompt(self, prompt: str) -> str:
        if self.always_prepend_system_prompt:
            return self.system_prompt + self.prompt_template.format(prompt)
        if self._iter == 0:
            return self.system_prompt + self.prompt_template.format(prompt)
        else:
            return self.prompt_template.format(prompt)

    def _stop_on_token_callback(self, token_id, token_string):
        # one sentence is enough:
        if self.model_params["stop"] in token_string:
            return False
        else:
            return True
