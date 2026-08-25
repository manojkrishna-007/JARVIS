from core.config import JarvisConfig
from core.logger import create_logger
from core.automation import AutomationAction, AutomationEngine

from tools.registry import ToolRegistry
from tools.system_tool import SystemTool
from tools.app_tool import AppTool
from tools.file_tool import FileTool
from tools.process_tool import ProcessTool
from tools.input_tool import InputTool
from tools.window_tool import WindowTool
from tools.screen_tool import ScreenTool


class JarvisRuntime:
    """Controls the lifecycle of the JARVIS application."""

    def __init__(self):
        self.config = JarvisConfig()
        self.logger = create_logger(self.config.logs_dir)

        self.running = False

        self.tools = ToolRegistry()
        self.tools.register(SystemTool())
        self.tools.register(AppTool())
        self.tools.register(FileTool())
        self.tools.register(ProcessTool())
        self.tools.register(InputTool())
        self.tools.register(WindowTool())
        self.tools.register(ScreenTool())
        
        self.automation = AutomationEngine(self.tools)

    def start(self):
        """Start JARVIS."""

        self.logger.info("Starting JARVIS runtime.")

        self.running = True

        print()
        print("=" * 50)
        print("              J A R V I S")
        print("=" * 50)
        print()

        print("JARVIS is online.")
        print()
        print(self.config.summary())
        print()

        self.logger.info("JARVIS runtime started successfully.")

    def process_command(self, command: str) -> str:
        """Process a command and route it to the appropriate tool."""

        command = command.strip()

        if not command:
            return "I didn't receive a command."

        command_lower = command.lower()
        
        if command_lower.startswith("wait for "):
            target = command[9:].strip()

            if not target:
                return "Please tell me what I should wait for."

            result = self.tools.execute(
                "screen",
                action="wait_for",
                target=target,
                timeout=10,
            )

            return result.message
        
        if command_lower.startswith("locate "):
            target = command[7:].strip()

            if not target:
                return "Please tell me what text you want me to locate."

            result = self.tools.execute(
                "screen",
                action="locate",
                target=target,
            )

            return result.message
        
        if command_lower.startswith("wait for "):
            target = command[9:].strip()

            if not target:
                return "Please tell me what I should wait for."

            result = self.tools.execute(
                "screen",
                action="wait_for",
                target=target,
                timeout=10,
            )

            return result.message
                
        if command_lower.startswith("click "):
            target = command[6:].strip()

            return self._visual_action(
                target=target,
                action="click",
                failure_message=(
                    "Please tell me what you want me to click."
                ),
                success_message=(
                    "Clicked '{target}' at ({x}, {y})."
                ),
            )

        if command_lower.startswith("double click "):
            target = command[13:].strip()

            return self._visual_action(
                target=target,
                action="double_click",
                failure_message=(
                    "Please tell me what you want me to double-click."
                ),
                success_message=(
                    "Double-clicked '{target}' at ({x}, {y})."
                ),
            )

        if command_lower.startswith("move to "):
            target = command[8:].strip()

            return self._visual_action(
                target=target,
                action="move",
                failure_message=(
                    "Please tell me where you want me to move."
                ),
                success_message=(
                    "Moved mouse to '{target}' at ({x}, {y})."
                ),
            )
                
        if command_lower == "automation test":
            launch_result = self.automation.launch_and_focus(
                application="notepad",
                window_title="Notepad",
            )

            if not launch_result.success:
                return launch_result.message

            type_result = self.automation.type_text(
                "Hello from JARVIS Automation Engine!"
            )

            if not type_result.success:
                return type_result.message

            window_title = launch_result.data["window_title"]

            return (
                "Automation completed successfully. "
                f"Controlled window: {window_title}"
            )
    
        if command_lower in {"hello", "hello jarvis", "hi"}:
            return "Hello. JARVIS is online and ready."

        if command_lower in {"help", "commands"}:
            tool_list = self.tools.list_tools()

            lines = [
                "Available commands:",
                "  help   - Show available commands",
                "  status - Show JARVIS system information",
                "  hello  - Test JARVIS",
                "  tools  - List registered tools",
                "  exit   - Shut down JARVIS",
                "",
                "Registered tools:",
            ]

            for tool in tool_list:
                lines.append(f"  {tool.name} - {tool.description}")

            return "\n".join(lines)

        if command_lower in {"tools", "list tools"}:
            tools = self.tools.list_tools()

            if not tools:
                return "No tools are currently registered."

            lines = ["Registered JARVIS tools:"]

            for tool in tools:
                lines.append(f"  {tool.name} - {tool.description}")

            return "\n".join(lines)
        
        if command_lower in {"screenshot", "take screenshot", "capture screen"}:
            result = self.tools.execute(
                "screen",
                action="screenshot",
            )

            return result.message
        
        if command_lower in {
            "read screen",
            "read the screen",
            "what is on my screen",
            "what's on my screen",
        }:
            result = self.tools.execute(
                "screen",
                action="read",
            )

            return result.message
        
        if command_lower.startswith("create folder "):
            folder_path = command[len("create folder "):].strip()

            result = self.tools.execute(
                "files",
                action="create_folder",
                path=folder_path,
            )

            return result.message

        if command_lower.startswith("create file "):
            file_path = command[len("create file "):].strip()

            result = self.tools.execute(
                "files",
                action="create_file",
                path=file_path,
                content="",
            )

            return result.message

        if command_lower.startswith("read file "):
            file_path = command[len("read file "):].strip()

            result = self.tools.execute(
                "files",
                action="read_file",
                path=file_path,
            )

            return result.message

        if command_lower.startswith("check file "):
            file_path = command[len("check file "):].strip()

            result = self.tools.execute(
                "files",
                action="exists",
                path=file_path,
            )

            return result.message

        if command_lower.startswith("open folder "):
            folder_path = command[len("open folder "):].strip()

            result = self.tools.execute(
                "files",
                action="open",
                path=folder_path,
            )

            return result.message
        
        if command_lower in {
            "what applications are running",
            "what apps are running",
            "list processes",
            "show processes",
        }:
            result = self.tools.execute(
                "processes",
                action="list",
            )

            if not result.success:
                return result.message

            processes = result.data

            lines = [
                f"Currently running processes: {len(processes)}"
            ]

            for process in processes:
                lines.append(
                    f"  PID {process['pid']} - {process['name']}"
                )

            return "\n".join(lines)


        if command_lower.startswith("is ") and " running" in command_lower:
            process_name = command_lower[3:]

            process_name = process_name.replace(
                " currently running",
                "",
            )

            process_name = process_name.replace(
                " running",
                "",
            )

            process_name = process_name.rstrip("?.! ")

            if process_name:
                result = self.tools.execute(
                    "processes",
                    action="check",
                    process_name=process_name,
                )

                return result.message

        if command_lower in {
            "system usage",
            "system status",
            "how much ram am i using",
            "how much memory am i using",
            "how is my computer doing",
            "computer status",
        }:
            result = self.tools.execute(
                "processes",
                action="system_usage",
            )

            return result.message


        if command_lower in {
            "what is using the most cpu",
            "what is using most cpu",
            "top cpu",
            "highest cpu usage",
        }:
            result = self.tools.execute(
                "processes",
                action="top_cpu",
            )

            return result.message


        if command_lower in {
            "what is using the most memory",
            "what is using most memory",
            "top memory",
            "highest memory usage",
        }:
            result = self.tools.execute(
                "processes",
                action="top_memory",
            )

            return result.message
        
        if command_lower == "move mouse":
            result = self.tools.execute(
                "input",
                action="move",
                x=500,
                y=300,
            )

            return result.message
        
        if (
    command_lower.startswith("move mouse to ")
    and " in " in command_lower
):
            coordinates, window_title = command[14:].rsplit(" in ", 1)

            parts = coordinates.strip().split()

            if len(parts) != 2:
                return "Please provide X and Y coordinates."

            try:
                x = int(parts[0])
                y = int(parts[1])
            except ValueError:
                return "X and Y coordinates must be numbers."

            window_title = window_title.strip()

            if not window_title:
                return "Please specify the target window."

            window_result = self.tools.execute(
                "windows",
                action="get",
                title=window_title,
            )

            if not window_result.success:
                return window_result.message

            window = window_result.data

            focus_result = self.tools.execute(
                "windows",
                action="focus",
                title=window_title,
            )

            if not focus_result.success:
                return focus_result.message

            move_result = self.tools.execute(
                "input",
                action="move_relative",
                x=x,
                y=y,
                window=window,
            )

            return move_result.message


        if command_lower.startswith("move mouse to "):
            coordinates = command[14:].strip()

            parts = coordinates.split()

            if len(parts) != 2:
                return "Please provide X and Y coordinates."

            try:
                x = int(parts[0])
                y = int(parts[1])
            except ValueError:
                return "X and Y coordinates must be numbers."

            result = self.tools.execute(
                "input",
                action="move",
                x=x,
                y=y,
            )

            return result.message
        
        if command_lower == "click test":
            result = self.tools.execute(
                "input",
                action="click",
                x=176,
                y=270,
            )

            return result.message
        
        if command_lower == "type test":
            result = self.tools.execute(
                "input",
                action="type",
                text="Hello from JARVIS!",
            )

            return result.message

        if command_lower.startswith("find window "):
            window_title = command[12:].strip()

            result = self.tools.execute(
                "windows",
                action="find",
                title=window_title,
            )

            return result.message


        if command_lower.startswith("focus window "):
            window_title = command[13:].strip()

            result = self.tools.execute(
                "windows",
                action="focus",
                title=window_title,
            )

            return result.message
        
        if command_lower.startswith("type ") and " in notepad" in command_lower:
            text = command[5:]

            text = text[:text.lower().rfind(" in notepad")]

            if not text.strip():
                return "Please tell me what you want me to type."

            focus_result = self.tools.execute(
                "windows",
                action="focus",
                title="notepad",
            )

            if not focus_result.success:
                return focus_result.message

            type_result = self.tools.execute(
                "input",
                action="type",
                text=text,
            )

            return type_result.message
        
        if command_lower.startswith("press ") and " in " in command_lower:
            key_part, window_part = command[6:].rsplit(" in ", 1)

            key = key_part.strip()
            window_title = window_part.strip()

            if not key:
                return "Please specify a key to press."

            if not window_title:
                return "Please specify the target window."

            focus_result = self.tools.execute(
                "windows",
                action="focus",
                title=window_title,
            )

            if not focus_result.success:
                return focus_result.message

            press_result = self.tools.execute(
                "input",
                action="press",
                key=key,
            )

            return press_result.message
        
        if command_lower.startswith("hotkey ") and " in " in command_lower:
            shortcut_part, window_part = command[7:].rsplit(" in ", 1)

            shortcut = shortcut_part.strip()
            window_title = window_part.strip()

            if not shortcut:
                return "Please specify a keyboard shortcut."

            if not window_title:
                return "Please specify the target window."

            keys = [
                key.strip()
                for key in shortcut.split("+")
                if key.strip()
            ]

            focus_result = self.tools.execute(
                "windows",
                action="focus",
                title=window_title,
            )

            if not focus_result.success:
                return focus_result.message

            hotkey_result = self.tools.execute(
                "input",
                action="hotkey",
                keys=keys,
            )

            return hotkey_result.message

        if command_lower.startswith("open "):
            application = command[5:].strip()

            result = self.tools.execute(
                "app",
                application=application,
            )

            return result.message

        if command_lower in {"status", "system status"}:
            result = self.tools.execute("system")

            if not result.success:
                return result.message

            data = result.data

            return (
                f"Operating System: {data['operating_system']}\n"
                f"OS Version: {data['os_version']}\n"
                f"Machine: {data['machine']}\n"
                f"Processor: {data['processor']}\n"
                f"CPU Count: {data['cpu_count']}\n"
                f"Disk Total: {data['disk_total_gb']} GB\n"
                f"Disk Used: {data['disk_used_gb']} GB\n"
                f"Disk Free: {data['disk_free_gb']} GB"
            )

        return (
            f"I received: '{command}'\n"
            "I don't have a tool capable of handling that request yet."
        )

    def _visual_action(
        self,
        target: str,
        action: str,
        failure_message: str,
        success_message: str,
    ) -> str:
        """Locate visible text and perform an input action on it."""

        target = target.strip()

        if not target:
            return failure_message

        locate_result = self.tools.execute(
            "screen",
            action="locate",
            target=target,
        )

        if not locate_result.success:
            return locate_result.message

        x = locate_result.data["x"]
        y = locate_result.data["y"]

        action_result = self.tools.execute(
            "input",
            action=action,
            x=x,
            y=y,
        )

        if not action_result.success:
            return action_result.message

        return success_message.format(
            target=target,
            x=x,
            y=y,
        )

    def shutdown(self):
        """Stop JARVIS cleanly."""

        self.logger.info("Shutting down JARVIS runtime.")

        self.running = False

        print()
        print("JARVIS shutting down...")
        print("JARVIS offline.")

        self.logger.info("JARVIS runtime stopped.")