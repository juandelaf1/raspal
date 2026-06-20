import asyncio
import json
import signal
import sys
from pathlib import Path

import typer
from rich.console import Console
from rich.json import JSON
from rich.table import Table

from raspal.cache import Cache
from raspal.extractor import Extractor
from raspal.fetcher import Fetcher
from raspal.improvements.async_compatibility import AsyncFetcher
from raspal.router import Router

app = typer.Typer(name="raspal")
console = Console()


def _handle_interrupt(sig, frame):
    console.print("\n[yellow]Interrupted. Exiting...[/yellow]")
    sys.exit(0)


signal.signal(signal.SIGINT, _handle_interrupt)


@app.command()
def fetch(
    url: str,
    engine: str = typer.Option(
        "auto", "--engine", "-e",
        help="scrapling | playwright | stealth | auto",
    ),
    text: bool = typer.Option(True, "--text", "-t", help="Extract text content"),
    timeout: int = typer.Option(30, "--timeout", help="Request timeout in seconds"),
    pretty: bool = typer.Option(True, "--pretty", "-p", help="Pretty print output"),
):
    """Fetch a URL and extract content."""
    with Fetcher() as fetcher:
        result = fetcher.fetch(url, engine=engine, timeout=timeout)

    output = {
        "url": url,
        "status": result.status,
        "engine": result.engine,
        "cached": result.cached,
    }

    if result.error:
        output["error"] = result.error
    elif text and result.html:
        ext = Extractor()
        output["text"] = ext.extract_text(result.html)
        output["metadata"] = ext.extract_metadata(result.html)

    if pretty:
        console.print(JSON(json.dumps(output, indent=2, default=str)))
    else:
        console.print(json.dumps(output, indent=2, default=str))


@app.command()
def run(
    config: str = typer.Argument(..., help="Path to YAML config file"),
    pretty: bool = typer.Option(True, "--pretty", "-p"),
):
    """Run a scraping pipeline from a YAML config."""
    router = Router()
    result = router.run(config)
    if pretty:
        console.print(JSON(json.dumps(result, indent=2, default=str)))
    else:
        console.print(json.dumps(result, indent=2, default=str))


@app.command()
def queue(
    config: str = typer.Argument(..., help="Path to YAML config file"),
    db: str = typer.Option("raspal_queue.sqlite", "--db", help="Queue database path"),
    output: str = typer.Option("results.json", "--output", "-o", help="Output file"),
):
    """Process URLs from a queue using a YAML config."""
    router = Router()
    pipeline = router.run_queue(config, db)
    pipeline.to_json(output)
    console.print(f"[green]Processed {len(pipeline)} items -> {output}[/green]")


@app.command()
def status():
    """Show current throttle delays and cache info."""
    from raspal.throttle import AutoThrottle

    throttle = AutoThrottle()
    table = Table(title="AutoThrottle Delays")
    table.add_column("Engine", style="cyan")
    table.add_column("Current delay (s)", style="magenta")

    for engine, delay in throttle.current_delays.items():
        table.add_row(engine, f"{delay:.2f}")

    console.print(table)


@app.command()
def async_fetch(
    url: str,
    engine: str = typer.Option("auto", "--engine", "-e", help="scrapling | playwright | stealth | auto"),
    text: bool = typer.Option(True, "--text", "-t", help="Extract text content"),
    timeout: int = typer.Option(30, "--timeout", help="Request timeout in seconds"),
    pretty: bool = typer.Option(True, "--pretty", "-p", help="Pretty print output"),
):
    """Fetch a URL asynchronously."""
    async def run():
        async with AsyncFetcher() as fetcher:
            result = await fetcher.fetch_async(url, engine=engine, timeout=timeout)

            output = {
                "url": url,
                "status": result.status,
                "engine": result.engine,
                "cached": result.cached,
            }

            if result.error:
                output["error"] = result.error
            elif text and result.html:
                ext = Extractor()
                output["text"] = ext.extract_text(result.html)
                output["metadata"] = ext.extract_metadata(result.html)

            return output

    try:
        output = asyncio.run(run())
        if pretty:
            console.print(JSON(json.dumps(output, indent=2, default=str)))
        else:
            console.print(json.dumps(output, indent=2, default=str))
    except Exception as e:
        console.print(f"[red]Error: {e}[/red]")
        sys.exit(1)


@app.command()
async def async_batch(
    urls: list[str] = typer.Argument(..., help="List of URLs to fetch asynchronously"),
    engine: str = typer.Option("auto", "--engine", "-e", help="scrapling | playwright | stealth | auto"),
    text: bool = typer.Option(True, "--text", "-t", help="Extract text content"),
    timeout: int = typer.Option(30, "--timeout", help="Request timeout in seconds"),
    pretty: bool = typer.Option(True, "--pretty", "-p", help="Pretty print output"),
):
    """Fetch multiple URLs asynchronously."""
    async with AsyncFetcher() as fetcher:
        results = await fetcher.fetch_batch(urls, engine=engine, timeout=timeout)

        output = []
        for result in results:
            entry = {
                "url": getattr(result, "url", "unknown"),
                "status": getattr(result, "status", 0),
                "engine": getattr(result, "engine", "unknown"),
                "cached": getattr(result, "cached", False),
            }

            if hasattr(result, "error") and result.error:
                entry["error"] = result.error
            elif text and hasattr(result, "html") and result.html:
                ext = Extractor()
                entry["text"] = ext.extract_text(result.html)
                entry["metadata"] = ext.extract_metadata(result.html)

            output.append(entry)

        if pretty:
            console.print(JSON(json.dumps(output, indent=2, default=str)))
        else:
            console.print(json.dumps(output, indent=2, default=str))


@app.command()
def clear_cache(
    url: str | None = typer.Argument(None, help="URL to clear (clears all if omitted)"),
):
    """Clear the cache."""
    with Cache() as cache:
        if url:
            cache.clear(url)
            console.print(f"[green]Cleared cache for {url}[/green]")
        else:
            cache.clear()
            console.print("[green]Cleared entire cache[/green]")


@app.command()
def validate(
    config: str = typer.Argument(..., help="Path to YAML config file"),
):
    """Validate a YAML config file."""
    from raspal.router import Router
    from raspal.exceptions import ConfigError

    try:
        router = Router()
        router._load_config(config)
        console.print(f"[green]✓ Config válido:[/green] {config}")
    except ConfigError as e:
        console.print(f"[red]✗ Config inválido:[/red] {e}")
        raise typer.Exit(1)


@app.command()
def compliance(
    url: str = typer.Argument(..., help="URL a verificar"),
):
    """Check basic compliance signals before scraping."""
    from raspal.compliance import check_compliance

    result = check_compliance(url)
    signals = result.get("signals", {})
    warnings = result.get("warnings", [])

    console.print(f"[bold]Dominio:[/bold] {signals.get('domain', 'N/A')}")
    console.print(f"[bold]robots.txt:[/bold] {signals.get('robots_txt', 'N/A')}")

    if signals.get("is_sensitive_domain"):
        console.print("[yellow]⚠️  Dominio potencialmente sensible (redes sociales, salud, finanzas)[/yellow]")

    if warnings:
        console.print("\n[yellow]Advertencias:[/yellow]")
        for warning in warnings:
            console.print(f"  • {warning}")
    else:
        console.print("\n[green]✓ Sin advertencias obvias. Aun así, revisa ToS y robots.txt.[/green]")


@app.command()
def setup():
    """Prepare the environment: install browsers, check Ollama."""
    from raspal.setup import run_setup
    run_setup()


@app.command()
def serve(
    host: str = typer.Option("127.0.0.1", "--host", help="Host del dashboard"),
    port: int = typer.Option(8462, "--port", "-p", help="Puerto del dashboard"),
):
    """Start the web dashboard."""
    from raspal.web.dashboard import serve as web_serve
    web_serve(host=host, port=port)


@app.command()
def init():
    """Scaffold a new scraping project interactively."""
    from raspal.scaffold import run_init
    run_init()


@app.command()
def report(
    input: str = typer.Option("results.json", "--input", "-i", help="Pipeline results JSON"),
    output: str = typer.Option("report.html", "--output", "-o", help="HTML report path"),
):
    """Generate an HTML report from pipeline results."""
    from raspal.reporter import generate_html, print_summary

    try:
        with open(input, encoding="utf-8") as f:
            data = json.load(f)
    except FileNotFoundError:
        console.print(f"[red]No se encontró {input}[/red]")
        raise typer.Exit(1)

    print_summary(data)
    generate_html(data, output)


if __name__ == "__main__":
    app()
