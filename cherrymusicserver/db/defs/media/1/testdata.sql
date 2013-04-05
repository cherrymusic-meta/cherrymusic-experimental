INSERT INTO _tagtypes(typeid, type, groupname) VALUES (1, 'artist', 'Artists');
INSERT INTO _tagtypes(typeid, type, groupname) VALUES (2, 'album', 'Albums');
INSERT INTO _tagtypes(typeid, type, groupname) VALUES (3, 'genre', 'Genres');
INSERT INTO _tagtypes(typeid, type, groupname) VALUES (4, 'playlist', 'Playlists');
INSERT INTO _tagtypes(typeid, type, groupname) VALUES (5, 'tag', 'Tags');
INSERT INTO _tagtypes(typeid, type, groupname) VALUES (6, 'filesystem', 'Files');

INSERT INTO _texts(textid, textdata) VALUES (1, 'madonna');
INSERT INTO _texts(textid, textdata) VALUES (2, 'true blue');
INSERT INTO _texts(textid, textdata) VALUES (3, 'lucky star');
INSERT INTO _texts(textid, textdata) VALUES (4, 'pop');
INSERT INTO _texts(textid, textdata) VALUES (5, 'madonna_-_true_blue_-_lucky_star.mp3');


INSERT INTO _tags(typeid, textid, userid, public) VALUES(1, 1, 0, 1);  --artist=madonna    1
INSERT INTO _tags(typeid, textid, userid, public) VALUES(2, 2, 0, 1);  --album=true blue   2
INSERT INTO _tags(typeid, textid, userid, public) VALUES(3, 4, 0, 1);  --genre=pop         3
INSERT INTO _tags(typeid, textid, userid, public) VALUES(6, 1, 0, 1);  --filesystem        4
INSERT INTO _tags(typeid, textid, userid, public) VALUES(6, 2, 0, 1);  --                  5
INSERT INTO _tags(typeid, textid, userid, public) VALUES(6, 5, 0, 1);  --                  6
INSERT INTO _tags(typeid, textid, userid, public) VALUES(4, 1, 1, 1);  --playlist          7
INSERT INTO _tags(typeid, textid, userid, public) VALUES(4, 4, 1, 0);  --                  8

INSERT INTO tracks(content) VALUES ('madonna_-_true_blue_-_lucky_star');  --1

INSERT INTO _taggeds(tagid, trackid, seq) VALUES (1, 1, NULL);
INSERT INTO _taggeds(tagid, trackid, seq) VALUES (2, 1, NULL);
INSERT INTO _taggeds(tagid, trackid, seq) VALUES (3, 1, NULL);
INSERT INTO _taggeds(tagid, trackid, seq) VALUES (4, 1, 1);
INSERT INTO _taggeds(tagid, trackid, seq) VALUES (5, 1, 2);
INSERT INTO _taggeds(tagid, trackid, seq) VALUES (6, 1, 3);
INSERT INTO _taggeds(tagid, trackid, seq) VALUES (7, 1, 1);
INSERT INTO _taggeds(tagid, trackid, seq) VALUES (8, 1, 1);

/*
ATTACH DATABASE ":memory:" AS mem;
CREATE TABLE mem.filesystem(
	fileid INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
	textid INTEGER NOT NULL,
	filetype TEXT,
	isdir INTEGER,
	parent INTEGER
	trackid INTEGER,
);
INSERT INTO mem.filesystem(fileid, textid, isdir, parent, trackid) VALUES (1, 1, 1, -1, NULL);
INSERT INTO mem.filesystem(fileid, textid, isdir, parent, trackid) VALUES (2, 2, 1, 1, NULL);
INSERT INTO mem.filesystem(fileid, textid, isdir, parent, trackid) VALUES (3, 5, 1, 1, NULL);
*/
