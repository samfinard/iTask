from send_message import send_message


def main() -> None:
    for number in ["9173274878", "7183950316"]:
        send_message("test", number)


if __name__ == "__main__":
    main()
