import sqlite3
import logging
import json


def tuple2dict(raw_tuple):
    msg_type = "Common"
    response_dict = {
        "text": raw_tuple[0],
        "timestamp": raw_tuple[1],
        "msg_type": msg_type,
        "id": raw_tuple[-1]
    }
    if raw_tuple[0].startswith('Вход в СберБанк'):
        msg_type = "Enter notify"
    if 'Покупка' in raw_tuple[0]:
        msg_type = "Purchase"
    if "Перевод" in raw_tuple[0]:
        # Сбербанковский внутренний
        words = raw_tuple[0].split(' ')
        if "Перевод от" in raw_tuple[0]:
            msg_type = "Income"
            sender = words[3] + words[4]

        else:
            msg_type = "Outcome"
            sender = "me"

        response_dict["sender"] = sender

    response_dict["msg_type"] = msg_type
    return response_dict


class DB_manager:

    def __init__(self):
        self.connect = sqlite3.connect("sms.db")
        self.cur = self.connect.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS messages(message TEXT, timestamp TEXT, type TEXT, status TEXT);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS incorrect_messages(message TEXT);")
        self.connect.commit()

    def handle_msg(self, sms):
        logging.error(sms)
        try:
            self.cur.execute("""
                INSERT INTO messages VALUES
                    (?, ?, "common", "new");
            """, (sms["text"], sms["sentStamp"]))
            self.connect.commit()
        except Exception as e:
            logging.error(f"incorrect sms {e}")
            sms_as_text = json.dumps(sms, ensure_ascii=False).encode('utf8')
            self.cur.execute("""
                INSERT INTO incorrect_messages VALUES
                    (?);
            """, (sms_as_text,)
            )
            self.connect.commit()
        return 0


    def get_all_sms(self):
        return self.cur.execute("""
            SELECT * FROM messages;
        """).fetchall()


    def get_new_sms(self):
        return [tuple2dict(line) for line in self.cur.execute("""
            SELECT message, timestamp, type, status, rowid FROM messages WHERE status="new";
        """)]

    def get_incorrect_sms(self):
        logging.error(self.cur.execute('SELECT * FROM incorrect_messages;').fetchall())
        return [line[0] for line in self.cur.execute("""
            SELECT * FROM incorrect_messages;
        """)]

    def mark_as_read(self, sms_ids):
        mark_as_read_query = """UPDATE messages SET status = "readed" WHERE rowid = ?;"""
        try:
            self.cur.executemany(mark_as_read_query, [(sms,) for sms in sms_ids])
            self.connect.commit()
        except Exception as e:
            logging.error(e)
            raise e

    def delete_read_sms(self):
        self.cur.execute(""" DELETE FROM messages WHERE status = "read";""")
        self.connect.commit()


