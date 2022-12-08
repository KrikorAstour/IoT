import sqlite3

con = sqlite3.connect('people.db')
c = con.cursor()

c.execute(""" INSERT INTO users (tag_num, "temp", humidity, light_intensity) VALUES ('13 05 5e 0d', 23, 0, 200)""")

con.commit()
con.close()

