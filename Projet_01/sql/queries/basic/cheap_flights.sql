-- Vols dont le prix est inférieur à un seuil donné, triés par prix croissant.
SELECT flight_number, destination, price_eur
FROM flights
WHERE price_eur < :max_price
ORDER BY price_eur;
