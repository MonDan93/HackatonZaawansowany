
DROP TABLE IF EXISTS "users";

CREATE TABLE "users"
(
    "id"     INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    "username"  TEXT    NOT NULL,
    "password"  TEXT    NOT NULL,
    "company"  TEXT


);

DROP TABLE IF EXISTS "rides";

CREATE TABLE "rides"
(
    "id" INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT UNIQUE,
    "user_id" INTEGER NOT NULL,
    "name" TEXT NOT NULL,
    "company" TEXT,
    "date" DATE NOT NULL,
    "km" DOUBLE NOT NULL,
     FOREIGN KEY ("user_id") REFERENCES "users" ("id")
     FOREIGN KEY ("company") REFERENCES "users" ("company")

);

INSERT INTO "users"
VALUES (1, 'nowy', 'pbkdf2:sha256:150000$EyGaYAph$e124af0868f258ebe768ec768893013d8cb29e82d43a648f5c6719d263abf9d7', 'Prokom')