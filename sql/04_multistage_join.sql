SELECT
  t.city,
  m.vertical,
  m.contract_tier,
  COUNT(*) AS completed_trips,
  SUM(t.fare_amount) AS gmv
FROM trip_state t
JOIN merchants_dim m
  ON t.merchant_id = m.merchant_id
WHERE t.status = 'completed'
GROUP BY t.city, m.vertical, m.contract_tier
ORDER BY gmv DESC
LIMIT 50;
