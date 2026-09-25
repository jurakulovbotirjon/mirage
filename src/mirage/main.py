from __future__ import annotations

import asyncio

from rich import print

from mirage.core.application import MirageApplication


async def run() -> None:
    application = MirageApplication()

    print("[bold cyan]MIRAGE ONLINE[/bold cyan]")
    print("[dim]Type 'exit' or 'quit' to shut down.[/dim]")

    while True:
        try:
            user_input = input("\nYou > ").strip()

            if not user_input:
                continue

            if user_input.lower() in {"exit", "quit"}:
                print("[yellow]MIRAGE shutting down...[/yellow]")
                break

            response = await application.process(user_input)

            print(f"[green]MIRAGE >[/green] {response.text}")

        except KeyboardInterrupt:
            print("\n[yellow]MIRAGE shutting down...[/yellow]")
            break

        except Exception as exc:
            print(f"[red]MIRAGE error:[/red] {exc}")


if __name__ == "__main__":
    asyncio.run(run())
