import pytest

from agentic_llm.tools import (
    DDGSearch,
    LinuxShell,
    PythonInterpreter,
    WikipediaSummary,
)

# Just smoke tests for now...


class TestTools:
    def test_duckduckgo(self):
        assert DDGSearch.name is not None
        assert DDGSearch.usage is not None

        search_tool = DDGSearch(max_results=5)
        result = search_tool("Who was Marie Curie?")
        print(result)

    def test_wikipedia(self):
        assert WikipediaSummary.name is not None
        assert WikipediaSummary.usage is not None
        wiki = WikipediaSummary(max_results=2)
        result = wiki("Who was Otto von Bismarck?")
        print(result)

    def test_python(self):
        assert PythonInterpreter.name is not None
        assert PythonInterpreter.usage is not None
        python_tool = PythonInterpreter()
        result = python_tool("print(f'10*2 = {10*2}')")
        print(result)
        cmd = """
def factorial(x):
    if x == 1:
        return x
    else:
        return x*factorial(x-1)
print(f"4! = {factorial(4)}")
    """
        result = python_tool(cmd)
        print(result)

    def test_linux(self):
        assert LinuxShell.name is not None
        assert LinuxShell.usage is not None
        linux_tool = LinuxShell()

        print(linux_tool("echo 'hello world'"))
        print(linux_tool("pwd; date"))
        print(linux_tool("ls -la"))
        print(
            linux_tool(
                (
                    "mkdir -p tmp_dir;"
                    "cd tmp_dir; mkdir -p tmp; touch test.txt; ls -l"
                )
            )
        )

        print(linux_tool("ping www.google.com -c 2"))
