--
-- File generated with SQLiteStudio v3.3.3 on Fri Dec 2 16:59:13 2022
--
-- Text encoding used: System
--
PRAGMA foreign_keys = off;
BEGIN TRANSACTION;

-- Table: user
CREATE TABLE user (tag_num PRIMARY KEY, "temp" INTEGER, humidity INTEGER, light_intensity INTEGER);
INSERT INTO user (tag_num, "temp", humidity, light_intensity) VALUES ('73 9c be 0d', -10, 0, 500);
INSERT INTO user (tag_num, "temp", humidity, light_intensity) VALUES ('e3 24 5d 0d', 20, 30, 300);

COMMIT TRANSACTION;
PRAGMA foreign_keys = on;