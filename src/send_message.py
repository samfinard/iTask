import subprocess
import os
import sqlite3


def format_phone_numbers(numbers: list[str]) -> list[str]:
    return [
        f"+1{number}" if not number.startswith("+") else number for number in numbers
    ]


class MessageBot:
    def __init__(self):
        self.db_path = os.path.expanduser("~/Library/Messages/chat.db")

    def send_imessage(self, message: str, phone_numbers: list[str]) -> None:
        phone_numbers = format_phone_numbers(phone_numbers)
        if len(phone_numbers) == 1:
            self.send_to_one(message, number=phone_numbers[0])
        else:
            group_chat_id = self._get_group_chat_id(phone_numbers)
            self.send_to_group(message, group_chat_id)

    def send_to_one(self, message: str, number: str) -> None:
        script = f"""
        osascript -e 'tell application "Messages"
        set targetBuddy to a reference to (get buddy "{number}")
        send "{message}" to targetBuddy
        end tell'
        """
        subprocess.run(script, shell=True)

    def send_to_group(self, message: str, group_chat_id: str) -> None:
        script = f"""
        osascript -e 'tell application "Messages"
        send "{message}" to chat id "{group_chat_id}"
        end tell'
        """
        subprocess.run(script, shell=True)

    def _get_group_chat_id(self, phone_numbers: list[str]) -> str | None:
        phone_numbers_set: set[str] = set(format_phone_numbers(phone_numbers))
        group_chat_id_tuple: str | None = None
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                            SELECT chat.chat_identifier
                            JOIN chat_handle_join AS chj ON chat.ROWID = chj.chat_id
                            JOIN handle ON chj.handle_id = handle.ROWID
                            WHERE chat.chat_identifier LIKE 'chat%' -- only group chats
                        """)
                group_chat_ids = cursor.fetchall()
                for group_chat_id_tuple in group_chat_ids:
                    cursor.execute(
                        """
                            SELECT chat_handle_join.handle_id
                            FROM chat_handle_join AS chj
                            JOIN handle ON chj.handle_id = handle.ROWID
                            WHERE chj.chat_id = (SELECT ROWID FROM chat WHERE chat_identifier = ?)
                        """,
                        (group_chat_id_tuple[0],),
                    )
                    participants = cursor.fetchall()
                    participants_set = set([p[0] for p in participants])
                    if participants_set == phone_numbers_set:
                        group_chat_id_tuple = group_chat_id_tuple[0]
                        break
        except sqlite3.Error as e:
            raise e
        finally:
            return group_chat_id_tuple
