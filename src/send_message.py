import subprocess


def format_phone_number(number: str) -> str:
    """
    Format phone number to ensure it start with +1 (for US numbers).
    """
    return f"+1{number}" if not number.startswith("+") else number


def send_message(message: str, phone_number: str) -> None:
    """
    Send a message to a single contact.
    """
    phone_number = format_phone_number(phone_number)
    script = f"""
    osascript -e 'tell application "Messages"
    set targetBuddy to a reference to (get buddy "{phone_number}")
    send "{message}" to targetBuddy    
    """
    subprocess.run(script, shell=True)
