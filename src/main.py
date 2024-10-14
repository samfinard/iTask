from send_message import MessageBot


def main() -> None:
    message_bot = MessageBot()
    message_bot.send_imessage("Hello World", ["9174992545", "7183950316"])


if __name__ == "__main__":
    main()
