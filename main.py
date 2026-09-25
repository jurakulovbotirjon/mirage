from brain.core import think
from config.logger import logger
from rich import print
from voice.speak import speak

speak("Hello. I am Mirage.")

print("[bold cyan]MIRAGE ONLINE[/bold cyan]")
logger.info("Mirage started")

while True:
    try:
        command = input("\nYou > ").strip()

        if not command:
            continue

        if command.lower() in ["exit", "quit"]:
            logger.info("Mirage shutdown")
            break

        response = think(command)

        logger.info(f"User: {command}")
        logger.info(f"Mirage: {response}")

        print(f"[green]Mirage >[/green] {response}")

    except KeyboardInterrupt:
        print("\n[yellow]Mirage shutting down...[/yellow]")
        logger.info("Mirage interrupted")
        break

    except Exception as e:
        logger.exception("Mirage error")
        print(f"[red]Mirage error:[/red] {e}")
