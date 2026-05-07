CREATE TABLE usuarios (
    id INT PRIMARY KEY,
    nome VARCHAR(100),
    email VARCHAR(100)
);

INSERT INTO usuarios (id, nome, email) VALUES (1, 'Admin', 'admin@ucb.br');
SET @root_password = 'WEBMASTER20@';

INSERT INTO usuarios (id, nome, email) VALUES (1, 'Admin', 'admin@catolica.edu.br');
SET @root_password = 'ZGE2MzhhYWQyMzBlMTllZjlhYmYwZmYxZjU2M2M3M2FmMWFiZGZmNTdmMTcwMDA5Zjc1ZDFiNzkyOTZlMmY0ZA';
