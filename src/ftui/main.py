import click
import os
from ftui.app import FTUI
from ftui.fly_client import FlyClient

@click.command()
@click.option("--mock", is_flag=True, help="Use mock flyctl for development")
@click.option("--refresh", default=5, type=int, help="Refresh interval in seconds (default: 5)")
def main(mock: bool, refresh: int):
    """Fly.io Terminal UI (ftui)"""
    if mock:
        os.environ["FTUI_MOCK"] = "1"
    
    app = FTUI(refresh_interval=refresh)
    app.run()

if __name__ == "__main__":
    main()
