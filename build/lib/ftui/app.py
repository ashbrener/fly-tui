import asyncio
import os
import sys
from typing import Dict, Any, List

from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, DataTable, Static, RichLog, Input, Label
from textual.screen import Screen, ModalScreen
from textual.containers import Container, Horizontal, Vertical
from textual.binding import Binding

from ftui.fly_client import FlyClient

class MachineListScreen(Screen):
    """Screen for listing and managing Fly machines."""
    
    BINDINGS = [
        Binding("r", "refresh", "Refresh", show=True),
        Binding("l", "view_logs", "Logs", show=True),
        Binding("s", "scale", "Scale", show=True),
        Binding("h", "ssh", "SSH", show=True),
        Binding("ctrl+s", "start_machine", "Start", show=True),
        Binding("ctrl+x", "stop_machine", "Stop", show=True),
    ]

    def __init__(self, fly_client: FlyClient):
        super().__init__()
        self.fly = fly_client

    def compose(self) -> ComposeResult:
        yield Header()
        yield DataTable(id="machine-table", cursor_type="row")
        yield Footer()

    async def on_mount(self) -> None:
        table = self.query_one(DataTable)
        table.add_columns("ID", "Name", "State", "Region", "Image", "Created")
        await self.action_refresh()
        # Set a timer for periodic refresh
        self.set_interval(10, self.action_refresh)

    async def action_refresh(self) -> None:
        """Fetch machine list and update table."""
        table = self.query_one(DataTable)
        try:
            machines = await self.fly.list_machines()
            table.clear()
            for m in machines:
                table.add_row(
                    m.get("id", ""),
                    m.get("name", ""),
                    m.get("state", ""),
                    m.get("region", ""),
                    m.get("image", ""),
                    m.get("created_at", "")[:19] # Truncate timestamp
                )
        except Exception as e:
            self.notify(f"Error fetching machines: {e}", severity="error")

    def get_selected_machine(self) -> str:
        """Get the ID of the selected machine in the table."""
        table = self.query_one(DataTable)
        if table.cursor_row is not None:
            row = table.get_row_at(table.cursor_row)
            return row[0]
        return None

    async def action_view_logs(self) -> None:
        machine_id = self.get_selected_machine()
        if machine_id:
            self.app.push_screen(LogScreen(self.fly, machine_id))
        else:
            self.notify("No machine selected")

    async def action_scale(self) -> None:
        self.app.push_screen(ScaleDialog(self.fly))

    async def action_ssh(self) -> None:
        machine_id = self.get_selected_machine()
        if not machine_id:
            self.notify("No machine selected")
            return

        # We need to suspend the TUI to run an interactive shell
        self.app.suspend_stdio()
        try:
            print(f"Connecting to {machine_id}...")
            # Use os.system for simple handover to the interactive fly ssh command
            cmd = f"fly ssh console -s -m {machine_id}"
            if self.fly.mock:
                 print(f"MOCK: {cmd}")
                 input("Press Enter to return to FTUI...")
            else:
                os.system(cmd)
        finally:
            self.app.resume_stdio()

    async def action_start_machine(self) -> None:
        machine_id = self.get_selected_machine()
        if machine_id:
            try:
                await self.fly.start_machine(machine_id)
                self.notify(f"Machine {machine_id} started")
                await self.action_refresh()
            except Exception as e:
                self.notify(f"Failed to start machine: {e}", severity="error")

    async def action_stop_machine(self) -> None:
        machine_id = self.get_selected_machine()
        if machine_id:
            try:
                await self.fly.stop_machine(machine_id)
                self.notify(f"Machine {machine_id} stopped")
                await self.action_refresh()
            except Exception as e:
                self.notify(f"Failed to stop machine: {e}", severity="error")

class LogScreen(Screen):
    """Screen for viewing machine logs."""
    
    BINDINGS = [
        Binding("q", "back", "Back", show=True),
        Binding("c", "clear", "Clear", show=True),
    ]

    def __init__(self, fly_client: FlyClient, machine_id: str):
        super().__init__()
        self.fly = fly_client
        self.machine_id = machine_id
        self.process = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield RichLog(id="log-viewer", highlight=True, markup=True)
        yield Footer()

    async def on_mount(self) -> None:
        log_viewer = self.query_one(RichLog)
        log_viewer.write(f"Tail logs for machine [bold cyan]{self.machine_id}[/bold cyan]...")
        
        # Start log tailing
        asyncio.create_task(self.stream_logs())

    async def stream_logs(self):
        log_viewer = self.query_one(RichLog)
        
        if self.fly.mock:
            while True:
                log_viewer.write(f"[{self.machine_id}] Simulated log message {random.randint(100,999)}")
                await asyncio.sleep(1)
                if self.is_current_screen is False:
                    break
            return

        args = ["logs", "--instance", self.machine_id]
        self.process = await asyncio.create_subprocess_exec(
            "fly", *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT
        )
        
        while True:
            line = await self.process.stdout.readline()
            if not line:
                break
            log_viewer.write(line.decode().strip())

    def action_back(self) -> None:
        if self.process:
            self.process.terminate()
        self.app.pop_screen()

    def action_clear(self) -> None:
        self.query_one(RichLog).clear()

class ScaleDialog(ModalScreen):
    """Modal for scaling applications."""
    
    def compose(self) -> ComposeResult:
        with Container(id="dialog"):
            yield Label("Scale Application", id="title")
            yield Label("Machine Count:")
            yield Input(placeholder="Enter count (e.g. 3)", id="count-input")
            yield Label("VM Size:")
            yield Input(placeholder="Enter size (e.g. shared-cpu-1x)", id="vm-input")
            with Horizontal():
                yield Static(id="spacer")
                yield Vertical(
                     Horizontal(
                        Static(" "),
                        Static("[b]Enter[/b] to Apply, [b]Esc[/b] to Cancel", id="help-text"),
                        classes="dialog-buttons"
                     )
                )

    def on_key(self, event) -> None:
        if event.key == "escape":
            self.app.pop_screen()

    async def on_input_submitted(self, event: Input.Submitted) -> None:
        count_val = self.query_one("#count-input", Input).value
        vm_val = self.query_one("#vm-input", Input).value
        
        fly = FlyClient() # Re-using FlyClient
        
        try:
            if count_val:
                await fly.scale_count(int(count_val))
                self.notify(f"Scaling count to {count_val}...")
            
            if vm_val:
                await fly.scale_vm(vm_val)
                self.notify(f"Scaling VM size to {vm_val}...")
                
            self.app.pop_screen()
        except Exception as e:
            self.notify(f"Scale error: {e}", severity="error")

class FTUI(App):
    """Main Fly.io TUI application."""
    
    CSS = """
    #dialog {
        width: 40;
        height: auto;
        border: thick $primary;
        background: $surface;
        padding: 1 2;
        align: center middle;
    }
    #title {
        text-align: center;
        width: 100%;
        margin-bottom: 1;
        background: $primary;
        color: $on-primary;
    }
    .dialog-buttons {
        margin-top: 1;
    }
    #spacer {
        width: 1fr;
    }
    """

    def on_mount(self) -> None:
        self.fly = FlyClient()
        self.push_screen(MachineListScreen(self.fly))

if __name__ == "__main__":
    app = FTUI()
    app.run()
