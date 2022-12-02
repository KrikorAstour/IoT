import sqlite3

con = sqlite3.connect('people.db')
c = con.cursor()

c.execute(""" INSERT INTO users (tag_num, "temp", humidity, light_intensity) VALUES ('e3 24 5d 0d', 20, 30, 300)""")

con.commit()
con.close()

