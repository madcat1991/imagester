-- initial
-- $ createuser imagester -e -P -s
-- $ createdb -e -E UTF8 -O imagester imagester

-- table of requests
DROP TABLE IF EXISTS request;
CREATE TABLE request
(
  id SERIAL PRIMARY KEY,
  email TEXT NOT NULL,
  img_dir TEXT NOT NULL,
  dt TIMESTAMP NOT NULL DEFAULT now(),
  is_processed BOOL NOT NULL DEFAULT FALSE
)
WITH (
  OIDS=FALSE
);
ALTER TABLE request OWNER TO imagester;

-- table of results
DROP TABLE IF EXISTS processed_request;
CREATE TABLE processed_request
(
  id SERIAL PRIMARY KEY,
  request_id INT NOT NULL REFERENCES request (id),
  img_path TEXT NOT NULL,
  hashtags TEXT[] NOT NULL,
  quotes TEXT[] NOT NULL,
  time_in_24h TIMESTAMP NOT NULL,
  time_closest TIMESTAMP NOT NULL
)
WITH (
  OIDS=FALSE
);
ALTER TABLE processed_request OWNER TO imagester;
