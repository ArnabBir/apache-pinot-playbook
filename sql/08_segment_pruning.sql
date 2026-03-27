SELECT
  city,
  COUNT(*) AS rows_scanned_candidate
FROM trip_events
WHERE city = 'bengaluru'
  AND event_time_ms BETWEEN 1767225600000 AND 1767232800000
GROUP BY city;
