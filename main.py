from core.runtime import JarvisRuntime


def main():
    jarvis = JarvisRuntime()

    try:
        jarvis.start()

        while jarvis.running:
            command = input("You > ")

            if command.strip().lower() in {"exit", "quit", "shutdown"}:
                break

            response = jarvis.process_command(command)

            print()
            print(f"JARVIS > {response}")
            print()

    except KeyboardInterrupt:
        print("\nKeyboard interrupt received.")

    finally:
        jarvis.shutdown()


if __name__ == "__main__":
    main()