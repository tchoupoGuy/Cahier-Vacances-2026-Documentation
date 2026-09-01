-- Passagers confirmés sur un vol donné (numéro de vol), avec classe et siège.
SELECT passengers.first_name, passengers.last_name, bookings.seat_class, bookings.seat_number
FROM passengers
JOIN bookings ON passengers.id = bookings.passenger_id
JOIN flights ON bookings.flight_id = flights.id
WHERE flights.flight_number = :flight_number
  AND bookings.status = 'confirmed';
