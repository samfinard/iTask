import subprocess


def format_phone_number(number: str) -> str:
    """
    Format phone number to ensure it starts with +1 (for US numbers).
    """
    return f"+1{number}" if not number.startswith("+") else number


def send_message(message: str, phone_number: str) -> None:
    """
    Send a message to a single contact using AppleScript.
    """
    phone_number = format_phone_number(phone_number)

    # Ensure single quotes in the message are properly escaped
    escaped_message = message.replace("'", "\\'")

    script = f"""
    osascript -e 'tell application "Messages"
    set targetBuddy to a reference to (get buddy "{phone_number}")
    send "{escaped_message}" to targetBuddy
    end tell'
    """

    subprocess.run(script, shell=True)
