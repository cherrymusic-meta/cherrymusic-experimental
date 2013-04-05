
CREATE TABLE users(
	userid INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
	name TEXT UNIQUE,	-- implies index
	admin INTEGER DEFAULT 0,
	password TEXT,
	salt TEXT
);

INSERT INTO users(userid, name) VALUES (0, 'system');
