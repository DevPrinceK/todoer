DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS todo;

CREATE TABLE user (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  username TEXT UNIQUE NOT NULL,
  password TEXT NOT NULL
);

CREATE TABLE todo (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  -- duedate TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  duedate DATE NOT NULL,
  sts TEXT NOT NULL, -- status
  title TEXT NOT NULL,
  detail TEXT NOT NULL,
  FOREIGN KEY (author_id) REFERENCES user (id)
);