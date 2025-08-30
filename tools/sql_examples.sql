#CREATE DATABASE testDB;
show databases;
use testDB;
CREATE TABLE Persons_InfoTb (
         ID int NOT NULL,
         LastName varchar(255) NOT NULL,
         FirstName varchar(255),
         Age int,
         PRIMARY KEY (ID)
     );

INSERT INTO Persons_InfoTb VALUES (1, 'Zhang', 'San', 45);
INSERT INTO Persons_InfoTb VALUES (2, 'Li', 'Si', 35);
INSERT INTO Persons_InfoTb VALUES (3, 'Xigui', 'Wang', 50);
show tables;
select * from Persons_InfoTb;
