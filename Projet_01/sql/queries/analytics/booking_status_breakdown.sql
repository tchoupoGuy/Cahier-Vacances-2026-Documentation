-- Nombre de réservations par statut (confirmed / cancelled / pending).
SELECT status, COUNT(*) AS count
FROM bookings
GROUP BY status
ORDER BY count DESC;
