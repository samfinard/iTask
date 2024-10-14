from send_message import send_message
import os
from dotenv import load_dotenv


def main() -> None:
    phone_numbers = os.getenv("PHONE_NUMBERS").split(",")
    for number in phone_numbers:
        send_message("test", number)


if __name__ == "__main__":
    load_dotenv()
    main()
