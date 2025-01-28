-- schema.sql

-- Create the database if it does not exist
CREATE DATABASE IF NOT EXISTS user_authentication;

-- Select the database to use
USE user_authentication;

-- Create a table for storing user information
CREATE TABLE users (
  id INT AUTO_INCREMENT PRIMARY KEY,  -- Unique identifier 70132252 for each user
  full_name VARCHAR(255) NOT NULL,    -- User's full name
  email VARCHAR(255) UNIQUE NOT NULL, -- User's email address, must be unique
  password VARCHAR(255) NOT NULL      -- User's hashed password
);
