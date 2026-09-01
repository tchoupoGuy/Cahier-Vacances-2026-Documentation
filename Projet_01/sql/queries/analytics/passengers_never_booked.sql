-- Passagers présents dans la base mais qui n'ont jamais fait de réservation
-- (LEFT JOIN + filtre sur NULL = les "orphelins" côté droit).
SELECT passengers.first_name, passengers.last_name
FROM passengers
LEFT JOIN bookings ON passengers.id = bookings.passenger_id
WHERE bookings.passenger_id IS NULL;
