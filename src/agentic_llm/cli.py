import click

from agentic_llm.agent import LLMAgent
from agentic_llm.utils.files import load_config


@click.command()
@click.option(
    "--config_path",
    default=None,
    help=(
        "path to config file, e.g. "
        "/home/USER/code/agentic-llm/configs/default_config.json. "
        "Uses default config if left empty"
    ),
)
@click.option("--query", prompt="Your Query:", help="A question for the agent")
def cli(config_path, query):
    """An AI agent that uses tools to answer your questions"""
    if config_path is not None:
        cfg = load_config(config_path)
    else:
        cfg = None
    agent = LLMAgent(cfg)
    response = agent.answer(query)
    click.echo(response)


if __name__ == "__main__":
    cli()
