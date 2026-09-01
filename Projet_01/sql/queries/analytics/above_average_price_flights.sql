-- Vols dont le prix dépasse le prix moyen de l'ensemble des vols (sous-requête).
SELECT flight_number, destination, price_eur
FROM flights
WHERE price_eur > (SELECT AVG(price_eur) FROM flights);
