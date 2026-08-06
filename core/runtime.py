from core.config import JarvisConfig
from core.logger import create_logger
from tools.registry import ToolRegistry
from tools.system_tool import SystemTool
from tools.app_tool import AppTool
from tools.file_tool import FileTool


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

    def shutdown(self):
        """Stop JARVIS cleanly."""

        self.logger.info("Shutting down JARVIS runtime.")

        self.running = False

        print()
        print("JARVIS shutting down...")
        print("JARVIS offline.")

        self.logger.info("JARVIS runtime stopped.")