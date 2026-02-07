import click
from rich.console import Console

console = Console()


@click.group()
@click.version_option(version="1.0.0", prog_name="devon")
def cli():
    """DEVON - Discovery Engine and Vault for Open Neural models

    Discover, download, and manage LLM models with ease.

    Examples:
      devon search --provider qwen --params 30b
      devon download https://huggingface.co/Qwen/Qwen2.5-32B-Instruct
      devon list
    """
    pass


# Import commands
from devon.cli.search_cmd import search  # noqa: E402
from devon.cli.download_cmd import download  # noqa: E402
from devon.cli.list_cmd import list_models  # noqa: E402
from devon.cli.info_cmd import info  # noqa: E402
from devon.cli.clean_cmd import clean  # noqa: E402
from devon.cli.export_cmd import export  # noqa: E402
from devon.cli.status_cmd import status  # noqa: E402
from devon.cli.remove_cmd import remove  # noqa: E402

# Register commands
cli.add_command(search)
cli.add_command(download)
cli.add_command(list_models, name="list")
cli.add_command(info)
cli.add_command(clean)
cli.add_command(export)
cli.add_command(status)
cli.add_command(remove)

if __name__ == "__main__":
    cli()
