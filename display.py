import threading
import queue
import time
from collections import deque
from datetime import datetime

from rich.live import Live
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.console import Group

import config


class Display:
    def __init__(self, result_queue: queue.Queue, stop_event: threading.Event,
                 model_size: str = None, chunk_duration: float = None):
        self.result_queue = result_queue
        self.stop_event = stop_event
        self.model_size = model_size or config.MODEL_SIZE
        self.chunk_duration = chunk_duration or config.CHUNK_DURATION
        self.entries = deque(maxlen=config.MAX_DISPLAY_LINES)
        self.last_latency = 0.0
        self.total_chunks = 0

    def _build_display(self) -> Group:
        table = Table(show_header=False, expand=True, box=None, padding=(0, 1))
        table.add_column("time", style="dim", width=10)
        table.add_column("content", ratio=1)

        for entry in self.entries:
            ts = datetime.fromtimestamp(entry["timestamp"]).strftime("%H:%M:%S")
            content = Text()
            content.append("JA: ", style="bold cyan")
            content.append(entry["japanese"])
            content.append("\n")
            content.append("EN: ", style="bold green")
            content.append(entry["english"])
            table.add_row(f"[{ts}]", content)

        status = Text()
        status.append(f" Model: {self.model_size}", style="dim")
        status.append(f"  |  Chunk: {self.chunk_duration}s", style="dim")
        status.append(f"  |  Latency: {self.last_latency:.1f}s", style="dim")
        status.append(f"  |  Chunks: {self.total_chunks}", style="dim")
        status.append("  |  Ctrl+C to stop", style="dim red")

        panel = Panel(
            Group(table, Text(""), status),
            title="[bold]Live Japanese → English Translation[/bold]",
            border_style="blue",
        )
        return panel

    def run(self):
        with Live(self._build_display(), refresh_per_second=2, screen=False) as live:
            while not self.stop_event.is_set():
                try:
                    result = self.result_queue.get(timeout=0.5)
                    self.entries.append(result)
                    self.last_latency = result["process_time"]
                    self.total_chunks += 1
                except queue.Empty:
                    pass
                live.update(self._build_display())
