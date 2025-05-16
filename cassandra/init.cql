CREATE KEYSPACE IF NOT EXISTS fintech
WITH REPLICATION = { 'class': 'SimpleStrategy', 'replication_factor': 1 };

USE fintech;

CREATE TABLE IF NOT EXISTS sensor_readings (
  sensor_id UUID,
  timestamp timestamp,
  tipo text,
  temperatura float,
  umidade float,
  pressao float,
  PRIMARY KEY (sensor_id, timestamp)
) WITH CLUSTERING ORDER BY (timestamp DESC);
