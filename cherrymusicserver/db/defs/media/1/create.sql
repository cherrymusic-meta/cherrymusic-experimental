CREATE TABLE _tagtypes(
	typeid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	type TEXT NOT NULL UNIQUE,
	groupname TEXT,
	count INTEGER DEFAULT 0
);

CREATE TABLE _texts(
	textid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	textdata TEXT NOT NULL UNIQUE,
	count INTEGER DEFAULT 0
);

CREATE TABLE _tags(
	tagid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	typeid INTEGER NOT NULL,
	textid INTEGER NOT NULL,
	userid INTEGER NOT NULL,
	public INTEGER DEFAULT 0,
	count INTEGER DEFAULT 0
);
CREATE UNIQUE INDEX uidx__tags_typeid_textid_userid ON _tags(typeid, textid, userid);

CREATE TABLE tracks(
	trackid INTEGER PRIMARY KEY NOT NULL DEFAULT (lower(hex(randomblob(16)))),
	content TEXT
);

CREATE TABLE _taggeds(
	tgdid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	tagid INTEGER NOT NULL,
	trackid INTEGER NOT NULL,
	seq INTEGER
);
CREATE UNIQUE INDEX uidx__tagged_tagid_trackid ON _taggeds(tagid, trackid);


-----
-- VIEWS
-----

CREATE VIEW tags AS
	SELECT tgdid as "id", tagid, textdata as "text", type, groupname, userid, public, seq, trackid FROM _tags
		JOIN _texts USING (textid)
		JOIN _tagtypes USING (typeid)
		JOIN _taggeds USING (tagid)
		JOIN tracks USING (trackid)
;

-----
-- TRIGGERS
-----


-- TAGS

CREATE TRIGGER trigger__tags_after_insert_count_tagtype_and_text AFTER INSERT ON _tags
FOR EACH ROW BEGIN
	UPDATE _tagtypes SET count = count + 1 WHERE typeid = new.typeid;
	UPDATE _texts SET count = count + 1 WHERE textid = new.textid;
END;

CREATE TRIGGER trigger__tags_after_delete_uncount_tagtype_and_text AFTER DELETE ON _tags
FOR EACH ROW BEGIN
	UPDATE _tagtypes SET count = count - 1 WHERE typeid = old.typeid;
	UPDATE _texts SET count = count - 1 WHERE textid = old.textid;
END;


-- TAGGEDS

CREATE TRIGGER trigger__taggeds_after_insert_count_tags AFTER INSERT on _taggeds
FOR EACH ROW BEGIN
	UPDATE _tags SET count = count + 1 WHERE tagid = new.tagid;
END;

CREATE TRIGGER trigger__taggeds_after_delete_uncount_tags AFTER DELETE on _taggeds
FOR EACH ROW BEGIN
	UPDATE _tags SET count = count - 1 WHERE tagid = old.tagid;
	DELETE FROM _tags WHERE count < 1;
END;


-- TAG VIEW

CREATE TRIGGER trigger_tags_insert INSTEAD OF INSERT on tags
	FOR EACH ROW BEGIN
		INSERT OR IGNORE INTO _tagtypes(type, groupname) VALUES (new.type, new.groupname);
		INSERT OR IGNORE INTO _texts(textdata) VALUES (new.text);
		INSERT OR IGNORE INTO _tags(tagid, typeid, textid, userid) VALUES (
			(SELECT tagid FROM _tags WHERE
				typeid = (SELECT typeid FROM _tagtypes WHERE type = new.type) AND
				textid=(SELECT textid FROM _texts WHERE textdata = new.text) AND
				userid=new.userid),
			(SELECT typeid FROM _tagtypes WHERE type = new.type),
			(SELECT textid FROM _texts WHERE textdata = new.text),
			new.userid
		);
		UPDATE _tags SET public = new.public
			WHERE tagid = (SELECT tagid FROM _tags WHERE
				typeid = (SELECT typeid FROM _tagtypes WHERE type = new.type) AND
				textid=(SELECT textid FROM _texts WHERE textdata = new.text) AND
				userid=new.userid);
		INSERT INTO _taggeds(tagid, trackid, seq) VALUES (
			(SELECT tagid FROM _tags WHERE
				typeid = (SELECT typeid FROM _tagtypes WHERE type = new.type) AND
				textid=(SELECT textid FROM _texts WHERE textdata = new.text) AND
				userid=new.userid),
			new.trackid,
			new.seq
		);
	END
;

CREATE TRIGGER trigger_tags_update INSTEAD OF UPDATE on tags
FOR EACH ROW
BEGIN
	UPDATE _tags SET public = new.public WHERE tagid = new.tagid;
	UPDATE _taggeds SET seq = new.seq WHERE tgdid = new.id;
END;

CREATE TRIGGER trigger_tags_delete INSTEAD OF DELETE on tags
FOR EACH ROW
BEGIN
	DELETE FROM _taggeds WHERE tgdid = old.id;
END;
