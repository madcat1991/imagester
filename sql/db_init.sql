-- initial
-- $ createuser imagester -e -P -s
-- $ createdb -e -E UTF8 -O imagester imagester

-- table of requests
DROP TABLE IF EXISTS request CASCADE;
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
  tags TEXT[] NOT NULL,
  loc_tags TEXT[] NOT NULL,
  quotes TEXT[] NOT NULL,
  time_in_24h TIMESTAMP NOT NULL,
  time_closest TIMESTAMP NOT NULL,
  dt TIMESTAMP NOT NULL DEFAULT now()
)
WITH (
  OIDS=FALSE
);
ALTER TABLE processed_request OWNER TO imagester;
