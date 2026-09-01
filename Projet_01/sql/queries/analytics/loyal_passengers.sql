-- Passagers ayant au moins N réservations (tous statuts confondus) : les clients fidèles.
SELECT passengers.first_name, passengers.last_name, COUNT(*) AS nb_bookings
FROM passengers
JOIN bookings ON passengers.id = bookings.passenger_id
GROUP BY passengers.id
HAVING COUNT(*) >= :min_bookings;
