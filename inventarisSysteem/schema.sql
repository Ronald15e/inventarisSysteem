DROP TABLE post;
DROP TABLE [user];

CREATE TABLE [user] (
  id int PRIMARY KEY identity(1,1),
  username varchar(50) NOT NULL,
  password varchar(50) NOT NULL
);

CREATE TABLE [post] (
  id INTEGER PRIMARY KEY identity(1,1),
  author_id INTEGER NOT NULL,
  created TIMESTAMP NOT NULL,
  title varchar(50) NOT NULL,
  body varchar(50) NOT NULL,
  FOREIGN KEY (author_id) REFERENCES [user](id)
);