SELECT
  city,
  COUNT(*) AS completed_trips,
  SUM(fare_amount) AS gmv
FROM trip_state
WHERE status = 'completed'
GROUP BY city
ORDER BY gmv DESC;
