from duckduckgo_search import DDGS

from agentic_llm.tools.base import ToolABC


class DDGSearch(ToolABC):
    name = "DDG Search"
    usage = (
        "Get information for a search query. "
        "Input should be either a question like "
        "'Who was Tolstoy?', or a single word like 'Tolstoy'. "
        "Result will be the answers to the question. "
        "There can be multiple results. "
    )

    def __init__(
        self,
        max_results: int = 10,
        instant_answers: bool = False,
        safe_search: bool = True,
        time_limit: bool = True,
        add_url: bool = False,
        **kwargs,
    ):
        super().__init__(**kwargs)
        self.max_results = max_results
        self.instant_answers = instant_answers
        self.safe_search = "on" if safe_search else "off"
        self.time_limit = "y" if time_limit else "n"
        self.add_url = add_url

        pass

    def __call__(self, query: str):
        with DDGS() as ddgs:
            answer = None
            if self.instant_answers:
                answer = list(ddgs.answers(query))
            if answer:
                answer_dict = {}
                if self.add_url:
                    answer_dict["source"] = answer[0]["url"]
                answer_dict["answer"] = answer[0]["text"]
                return "\n ".join(
                    [f"{k}: {v}" for k, v in answer_dict.items()]
                )
            else:
                # fall back to normal search
                answers = []
                results = list(
                    ddgs.text(
                        query,
                        safesearch=self.safe_search,
                        timelimit=self.time_limit,
                        max_results=self.max_results,
                    )
                )
                for answer in results:
                    answer_dict = {}
                    answer_dict["title"] = answer["title"]
                    if self.add_url:
                        answer_dict["source"] = answer["href"]
                    answer_dict["answer"] = answer["body"]

                    answers.append(
                        "\n".join(
                            [f"{k}: {v}" for k, v in answer_dict.items()]
                        )
                    )
                return "\n".join(answers)
