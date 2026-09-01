-- Recherche d'un passager par son nom de famille.
SELECT *
FROM passengers
WHERE last_name = :last_name;
