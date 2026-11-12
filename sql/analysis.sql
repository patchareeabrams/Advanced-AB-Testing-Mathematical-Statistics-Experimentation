-- Load data into a table named experiment(user_id, variant, converted).
SELECT variant, COUNT(*) AS visitors, SUM(converted) AS purchases,
       ROUND(100.0 * AVG(converted), 2) AS conversion_rate_pct
FROM experiment
GROUP BY variant
ORDER BY variant;

-- Data quality: users assigned more than once
SELECT user_id, COUNT(*) AS assignments
FROM experiment GROUP BY user_id HAVING COUNT(*) > 1;
