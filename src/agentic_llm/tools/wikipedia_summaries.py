# loosely based on https://github.com/langchain-ai/langchain/blob/master/libs/community/langchain_community/utilities/wikipedia.py # noqa

import wikipedia

from agentic_llm.tools.base import ToolABC


class WikipediaSummary(ToolABC):
    name = "Wikipedia"
    usage = (
        "Get information from an encyclopedia to answer a search query. "
        "Input should be a search query such as "
        "'Who was Marie Curie?'. "
        "Result will be a detailed answer to the question. "
        "There can be multiple results. "
    )

    def __init__(
        self,
        max_results: int = 5,
        max_words: int = 200,
        language: str = "en",
        **kwargs,
    ):
        super().__init__(**kwargs)
        wikipedia.set_lang(language)
        self.max_results = max_results
        self.max_words = max_words
        self.wikipedia_client = wikipedia

    def __call__(self, query: str) -> str:
        results = self.wikipedia_client.search(query, results=self.max_results)
        if len(results):
            pages = []
            for result in results:
                try:
                    content_page = self.wikipedia_client.page(
                        title=result, auto_suggest=False
                    )
                    result_dict = {
                        "title": result,
                        "summary": content_page.summary[: self.max_words],
                        "source": content_page.url,
                    }
                    pages.append(
                        "\n".join(
                            [f"{k}: {v}" for k, v in result_dict.items()]
                        )
                    )

                except (
                    self.wiki_client.exceptions.PageError,
                    self.wiki_client.exceptions.DisambiguationError,
                ):
                    continue
            return "\n".join(pages)

        else:
            return "No results found!"
