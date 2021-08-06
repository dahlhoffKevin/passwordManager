DROP DATABASE IF EXISTS SQL0002;
CREATE DATABASE SQL0002
 CHARACTER SET utf8mb4
 COLLATE utf8mb4_german2_ci
;

USE SQL0002;

CREATE TABLE users (
 user_id  INT,
 username VARCHAR(255),
 password VARCHAR(255),
 email    VARCHAR(255),
 name     VARCHAR(255),
 lastname VARCHAR(255),
 time     TIME,
 date     DATE,
 PRIMARY KEY(user_id)
);

CREATE TABLE infos (
 author  VARCHAR(255),
 version FLOAT
);

INSERT INTO infos
 SET 
  author='Crancki',
  version=1.1
;