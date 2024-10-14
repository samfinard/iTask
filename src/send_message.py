import subprocess
import os
import sqlite3
import platform


def format_phone_numbers(numbers: list[str]) -> list[str]:
    """
    Format phone numbers to ensure they start with +1 (for US numbers).
    """
    return [
        f"+1{number}" if not number.startswith("+") else number for number in numbers
    ]


class MessageBot:
    def __init__(self):
        if platform.system() != "Darwin":
            raise ValueError("This script is intended to run on macOS.")
        self.db_path = os.path.expanduser("~/Library/Messages/chat.db")

    def send_imessage(self, message: str, phone_numbers: list[str]) -> None:
        """
        Send an iMessage to either a single contact or a group chat.
        """
        phone_numbers = format_phone_numbers(phone_numbers)
        if len(phone_numbers) == 1:
            self.send_to_one(message, number=phone_numbers[0])
        else:
            group_chat_id = self._get_group_chat_id(phone_numbers)
            if group_chat_id:
                self.send_to_group(message, group_chat_id)
            else:
                print(f"No group chat found with {phone_numbers}")

    def send_to_one(self, message: str, number: str) -> None:
        """
        Send a message to a single contact.
        """
        script = f"""
        osascript -e 'tell application "Messages"
        set targetBuddy to a reference to (get buddy "{number}")
        send "{message}" to targetBuddy
        end tell'
        """
        subprocess.run(script, shell=True)

    def send_to_group(self, message: str, group_chat_id: str) -> None:
        """
        Send a message to a group chat with the given group chat ID.
        """
        script = f"""
        osascript -e 'tell application "Messages"
        send "{message}" to chat id "{group_chat_id}"
        end tell'
        """
        subprocess.run(script, shell=True)

    def _get_group_chat_id(self, phone_numbers: list[str]) -> str | None:
        """
        Get the group chat ID for a group with the specified participants, or return None if not found.
        """
        phone_numbers_set = set(format_phone_numbers(phone_numbers))
        group_chat_id: str | None = None

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()

                # SQL query to get group chats
                cursor.execute("""
                    SELECT chat.chat_identifier
                    FROM chat
                    JOIN chat_handle_join AS chj ON chat.ROWID = chj.chat_id
                    JOIN handle ON chj.handle_id = handle.ROWID
                    WHERE chat.chat_identifier LIKE 'chat%' -- group chats only
                """)
                group_chat_ids = cursor.fetchall()

                # Check if any group chat contains the exact same participants
                for group_chat_id_tuple in group_chat_ids:
                    cursor.execute(
                        """
                        SELECT handle.id
                        FROM chat_handle_join AS chj
                        JOIN handle ON chj.handle_id = handle.ROWID
                        WHERE chj.chat_id = (SELECT ROWID FROM chat WHERE chat_identifier = ?)
                        """,
                        (group_chat_id_tuple[0],),
                    )
                    participants = cursor.fetchall()
                    participants_set = set([p[0] for p in participants])

                    # If the participants match, return the group chat ID
                    if participants_set == phone_numbers_set:
                        group_chat_id = group_chat_id_tuple[0]
                        break
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            raise e

        return group_chat_id
