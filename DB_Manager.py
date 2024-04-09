import sqlite3
import logging
import json
import re
from config import cfg


src_mapping = {str(src.NUMBER): src.NAME for src in cfg.SOURCES}


def tuple2dict(raw_tuple):
    income_patterns = [
        r'MIR-9202 (?P<time>\d{2}:\d{2}) Перевод (?P<amount>\d+(\.\d+){0,1})р от (?P<sender> \w+( \w+){0,1,2}\.) Баланс: (?P<updated_balance>\d+(\.\d+){0,1})р',
        r'СЧЁТ(?P<card>\d{4}) (?P<time>\d{2}:\d{2}) зачисление (?P<amount>\d+(\.\d+){0,1})р \w+( \w+)* Баланс: (?P<balance>\d+(\.\d+){0,1})р',
        r'MIR-(?P<card>\d{4}) (?P<time>\d{2}:\d{2}) Перевод (?P<amount>\d+(\.\d+){0,1})р от \w+( \w\.)* Баланс: (?P<balance>\d+(\.\d+){0,1})р',
        r'Popolnenie \*\*4151 na (?P<amount>\d{1,3}( \d{3})*(\,\d{1,2})?) RUR Balans (?P<balance>\d{1,3}( \d{3})*(\,\d{1,2})?) RUR (?P<date>\d{2}\.\d{2}\.\d{4}) (?P<time>\d{2}:\d{2})',
        r'Поступление (?P<amount>\d+(\.\d+){0,1}) RUR по СБП от (?P<sender> \w+( \w+){0,1,2}\.)',
        r'MIR-9202 (?P<time>\d{2}:\d{2}) зачисление (?P<amount>\d+(\.\d+){0,1})р C2C \w+( \w+){0,2} Баланс: (?P<updated_balance>\d+(\.\d+){0,1})р'
    ]

    for pattern in income_patterns:
        try:
            # m = re.fullmatch(pattern, raw_tuple[0])
            m = re.match(pattern, raw_tuple[0])
            if m is not None:
                return {
                    "text": raw_tuple[0],
                    "timestamp": raw_tuple[1],
                    "msg_type": "Income",
                    "amount": m.group('amount'),
                    "src": src_mapping[raw_tuple[-2]],
                    "id": raw_tuple[-1]
                }
        except Exception as e:
            print(e)
            continue
    return {
            "text": raw_tuple[0],
            "timestamp": raw_tuple[1],
            "msg_type": "Other",
            "src": src_mapping[raw_tuple[-2]],
            "id": raw_tuple[-1]
        }



class DB_manager:

    def __init__(self):
        self.connect = sqlite3.connect("sms.db")
        self.cur = self.connect.cursor()
        self.cur.execute("CREATE TABLE IF NOT EXISTS messages(message TEXT, timestamp TEXT, type TEXT, source TEXT, status TEXT);")
        self.cur.execute("CREATE TABLE IF NOT EXISTS incorrect_messages(message TEXT);")
        self.connect.commit()

    def handle_msg(self, sms):
        logging.error(sms)
        try:
            self.cur.execute("""
                INSERT INTO messages VALUES
                    (?, ?, "common", ?, "new");
            """, (sms["text"], sms["sentStamp"], sms["from"]))
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


    def get_all_sms(self, src=None):
        if src in src_mapping:
            return self.cur.execute("""
                SELECT * FROM messages WHERE source=?;
            """, src_mapping[src]).fetchall()

        return self.cur.execute("""
            SELECT * FROM messages;
        """).fetchall()

    def get_new_sms(self, src=None):
        if src in src_mapping:
            return [tuple2dict(line) for line in self.cur.execute("""
                SELECT message, timestamp, type, status, source, rowid  FROM messages WHERE status="new" AND source=?;
            """, src_mapping[src])]
        return [tuple2dict(line) for line in self.cur.execute("""
            SELECT message, timestamp, type, status, source, rowid FROM messages WHERE status="new";
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


