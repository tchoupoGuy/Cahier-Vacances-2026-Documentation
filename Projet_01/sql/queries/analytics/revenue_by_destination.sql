-- Chiffre d'affaires et nombre de réservations confirmées, par destination.
SELECT flights.destination,
       SUM(flights.price_eur) AS total_revenue,
       COUNT(*)               AS nb_bookings
FROM flights
JOIN bookings ON flights.id = bookings.flight_id
WHERE bookings.status = 'confirmed'
GROUP BY flights.destination
ORDER BY total_revenue DESC;
