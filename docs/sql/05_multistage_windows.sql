SELECT *
FROM (
  SELECT
    city,
    merchant_id,
    merchant_name,
    SUM(fare_amount) AS gmv,
    RANK() OVER (
      PARTITION BY city
      ORDER BY SUM(fare_amount) DESC
    ) AS merchant_rank
  FROM trip_state
  WHERE status = 'completed'
  GROUP BY city, merchant_id, merchant_name
) ranked
WHERE merchant_rank <= 3
ORDER BY city, merchant_rank, gmv DESC;
