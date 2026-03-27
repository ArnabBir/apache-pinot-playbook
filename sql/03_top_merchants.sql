SELECT
  merchant_id,
  merchant_name,
  city,
  COUNT(*) AS completed_trips,
  SUM(fare_amount) AS revenue
FROM trip_state
WHERE status = 'completed'
GROUP BY merchant_id, merchant_name, city
ORDER BY revenue DESC
LIMIT 20;
