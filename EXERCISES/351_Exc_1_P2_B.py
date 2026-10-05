#
# CART 351 EXERCISE ONE PART TWO B
# Exploring the Star Wars API (SWAPI) with requests + rich
#
# Install:  pip install requests rich
#

import requests
from rich.console import Console
from rich.table import Table

console = Console()
URL = "https://swapi.dev/api/planets/"


def fetch_all_planets(url):
    """Follow the API's pagination ('next' links) and collect every planet."""
    planets = []
    with console.status("[bold yellow]Contacting the Galactic Archives...[/]"):
        while url:
            response = requests.get(url, timeout=15)
            response.raise_for_status()
            data = response.json()
            planets.extend(data["results"])
            url = data["next"]  # None on the last page
    return planets


def pretty_number(value, suffix=""):
    """Format '12500' as '12,500 km'; leave 'unknown' as a dim placeholder."""
    if value in ("unknown", "n/a", None):
        return "[dim]unknown[/]"
    try:
        return f"{int(value):,}{suffix}"
    except ValueError:
        return value


def main():
    try:
        planets = fetch_all_planets(URL)
    except requests.RequestException as err:
        console.print(f"[bold red]Could not reach the API:[/] {err}")
        return

    table = Table(
        title="Star Wars Planets",
        title_style="bold yellow",
        header_style="bold cyan",
        border_style="yellow",
        show_lines=False,
    )
    table.add_column("#", justify="right", style="dim")
    table.add_column("Planet", style="bold white")
    table.add_column("Diameter (km)", justify="right", style="green")
    table.add_column("Population", justify="right", style="magenta")

    for i, planet in enumerate(planets, start=1):
        table.add_row(
            str(i),
            planet["name"],
            pretty_number(planet["diameter"]),
            pretty_number(planet["population"]),
        )

    console.print(table)
    console.print(f"[italic]{len(planets)} planets found.[/]")


if __name__ == "__main__":
    main()