-- Sample data so the GUI has something to show immediately.

INSERT INTO locations (name, building, floor, description) VALUES
('Ward A - Nurse Station', 'Main Hospital', '1', 'General ward waste pickup point'),
('Ward B - ICU', 'Main Hospital', '2', 'ICU sharps and infectious waste point'),
('Operation Theatre 1', 'Surgical Block', 'G', 'Pathological and sharps waste'),
('Laboratory', 'Diagnostics Block', '1', 'Chemical and biohazard waste'),
('Charging Bay', 'Main Hospital', 'G', 'Robot charging and docking station');

INSERT INTO waste_types (name, category, hazard_level) VALUES
('Used Syringes', 'sharps', 'high'),
('Blood-soaked Gauze', 'infectious', 'high'),
('Anatomical Waste', 'pathological', 'critical'),
('Expired Reagents', 'chemical', 'medium'),
('General Biomedical Waste', 'general', 'low');

INSERT INTO robots (name, status, battery_level, current_location_id) VALUES
('BWR-01', 'idle', 96.00, 5),
('BWR-02', 'collecting', 78.50, 1);

INSERT INTO compartments (robot_id, waste_type_id, capacity_kg, current_fill_kg, status, qr_code) VALUES
(1, 1, 8.00, 0.50, 'partial', 'BIN-BWR01-01'),
(1, 3, 5.00, 0.00, 'empty',   'BIN-BWR01-02'),
(2, 2, 10.00, 6.20, 'partial', 'BIN-BWR02-01'),
(2, 5, 10.00, 1.00, 'partial', 'BIN-BWR02-02');

-- Seeded admin login: username 'admin', password 'admin123'
-- (MD5 for this demo only - swap for a real password hashing scheme before real use)
INSERT INTO admin (username, password_hash) VALUES
('admin', '0192023a7bbd73250516f069df18b500');

INSERT INTO drivers (name, phone, license_no, status) VALUES
('Ramesh Kumar', '9876500011', 'DL-0420110012345', 'available'),
('Suresh Yadav', '9876500022', 'DL-0420110067890', 'available');

INSERT INTO destinations (name, qr_code, description) VALUES
('Central Biomedical Disposal Facility', 'DEST-CENTRAL-01', 'Main incineration and autoclave facility'),
('Secondary Treatment Site', 'DEST-SECONDARY-01', 'Backup disposal site for overflow loads');
