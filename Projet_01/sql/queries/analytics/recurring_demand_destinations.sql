-- Comme revenue_by_destination.sql, mais uniquement les destinations avec plus
-- d'une réservation confirmée : on écarte les destinations gonflées par une seule grosse vente.
SELECT flights.destination,
       SUM(flights.price_eur) AS total_revenue,
       COUNT(*)               AS nb_bookings
FROM flights
JOIN bookings ON flights.id = bookings.flight_id
WHERE bookings.status = 'confirmed'
  AND flights.destination IN (
        SELECT flights.destination
        FROM flights
        JOIN bookings ON flights.id = bookings.flight_id
        WHERE bookings.status = 'confirmed'
        GROUP BY flights.destination
        HAVING COUNT(*) > :min_bookings
  )
GROUP BY flights.destination
ORDER BY total_revenue DESC;
