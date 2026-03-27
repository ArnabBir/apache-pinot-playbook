SELECT
  last_event_minute_bucket_ms AS bucket_start_ms,
  SUM(fare_amount) AS gmv
FROM trip_state
WHERE status = 'completed'
GROUP BY last_event_minute_bucket_ms
ORDER BY bucket_start_ms;
