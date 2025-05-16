CREATE KEYSPACE IF NOT EXISTS fintech
WITH REPLICATION = { 'class': 'SimpleStrategy', 'replication_factor': 1 };

USE fintech;

DROP TABLE IF EXISTS sensor_readings;

CREATE TABLE IF NOT EXISTS sensor_readings (
  sensor_id UUID,
  timestamp timestamp,
  tipo text,
  valores map<text, float>,
  PRIMARY KEY (sensor_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
