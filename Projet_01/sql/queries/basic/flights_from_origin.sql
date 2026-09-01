-- Liste des vols au départ d'une ville donnée, triés par heure de départ.
SELECT flight_number, destination, departure_time, price_eur
FROM flights
WHERE origin = :origin
ORDER BY departure_time;
