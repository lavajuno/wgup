from wgup import cli

if __name__ == "__main__":
    """
    Called by runpy. cli.entrypoint is called directly when installed via pipx.
    """
    cli.entrypoint()
