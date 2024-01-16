from setuptools import setup, find_packages

setup(
    name="agentic_llm",
    # py_modules=["agentic_llm"],
    version="0.0.1",
    description="A package for enabling locally hosted LLMs to use tools.",
    author="Timo Flesch",
    author_email="timo.flesch@googlemail.com",
    url="https://github.com/timoflesch/agentic_llms",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    install_requires=[
        "click>=8.1.7",
        "duckduckgo_search>=4.1.1",
        "gpt4all>=2.1.0",
        "docker>=7.0.0",
        "wikipedia>=1.4.0",
    ],
    entry_points="""
        [console_scripts]
        agentic_llm=agentic_llm.cli:cli
    """,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)
