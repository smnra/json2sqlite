import sqlite3





conn = sqlite3.connect(u'安全考试.db')
c = conn.cursor()


cursor = c.execute("select * from question_list where rightflag = '0'")
wrongflag = [row[0] for row in cursor]



