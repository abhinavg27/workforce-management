-- Sample data for task table: one task per skill_id, total task_count ≈ 10,000
-- Each skill_id gets a proportional share of the total

-- Logistics sample data for task table with realistic dependencies and groupings
-- Total task_count ≈ 10,000
INSERT INTO task (id, skill_id, task_name, task_type, priority, dependent_task_id, task_count) VALUES
-- Inbound (In): Receive → Stow → D2B (some D2B carryover)
-- Inbound (In): Receive → Stow → D2B (some D2B carryover)
(1, 100, 'Receive', 'In', 1, NULL, 800),
(2, 120, 'Stow', 'In', 2, 1, 700),
(3, 121, 'D2B', 'In', 3, 2, 600),
-- D2B carryover (pending from previous day, no dependency)
-- D2B carryover (pending from previous day, no dependency)
(4, 121, 'D2B (carryover)', 'In', 3, NULL, 200),
-- Pick_Paperless carryover (pending, no dependency)
-- Pick_Paperless carryover (pending, no dependency)
(23, 200, 'Pick_Paperless (carryover)', 'Out', 1, NULL, 150),
-- Pick_Paper carryover (pending, no dependency)
-- Pick_Paper carryover (pending, no dependency)
(24, 211, 'Pick_Paper (carryover)', 'Out', 1, NULL, 150),
-- Induction carryover (pending, no dependency)
-- Induction carryover (pending, no dependency)
(25, 220, 'Induction (carryover)', 'Out', 2, NULL, 100),
-- DPS carryover (pending, no dependency)
-- DPS carryover (pending, no dependency)
(26, 221, 'DPS (carryover)', 'Out', 3, NULL, 100),
-- Rebin_Manual carryover (pending, no dependency)
-- Rebin_Manual carryover (pending, no dependency)
(27, 230, 'Rebin_Manual (carryover)', 'Out', 4, NULL, 80),
-- Rebin_DAS carryover (pending, no dependency)
-- Rebin_DAS carryover (pending, no dependency)
(28, 231, 'Rebin_DAS (carryover)', 'Out', 4, NULL, 80),
-- Pack carryover (pending, no dependency)
-- Pack carryover (pending, no dependency)
(29, 240, 'Pack (carryover)', 'Out', 5, NULL, 120),
-- Gift carryover (pending, no dependency)
-- Gift carryover (pending, no dependency)
(30, 260, 'Gift (carryover)', 'Out', 6, NULL, 60),
-- Pick to Go Paperless carryover (pending, no dependency)
-- Pick to Go Paperless carryover (pending, no dependency)
(31, 250, 'Pick to Go Paperless (carryover)', 'Out', 6, NULL, 60),
-- Pack_Return carryover (pending, no dependency)
-- Pack_Return carryover (pending, no dependency)
(32, 243, 'Pack_Return (carryover)', 'Out', 7, NULL, 60),
-- Pack_Paperless carryover (pending, no dependency)
-- Pack_Paperless carryover (pending, no dependency)
(33, 241, 'Pack_Paperless (carryover)', 'Out', 7, NULL, 60),
-- Pack_Paper carryover (pending, no dependency)
-- Pack_Paper carryover (pending, no dependency)
(34, 242, 'Pack_Paper (carryover)', 'Out', 7, NULL, 60),
-- Pick to Go Paper carryover (pending, no dependency)
-- Pick to Go Paper carryover (pending, no dependency)
(35, 251, 'Pick to Go Paper (carryover)', 'Out', 7, NULL, 60),
-- ShipSort carryover (pending, no dependency)
-- ShipSort carryover (pending, no dependency)
(36, 300, 'ShipSort (carryover)', 'Sort', 8, NULL, 100),
-- Maintenance carryover (pending, no dependency)
-- Maintenance carryover (pending, no dependency)
(37, 500, 'Maintenance (carryover)', 'Other', 9, NULL, 60),
-- QA carryover (pending, no dependency)
-- QA carryover (pending, no dependency)
(38, 600, 'QA (carryover)', 'Other', 9, NULL, 60),
-- Forklift carryover (pending, no dependency)
-- Forklift carryover (pending, no dependency)
(39, 400, 'Forklift (carryover)', 'Other', 9, NULL, 60),
-- Management carryover (pending, no dependency)
-- Management carryover (pending, no dependency)
(40, 700, 'Management (carryover)', 'Other', 9, NULL, 60),
-- Outbound (Out): Pick (independent)
-- Outbound (Out): Pick (independent)
(5, 200, 'Pick_Paperless', 'Out', 1, NULL, 900),
(6, 211, 'Pick_Paper', 'Out', 1, NULL, 900),
-- Outbound (Out): Rebin (sequential)
-- Outbound (Out): Rebin (sequential)
(7, 220, 'Induction', 'Out', 2, NULL, 700),
(8, 221, 'DPS', 'Out', 3, 7, 700),
(9, 230, 'Rebin_Manual', 'Out', 4, 8, 500),
(10, 231, 'Rebin_DAS', 'Out', 4, 8, 500),
-- Outbound (Out): Pack (some depend on Pick, some on Rebin, some independent)
-- Outbound (Out): Pack (some depend on Pick, some on Rebin, some independent)
(11, 240, 'Pack', 'Out', 5, 9, 600),
(12, 260, 'Gift', 'Out', 6, 11, 400),
(13, 250, 'Pick to Go Paperless', 'Out', 6, 5, 400),
(14, 243, 'Pack_Return', 'Out', 7, NULL, 400),
(15, 241, 'Pack_Paperless', 'Out', 7, 6, 400),
(16, 242, 'Pack_Paper', 'Out', 7, 6, 400),
(17, 251, 'Pick to Go Paper', 'Out', 7, 6, 400),
-- Sort
-- Sort
(18, 300, 'ShipSort', 'Sort', 8, 11, 700),
-- Other (no dependencies)
-- Other (no dependencies)
(19, 500, 'Maintenance', 'Other', 9, NULL, 400),
(20, 600, 'QA', 'Other', 9, NULL, 400),
(21, 400, 'Forklift', 'Other', 9, NULL, 400),
(22, 700, 'Management', 'Other', 9, NULL, 400);
-- Total task_count: 11,800
-- DDL for task table (already in V1__init_schema.sql)
-- See migration file for table creation

-- DML: Sample data for task table
INSERT INTO task (id, skill_id, task_name, priority, dependent_task_id, task_count) VALUES
(1, 100, 'Receive', 1, NULL, 50),
(2, 120, 'Stow', 2, 1, 40),
(3, 200, 'Pick_Paperless', 3, 2, 100),
(4, 240, 'Pack', 4, 3, 80),
(5, 300, 'ShipSort', 5, 4, 60);
