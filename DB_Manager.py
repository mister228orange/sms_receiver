import sqlite3
import logging
import json


def tuple2dict(raw_tuple):
    return {
            "text": raw_tuple[0],
            "timestamp": raw_tuple[1]
        }


class DB_manager:

    def __init__(self):
        self.connect = sqlite3.connect("sms.db")
        self.cur = self.connect.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS messages(text, timestamp, type, status);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS incorrect_messages(text);")

    def handle_msg(self, sms):
        logging.error(sms)
        try:
            self.cur.execute("""
                INSERT INTO messages VALUES
                    (?, ?, "common", "new");
            """, (sms["text"], sms["sentStamp"]))
        except Exception as e:
            logging.error(f"incorrect sms {e}")
            sms_as_text = json.dumps(sms)
            self.cur.execute("""
                INSERT INTO incorrect_messages VALUES
                    (?);
            """, (sms_as_text,)
            )
        return 0


    def get_all_sms(self):
        return self.cur.execute("""
            SELECT * FROM messages;
        """).fetchall()


    def get_new_sms(self):
        return [tuple2dict(line) for line in self.cur.execute("""
            SELECT * FROM messages WHERE status="new";
        """)]

