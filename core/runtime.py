from core.config import JarvisConfig
from core.logger import create_logger


class JarvisRuntime:
    """Controls the lifecycle of the JARVIS application."""

    def __init__(self):
        self.config = JarvisConfig()
        self.logger = create_logger(self.config.logs_dir)

        self.running = False

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
        """Process a basic command."""

        command = command.strip()

        if not command:
            return "I didn't receive a command."

        if command.lower() in {"hello", "hello jarvis", "hi"}:
            return "Hello. JARVIS is online and ready."

        if command.lower() in {"status", "system status"}:
            return self.config.summary()

        if command.lower() in {"help", "commands"}:
            return (
                "Available commands:\n"
                "  help   - Show available commands\n"
                "  status - Show JARVIS system information\n"
                "  hello  - Test JARVIS\n"
                "  exit   - Shut down JARVIS"
            )

        return (
            f"I received: '{command}'\n"
            "I don't have a tool for that yet."
        )

    def shutdown(self):
        """Stop JARVIS cleanly."""

        self.logger.info("Shutting down JARVIS runtime.")

        self.running = False

        print()
        print("JARVIS shutting down...")
        print("JARVIS offline.")

        self.logger.info("JARVIS runtime stopped.")