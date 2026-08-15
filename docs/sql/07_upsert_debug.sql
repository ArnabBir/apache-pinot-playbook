SELECT
  trip_id,
  COUNT(*) AS versions_seen,
  MAX(event_version) AS max_version
FROM trip_events
GROUP BY trip_id
HAVING COUNT(*) > 1
ORDER BY versions_seen DESC
LIMIT 50;
