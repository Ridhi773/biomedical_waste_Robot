-- Biomedical Waste Robot - full database schema
-- This DROPS and recreates every table so it's safe to run fresh even if
-- an older/partial version of this schema already exists on your server.
-- Run with:  python setup_db.py   (see project root)

CREATE DATABASE IF NOT EXISTS biomedical_waste_robot;
USE biomedical_waste_robot;

SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS qr_verifications;
DROP TABLE IF EXISTS transports;
DROP TABLE IF EXISTS destinations;
DROP TABLE IF EXISTS drivers;
DROP TABLE IF EXISTS complaints;
DROP TABLE IF EXISTS admin;
DROP TABLE IF EXISTS alerts;
DROP TABLE IF EXISTS collections;
DROP TABLE IF EXISTS compartments;
DROP TABLE IF EXISTS robots;
DROP TABLE IF EXISTS waste_types;
DROP TABLE IF EXISTS locations;

SET FOREIGN_KEY_CHECKS = 1;

CREATE TABLE locations (
    location_id     INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    building        VARCHAR(100),
    floor           VARCHAR(20),
    description     VARCHAR(255)
);

CREATE TABLE waste_types (
    waste_type_id   INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    category        ENUM('sharps', 'infectious', 'pathological', 'chemical', 'general') NOT NULL,
    hazard_level    ENUM('low', 'medium', 'high', 'critical') NOT NULL DEFAULT 'medium'
);

CREATE TABLE robots (
    robot_id            INT AUTO_INCREMENT PRIMARY KEY,
    name                VARCHAR(100) NOT NULL,
    status              ENUM('idle', 'collecting', 'charging', 'error', 'manual') NOT NULL DEFAULT 'idle',
    battery_level       DECIMAL(5,2) NOT NULL DEFAULT 100.00,
    current_location_id INT,
    last_updated        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (current_location_id) REFERENCES locations(location_id) ON DELETE SET NULL
);

CREATE TABLE compartments (
    compartment_id   INT AUTO_INCREMENT PRIMARY KEY,
    robot_id         INT NOT NULL,
    waste_type_id    INT NOT NULL,
    capacity_kg      DECIMAL(6,2) NOT NULL DEFAULT 10.00,
    current_fill_kg  DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    status           ENUM('empty', 'partial', 'full') NOT NULL DEFAULT 'empty',
    qr_code          VARCHAR(64) UNIQUE,
    FOREIGN KEY (robot_id) REFERENCES robots(robot_id) ON DELETE CASCADE,
    FOREIGN KEY (waste_type_id) REFERENCES waste_types(waste_type_id)
);

CREATE TABLE collections (
    collection_id   INT AUTO_INCREMENT PRIMARY KEY,
    robot_id        INT NOT NULL,
    compartment_id  INT NOT NULL,
    location_id     INT,
    waste_type_id   INT NOT NULL,
    weight_kg       DECIMAL(6,2) NOT NULL,
    collected_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (robot_id) REFERENCES robots(robot_id) ON DELETE CASCADE,
    FOREIGN KEY (compartment_id) REFERENCES compartments(compartment_id) ON DELETE CASCADE,
    FOREIGN KEY (location_id) REFERENCES locations(location_id) ON DELETE SET NULL,
    FOREIGN KEY (waste_type_id) REFERENCES waste_types(waste_type_id)
);

CREATE TABLE alerts (
    alert_id      INT AUTO_INCREMENT PRIMARY KEY,
    robot_id      INT NOT NULL,
    alert_type    ENUM('compartment_full', 'low_battery', 'malfunction', 'route_blocked', 'qr_mismatch') NOT NULL,
    severity      ENUM('low', 'medium', 'high', 'critical') NOT NULL DEFAULT 'medium',
    message       VARCHAR(255) NOT NULL,
    created_at    DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved      BOOLEAN NOT NULL DEFAULT FALSE,
    resolved_at   DATETIME NULL,
    FOREIGN KEY (robot_id) REFERENCES robots(robot_id) ON DELETE CASCADE
);

CREATE TABLE admin (
    admin_id        INT AUTO_INCREMENT PRIMARY KEY,
    username        VARCHAR(50) UNIQUE NOT NULL,
    password_hash   VARCHAR(255) NOT NULL,
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE complaints (
    complaint_id    INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100),
    contact         VARCHAR(100),
    message         VARCHAR(500) NOT NULL,
    status          ENUM('open', 'resolved') NOT NULL DEFAULT 'open',
    created_at      DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    resolved_at     DATETIME NULL
);

CREATE TABLE drivers (
    driver_id       INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    phone           VARCHAR(30),
    license_no      VARCHAR(50),
    status          ENUM('available', 'on_duty', 'off_duty') NOT NULL DEFAULT 'available'
);

CREATE TABLE destinations (
    destination_id  INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(100) NOT NULL,
    qr_code         VARCHAR(64) UNIQUE NOT NULL,
    description     VARCHAR(255)
);

CREATE TABLE transports (
    transport_id     INT AUTO_INCREMENT PRIMARY KEY,
    robot_id         INT NOT NULL,
    compartment_id   INT NOT NULL,
    driver_id        INT NULL,
    destination_id   INT NULL,
    status           ENUM('pending', 'assigned', 'in_progress', 'pickup_verified', 'completed', 'cancelled')
                     NOT NULL DEFAULT 'pending',
    requested_at     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    started_at       DATETIME NULL,
    completed_at     DATETIME NULL,
    FOREIGN KEY (robot_id) REFERENCES robots(robot_id) ON DELETE CASCADE,
    FOREIGN KEY (compartment_id) REFERENCES compartments(compartment_id) ON DELETE CASCADE,
    FOREIGN KEY (driver_id) REFERENCES drivers(driver_id) ON DELETE SET NULL,
    FOREIGN KEY (destination_id) REFERENCES destinations(destination_id) ON DELETE SET NULL
);

CREATE TABLE qr_verifications (
    qr_verification_id  INT AUTO_INCREMENT PRIMARY KEY,
    transport_id         INT NOT NULL,
    stage                ENUM('pickup', 'destination') NOT NULL,
    scanned_code          VARCHAR(64) NOT NULL,
    expected_code         VARCHAR(64) NOT NULL,
    result                ENUM('match', 'mismatch') NOT NULL,
    verified_at           DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (transport_id) REFERENCES transports(transport_id) ON DELETE CASCADE
);
