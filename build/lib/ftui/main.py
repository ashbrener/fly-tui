import click
import os
from ftui.app import FTUI
from ftui.fly_client import FlyClient

@click.command()
@click.option("--mock", is_flag=True, help="Use mock flyctl for development")
def main(mock: bool):
    """Fly.io Terminal UI (ftui)"""
    if mock:
        os.environ["FTUI_MOCK"] = "1"
    
    app = FTUI()
    app.run()

if __name__ == "__main__":
    main()
