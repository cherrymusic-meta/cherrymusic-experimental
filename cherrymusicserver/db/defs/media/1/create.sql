CREATE TABLE _tagtypes(
	typeid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	type TEXT NOT NULL UNIQUE,
	groupname TEXT,
	count INTEGER DEFAULT 0
);

CREATE TABLE tracks(
	trackid INTEGER PRIMARY KEY NOT NULL DEFAULT (lower(hex(randomblob(16)))),
	content TEXT
);

CREATE TABLE tags(
	tgid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	tagid INTEGER DEFAULT 0,
	"text" TEXT,
	"type" TEXT,
	"groupname" TEXT,
	userid INTEGER,
	public INTEGER,
	seq INTEGER,
	trackid INTEGER
);

-----
-- VIEWS
-----


-----
-- TRIGGERS
-----


