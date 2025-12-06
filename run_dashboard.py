import time
import random
from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.layout import Layout
from datetime import datetime
from spreadish.selection.gladiator import select_best_pairs_with_stats

CARTMAN_QUOTES = [
    "Screw you guys, I'm going home!",
    "Respect my authoritah!",
    "Whatever, I do what I want!",
    "Beefcake! BEEFCAKE!",
    "I'm not fat, I'm just big-boned!"
]

def cartman_ascii():
    return r"""
       _____
     /  O  O  \
    |   _   |
    |  |_|  |
     \_____/
    """

def generate_live_dashboard(top_pairs):
    layout = Layout()
    layout.split(Layout(name="header", size=3), Layout(name="main"), Layout(name="footer", size=3))
    layout["header"].update(f"[bold yellow]{cartman_ascii()}[/] [blink white]LIVE CRYPTO GLADIATOR ARENA[/]")
    table = Table(title="\n🔥 Top Gladiator Pairs (Immortal Index Ranking)", show_header=True)
    table.add_column("Rank", style="cyan"); table.add_column("Pair", style="bold")
    table.add_column("Price", justify="right"); table.add_column("Immortal Index", justify="right")
    table.add_column("RSI", justify="right"); table.add_column("Liquidity Depth", justify="right")
    table.add_column("Spread", justify="right"); table.add_column("Volatility", justify="right")

    for idx, (pair, score, stats) in enumerate(top_pairs, 1):
        rsi_color = "red" if stats['rsi'] > 70 else "green" if stats['rsi'] < 30 else "yellow"
        index_color = "green" if score > 0.7 else "yellow" if score > 0.5 else "red"
        table.add_row(
            str(idx),
            f"[bold]{pair}[/]",
            f"${stats['last_price']:,.4f}",
            f"[{index_color}]🏆 {score:.2f}[/]",
            f"[{rsi_color}]{stats['rsi']:.1f}[/]",
            f"${stats['depth'] / 1e6:,.1f}M",
            f"{stats['spread']:.2f}%",
            f"{stats['volatility']:.2f}%"
        )
    layout["main"].update(table)
    total_score = sum(p[1] for p in top_pairs) if top_pairs else 0.0
    footer_text = (f"[bold white]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/] | "
                   f"[blink yellow]Market Vitality: {total_score/len(top_pairs) if top_pairs else 0:.2f}[/] | "
                   f"[cyan]{random.choice(CARTMAN_QUOTES)}[/]")
    layout["footer"].update(footer_text)
    return layout

def main():
    console = Console()
    console.clear()
    console.print("[bold red]INITIALIZING IMMORTAL TRADING GLADIATOR...[/]")
    time.sleep(1)
    with Live(console=console, screen=True, auto_refresh=False) as live:
        while True:
            try:
                top_pairs_data = select_best_pairs_with_stats(limit_markets=400, top_n=30)
                live.update(generate_live_dashboard(top_pairs_data))
                live.refresh()
                time.sleep(6)
            except KeyboardInterrupt:
                console.print("\n[bold red]Stopping...[/]")
                break
            except Exception as e:
                print(f"An error occurred: {e}")
                time.sleep(2)

if __name__ == "__main__":
    main()
