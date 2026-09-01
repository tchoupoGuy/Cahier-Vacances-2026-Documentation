-- Schéma de la base de réservations de vols (Projet 01)
-- Trois tables reliées entre elles par des clés étrangères :
-- passengers <-- bookings --> flights

CREATE TABLE passengers (
    id          INTEGER PRIMARY KEY,
    first_name  TEXT NOT NULL,
    last_name   TEXT NOT NULL,
    email       TEXT UNIQUE,
    nationality TEXT
);

CREATE TABLE flights (
    id             INTEGER PRIMARY KEY,
    flight_number  TEXT NOT NULL,
    origin         TEXT NOT NULL,
    destination    TEXT NOT NULL,
    departure_time TEXT NOT NULL,
    arrival_time   TEXT NOT NULL,
    aircraft       TEXT,
    capacity       INTEGER,
    price_eur      REAL
);

CREATE TABLE bookings (
    id            INTEGER PRIMARY KEY,
    passenger_id  INTEGER,
    flight_id     INTEGER,
    booking_date  TEXT,
    seat_class    TEXT,
    seat_number   TEXT,
    status        TEXT,
    FOREIGN KEY (passenger_id) REFERENCES passengers(id),
    FOREIGN KEY (flight_id) REFERENCES flights(id),
    CHECK (seat_class IN ('economy', 'business', 'first')),
    CHECK (status IN ('confirmed', 'cancelled', 'pending'))
);
