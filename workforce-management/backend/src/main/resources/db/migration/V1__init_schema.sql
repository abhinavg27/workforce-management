
-- V1__init_schema.sql

CREATE TABLE worker (
    worker_id CHAR(7) PRIMARY KEY,
    worker_name VARCHAR(100) NOT NULL,
    age INT NOT NULL
);

CREATE TABLE skill_master (
    skill_id INT PRIMARY KEY,
    skill_name VARCHAR(100) NOT NULL,
    process_skill_sub_category_cd INT NOT NULL
);

CREATE TABLE worker_skill (
    worker_id CHAR(7) NOT NULL,
    skill_id INT NOT NULL,
    skill_level INT NOT NULL,
    productivity INT NOT NULL
);

CREATE TABLE shift_template (
    shift_id INT PRIMARY KEY,
    shift_name VARCHAR(50) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL
);

CREATE TABLE worker_shift (
    worker_id CHAR(7) NOT NULL,
    day_of_week VARCHAR(10) NOT NULL,
    shift_id INT NOT NULL
);

-- Example task table, update references to use worker_id if needed
CREATE TABLE task (
    id BIGINT PRIMARY KEY,
    skill_id INT NOT NULL,
    task_name VARCHAR(100) NOT NULL,
    task_type VARCHAR(20) NOT NULL,
    priority INT NOT NULL DEFAULT 0,
    dependent_task_id BIGINT NULL,
    task_count INT NOT NULL DEFAULT 1
);

CREATE TABLE assignment (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    worker_id CHAR(7) NOT NULL,
    task_id BIGINT NOT NULL,
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    feedback VARCHAR(255) DEFAULT NULL
);

-- Skill Master
INSERT INTO skill_master (skill_id, skill_name, process_skill_sub_category_cd) VALUES
(100, 'Receive', 7000),
(120, 'Stow', 7000),
(121, 'D2B', 7000),
(200, 'Pick_Paperless', 8000),
(211, 'Pick_Paper', 8000),
(220, 'Induction', 8001),
(221, 'DPS', 8001),
(230, 'Rebin_Manual', 8001),
(231, 'Rebin_DAS', 8001),
(240, 'Pack', 8002),
(260, 'Gift', 8002),
(250, 'Pick to Go Paperless', 8002),
(300, 'ShipSort', 7002),
(500, 'Maintenance', 3001),
(600, 'QA', 3001),
(400, 'Forklift', 3001),
(700, 'Management', 3002),
(243, 'Pack_Return', 8002),
(241, 'Pack_Paperless', 8002),
(242, 'Pack_Paper', 8002),
(251, 'Pick to Go Paper', 8002);
-- Set a default for any skills not matched above (optional)
UPDATE skill_master SET process_skill_sub_category_cd = 7000 WHERE process_skill_sub_category_cd IS NULL;


-- Shift Templates
INSERT INTO shift_template (shift_id, shift_name, start_time, end_time) VALUES
(1, 'Morning', '08:00:00', '16:00:00'),
(2, 'Evening', '16:00:00', '00:00:00'),
(3, 'Night', '00:00:00', '08:00:00'),
(4, 'Day Short', '09:00:00', '15:00:00'),
(5, 'Late Start', '10:00:00', '18:00:00');

-- worker sample data
INSERT INTO worker (worker_id,worker_name,age) VALUES
	 ('A1B2C3D','Alice Smith',28),
	 ('A1B2C3Q','Joe',25),
	 ('B1C2D3E','Beth Owen',31),
	 ('B4C5D6E','Nina Reed',24),
	 ('B7C8D9E','Gina Tate',30),
	 ('C1D2E3F','Usha Ives',33),
	 ('C4D5E6F','Hannah Scott',27),
	 ('C7D8E9F','Ava Nash',28),
	 ('D1E2F3G','Vik Jay',28),
	 ('D1E2F4G','Nate Cole',26);
INSERT INTO worker (worker_id,worker_name,age) VALUES
	 ('D4E5F6G','Iris Wood',30),
	 ('D7E8F9G','Uma Fox',32),
	 ('E4F5G6H','Bob Johnson',35),
	 ('F1G2H3I','Hugo Voss',31),
	 ('F4G5H6I','Carl Pike',29),
	 ('F7G8H9I','Oscar Price',36),
	 ('G1H2I3J','Ben Owen',34),
	 ('G4H5I6J','Vera Jay',28),
	 ('G7H8I9J','Ian Turner',34),
	 ('H1I2J3K','Victor Gray',30);
INSERT INTO worker (worker_id,worker_name,age) VALUES
	 ('H4I5J6K','Walt Kent',34),
	 ('H4I5J7K','Olga Drew',30),
	 ('H7I8J9K','Joel Xian',33),
	 ('I7J8K9L','Charlie Lee',41),
	 ('J1K2L3M','Paula Bell',29),
	 ('J4K5L6M','Ivy West',29),
	 ('J7K8L9M','Dana Reed',27),
	 ('K1L2M3N','Julia Evans',31),
	 ('K4L5M6N','Cara Page',27),
	 ('K7L8M9N','Will Kent',34);
INSERT INTO worker (worker_id,worker_name,age) VALUES
	 ('L1M2N3O','Kian Yule',29),
	 ('L4M5N6O','Wendy Hill',26),
	 ('L7M8N2O','Paul East',32),
	 ('L7M8N9O','Yani Long',25),
	 ('M1N2O3P','Diana King',30),
	 ('N1O2P3Q','Eli Snow',32),
	 ('N4O5P6Q','Quentin Ross',40),
	 ('N7O8P9Q','Jake York',33),
	 ('O1P2Q3R','Yuri Long',25),
	 ('O4P5Q6R','Kevin Harris',26);
INSERT INTO worker (worker_id,worker_name,age) VALUES
	 ('O7P8Q9R','Dean Quinn',36),
	 ('P1Q2R3S','Zed Moon',36),
	 ('P1Q2R4S','Rita Ford',29),
	 ('P4Q5R6S','Lila Zorn',27),
	 ('P7Q8R9S','Xander King',31),
	 ('Q4R5S6T','Evan Wright',25),
	 ('R1S2T3U','Kara Zane',27),
	 ('R4S5T6U','Fay Todd',28),
	 ('R7S8T9U','Rachel Ward',28),
	 ('S1T2U3V','Ella Rose',25);
INSERT INTO worker (worker_id,worker_name,age) VALUES
	 ('S4T5U6V','Zoe Moon',36),
	 ('S7T8U9V','Laura Young',33),
	 ('T1U2V3W','Yara Lane',33),
	 ('T4U5V6W','Sara Gale',31),
	 ('T7U8V9W','Mick Abel',31),
	 ('U7V8W9X','Fiona Adams',32),
	 ('V1W2X3Y','Sam Green',27),
	 ('V4W5X6Y','Liam Abel',28),
	 ('V7W8X9Y','Gus Upton',35),
	 ('W1X2Y3Z','Mike Baker',38);
INSERT INTO worker (worker_id,worker_name,age) VALUES
	 ('W4X5Y6Z','Finn Shaw',32),
	 ('W7X8Y9Z','Alan Neal',30),
	 ('X1Y2Z3A','Nora Bond',28),
	 ('X4Y5Z6A','Zane Moss',29),
	 ('X7Y8Z9A','Tom Hope',27),
	 ('Y1Z2A3B','George Clark',29),
	 ('Z1A2B3C','Hope Vale',26),
	 ('Z4A5B6C','Tina Hall',35),
	 ('Z7A8B9C','Mona Bond',35);

-- worker shift sample data
INSERT INTO worker_shift (worker_id,day_of_week,shift_id) VALUES
	 ('A1B2C3D','MONDAY',1),
	 ('A1B2C3D','TUESDAY',1),
	 ('A1B2C3D','WEDNESDAY',2),
	 ('A1B2C3D','THURSDAY',1),
	 ('A1B2C3D','FRIDAY',3),
	 ('E4F5G6H','MONDAY',2),
	 ('E4F5G6H','TUESDAY',2),
	 ('E4F5G6H','WEDNESDAY',2),
	 ('E4F5G6H','THURSDAY',3),
	 ('E4F5G6H','FRIDAY',1);
INSERT INTO worker_shift (worker_id,day_of_week,shift_id) VALUES
	 ('I7J8K9L','MONDAY',3),
	 ('I7J8K9L','TUESDAY',3),
	 ('I7J8K9L','WEDNESDAY',1),
	 ('I7J8K9L','THURSDAY',4),
	 ('I7J8K9L','FRIDAY',5),
	 ('M1N2O3P','MONDAY',1),
	 ('M1N2O3P','TUESDAY',1),
	 ('M1N2O3P','WEDNESDAY',2),
	 ('M1N2O3P','THURSDAY',1),
	 ('M1N2O3P','FRIDAY',3);
INSERT INTO worker_shift (worker_id,day_of_week,shift_id) VALUES
	 ('Q4R5S6T','MONDAY',2),
	 ('Q4R5S6T','TUESDAY',2),
	 ('Q4R5S6T','WEDNESDAY',2),
	 ('Q4R5S6T','THURSDAY',3),
	 ('Q4R5S6T','FRIDAY',1),
	 ('U7V8W9X','MONDAY',3),
	 ('U7V8W9X','TUESDAY',3),
	 ('U7V8W9X','WEDNESDAY',1),
	 ('U7V8W9X','THURSDAY',4),
	 ('U7V8W9X','FRIDAY',5);
INSERT INTO worker_shift (worker_id,day_of_week,shift_id) VALUES
	 ('Y1Z2A3B','MONDAY',1),
	 ('Y1Z2A3B','TUESDAY',1),
	 ('Y1Z2A3B','WEDNESDAY',2),
	 ('Y1Z2A3B','THURSDAY',1),
	 ('Y1Z2A3B','FRIDAY',3),
	 ('C4D5E6F','MONDAY',2),
	 ('C4D5E6F','TUESDAY',2),
	 ('C4D5E6F','WEDNESDAY',2),
	 ('C4D5E6F','THURSDAY',3),
	 ('C4D5E6F','FRIDAY',1);
INSERT INTO worker_shift (worker_id,day_of_week,shift_id) VALUES
	 ('G7H8I9J','MONDAY',3),
	 ('G7H8I9J','TUESDAY',3),
	 ('G7H8I9J','WEDNESDAY',1),
	 ('G7H8I9J','THURSDAY',4),
	 ('G7H8I9J','FRIDAY',5),
	 ('K1L2M3N','MONDAY',1),
	 ('K1L2M3N','TUESDAY',1),
	 ('K1L2M3N','WEDNESDAY',2),
	 ('K1L2M3N','THURSDAY',1),
	 ('K1L2M3N','FRIDAY',3);
INSERT INTO worker_shift (worker_id,day_of_week,shift_id) VALUES
	 ('O4P5Q6R','MONDAY',2),
	 ('O4P5Q6R','TUESDAY',2),
	 ('O4P5Q6R','WEDNESDAY',2),
	 ('O4P5Q6R','THURSDAY',3),
	 ('O4P5Q6R','FRIDAY',1),
	 ('S7T8U9V','MONDAY',3),
	 ('S7T8U9V','TUESDAY',3),
	 ('S7T8U9V','WEDNESDAY',1),
	 ('S7T8U9V','THURSDAY',4),
	 ('S7T8U9V','FRIDAY',5);
INSERT INTO worker_shift (worker_id,day_of_week,shift_id) VALUES
	 ('W1X2Y3Z','MONDAY',1),
	 ('W1X2Y3Z','TUESDAY',1),
	 ('W1X2Y3Z','WEDNESDAY',2),
	 ('W1X2Y3Z','THURSDAY',1),
	 ('W1X2Y3Z','FRIDAY',3),
	 ('A1B2C3Q','Monday',1);

-- worker skills sample data
INSERT INTO worker_skill (worker_id,skill_id,skill_level,productivity) VALUES
	 ('A1B2C3D',100,4,95),
	 ('A1B2C3D',240,3,88),
	 ('E4F5G6H',120,4,92),
	 ('E4F5G6H',231,2,75),
	 ('I7J8K9L',200,3,80),
	 ('I7J8K9L',221,4,90),
	 ('A1B2C3D',100,4,95),
	 ('A1B2C3D',240,3,88),
	 ('A1B2C3D',231,2,75),
	 ('E4F5G6H',120,4,92);
INSERT INTO worker_skill (worker_id,skill_id,skill_level,productivity) VALUES
	 ('E4F5G6H',231,2,75),
	 ('E4F5G6H',221,3,80),
	 ('I7J8K9L',200,3,80),
	 ('I7J8K9L',221,4,90),
	 ('I7J8K9L',243,2,70),
	 ('M1N2O3P',240,4,97),
	 ('M1N2O3P',100,3,85),
	 ('Q4R5S6T',251,2,60),
	 ('Q4R5S6T',211,3,78),
	 ('U7V8W9X',100,3,80);
INSERT INTO worker_skill (worker_id,skill_id,skill_level,productivity) VALUES
	 ('U7V8W9X',120,2,70),
	 ('U7V8W9X',231,4,95),
	 ('Y1Z2A3B',221,3,85),
	 ('Y1Z2A3B',240,2,65),
	 ('C4D5E6F',200,4,90),
	 ('C4D5E6F',231,3,80),
	 ('G7H8I9J',100,2,60),
	 ('G7H8I9J',243,4,98),
	 ('K1L2M3N',120,3,75),
	 ('K1L2M3N',221,2,68);
INSERT INTO worker_skill (worker_id,skill_id,skill_level,productivity) VALUES
	 ('O4P5Q6R',231,4,95),
	 ('O4P5Q6R',240,3,85),
	 ('S7T8U9V',100,2,60),
	 ('S7T8U9V',243,4,98),
	 ('W1X2Y3Z',120,3,75),
	 ('W1X2Y3Z',221,2,68),
	 ('B4C5D6E',231,4,95),
	 ('B4C5D6E',240,3,85),
	 ('F7G8H9I',100,2,60),
	 ('F7G8H9I',243,4,98);
INSERT INTO worker_skill (worker_id,skill_id,skill_level,productivity) VALUES
	 ('J1K2L3M',120,3,75),
	 ('J1K2L3M',221,2,68),
	 ('N4O5P6Q',231,4,95),
	 ('N4O5P6Q',240,3,85),
	 ('R7S8T9U',100,2,60),
	 ('R7S8T9U',243,4,98),
	 ('V1W2X3Y',120,3,75),
	 ('V1W2X3Y',221,2,68),
	 ('Z4A5B6C',231,4,95),
	 ('Z4A5B6C',240,3,85);
INSERT INTO worker_skill (worker_id,skill_id,skill_level,productivity) VALUES
	 ('D7E8F9G',100,2,60),
	 ('D7E8F9G',243,4,98),
	 ('H1I2J3K',120,3,75),
	 ('H1I2J3K',221,2,68),
	 ('L4M5N6O',231,4,95),
	 ('L4M5N6O',240,3,85),
	 ('P7Q8R9S',100,2,60),
	 ('P7Q8R9S',243,4,98),
	 ('T1U2V3W',120,3,75),
	 ('T1U2V3W',221,2,68);
INSERT INTO worker_skill (worker_id,skill_id,skill_level,productivity) VALUES
	 ('X4Y5Z6A',231,4,95),
	 ('X4Y5Z6A',240,3,85),
	 ('C7D8E9F',100,2,60),
	 ('C7D8E9F',243,4,98),
	 ('G1H2I3J',120,3,75),
	 ('G1H2I3J',221,2,68),
	 ('K4L5M6N',231,4,95),
	 ('K4L5M6N',240,3,85),
	 ('O7P8Q9R',100,2,60),
	 ('O7P8Q9R',243,4,98);
INSERT INTO worker_skill (worker_id,skill_id,skill_level,productivity) VALUES
	 ('S1T2U3V',120,3,75),
	 ('S1T2U3V',221,2,68),
	 ('W4X5Y6Z',231,4,95),
	 ('W4X5Y6Z',240,3,85),
	 ('B7C8D9E',100,2,60),
	 ('B7C8D9E',243,4,98),
	 ('F1G2H3I',120,3,75),
	 ('F1G2H3I',221,2,68),
	 ('J4K5L6M',231,4,95),
	 ('J4K5L6M',240,3,85);
INSERT INTO worker_skill (worker_id,skill_id,skill_level,productivity) VALUES
	 ('N7O8P9Q',100,2,60),
	 ('N7O8P9Q',243,4,98),
	 ('R1S2T3U',120,3,75),
	 ('R1S2T3U',221,2,68),
	 ('V4W5X6Y',231,4,95),
	 ('V4W5X6Y',240,3,85),
	 ('Z7A8B9C',100,2,60),
	 ('Z7A8B9C',243,4,98),
	 ('D1E2F3G',120,3,75),
	 ('D1E2F3G',221,2,68);
INSERT INTO worker_skill (worker_id,skill_id,skill_level,productivity) VALUES
	 ('H4I5J6K',231,4,95),
	 ('H4I5J6K',240,3,85),
	 ('L7M8N9O',100,2,60),
	 ('L7M8N9O',243,4,98),
	 ('P1Q2R3S',120,3,75),
	 ('P1Q2R3S',221,2,68),
	 ('A1B2C3Q',100,3,96);

-- task sample data
INSERT INTO task (id,skill_id,task_name,task_type,priority,dependent_task_id,task_count) VALUES
	 (1,100,'Receive','In',1,NULL,800),
	 (2,120,'Stow','In',2,1,700),
	 (3,121,'D2B','In',3,2,600),
	 (4,121,'D2B (carryover)','In',3,NULL,200),
	 (5,200,'Pick_Paperless','Out',1,NULL,900),
	 (6,211,'Pick_Paper','Out',1,NULL,900),
	 (7,220,'Induction','Out',2,NULL,700),
	 (8,221,'DPS','Out',3,7,700),
	 (9,230,'Rebin_Manual','Out',4,8,500),
	 (10,231,'Rebin_DAS','Out',4,8,500);
INSERT INTO task (id,skill_id,task_name,task_type,priority,dependent_task_id,task_count) VALUES
	 (11,240,'Pack','Out',5,9,600),
	 (12,260,'Gift','Out',6,11,400),
	 (13,250,'Pick to Go Paperless','Out',6,5,400),
	 (14,243,'Pack_Return','Out',7,NULL,400),
	 (15,241,'Pack_Paperless','Out',7,6,400),
	 (16,242,'Pack_Paper','Out',7,6,400),
	 (17,251,'Pick to Go Paper','Out',7,6,400),
	 (18,300,'ShipSort','Sort',8,11,700),
	 (19,500,'Maintenance','Other',9,NULL,400),
	 (20,600,'QA','Other',9,NULL,400);
INSERT INTO task (id,skill_id,task_name,task_type,priority,dependent_task_id,task_count) VALUES
	 (21,400,'Forklift','Other',9,NULL,400),
	 (22,700,'Management','Other',9,NULL,400),
	 (23,200,'Pick_Paperless (carryover)','Out',1,NULL,150),
	 (24,211,'Pick_Paper (carryover)','Out',1,NULL,150),
	 (25,220,'Induction (carryover)','Out',2,NULL,100),
	 (26,221,'DPS (carryover)','Out',3,NULL,100),
	 (27,230,'Rebin_Manual (carryover)','Out',4,NULL,80),
	 (28,231,'Rebin_DAS (carryover)','Out',4,NULL,80),
	 (29,240,'Pack (carryover)','Out',5,NULL,120),
	 (30,260,'Gift (carryover)','Out',6,NULL,60);
INSERT INTO task (id,skill_id,task_name,task_type,priority,dependent_task_id,task_count) VALUES
	 (31,250,'Pick to Go Paperless (carryover)','Out',6,NULL,60),
	 (32,243,'Pack_Return (carryover)','Out',7,NULL,60),
	 (33,241,'Pack_Paperless (carryover)','Out',7,NULL,60),
	 (34,242,'Pack_Paper (carryover)','Out',7,NULL,60),
	 (35,251,'Pick to Go Paper (carryover)','Out',7,NULL,60),
	 (36,300,'ShipSort (carryover)','Sort',8,NULL,100),
	 (37,500,'Maintenance (carryover)','Other',9,NULL,60),
	 (38,600,'QA (carryover)','Other',9,NULL,60),
	 (39,400,'Forklift (carryover)','Other',9,NULL,60),
	 (40,700,'Management (carryover)','Other',9,NULL,60);

-- assignment sample data
INSERT INTO assignment (worker_id,task_id,assigned_at,status,feedback) VALUES
	 ('G7H8I9J',14,'2025-07-14 00:42:37','PENDING',NULL),
	 ('S7T8U9V',32,'2025-07-14 00:42:37','PENDING',NULL),
	 ('Q4R5S6T',35,'2025-07-14 00:42:37','PENDING',NULL),
	 ('M1N2O3P',29,'2025-07-14 00:42:37','PENDING',NULL),
	 ('U7V8W9X',28,'2025-07-14 00:42:37','PENDING',NULL),
	 ('I7J8K9L',26,'2025-07-14 00:42:37','PENDING',NULL),
	 ('A1B2C3D',1,'2025-07-14 00:42:37','PENDING',NULL),
	 ('C4D5E6F',23,'2025-07-14 00:42:37','PENDING',NULL);