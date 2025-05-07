CREATE DATABASE stock_db;
USE stock_db;

CREATE TABLE stock (
    id INT AUTO_INCREMENT PRIMARY KEY,
    product_name VARCHAR(255),
    quantity INT,
    action ENUM('add', 'remove'),
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
