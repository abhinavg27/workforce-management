-- DML for task table with task_type column
INSERT INTO task (id, skill_id, task_name, task_type, priority, dependent_task_id, task_count) VALUES
-- Inbound (In): Receive → Stow → D2B (some D2B carryover)
(1, 100, 'Receive', 'In', 1, NULL, 800),
(2, 120, 'Stow', 'In', 2, 1, 700),
(3, 121, 'D2B', 'In', 3, 2, 600),
(4, 121, 'D2B (carryover)', 'In', 3, NULL, 200),
-- Outbound (Out): Pick (independent)
(5, 200, 'Pick_Paperless', 'Out', 1, NULL, 900),
(6, 211, 'Pick_Paper', 'Out', 1, NULL, 900),
-- Outbound (Out): Rebin (sequential)
(7, 220, 'Induction', 'Out', 2, NULL, 700),
(8, 221, 'DPS', 'Out', 3, 7, 700),
(9, 230, 'Rebin_Manual', 'Out', 4, 8, 500),
(10, 231, 'Rebin_DAS', 'Out', 4, 8, 500),
-- Outbound (Out): Pack (some depend on Pick, some on Rebin, some independent)
(11, 240, 'Pack', 'Out', 5, 9, 600),
(12, 260, 'Gift', 'Out', 6, 11, 400),
(13, 250, 'Pick to Go Paperless', 'Out', 6, 5, 400),
(14, 243, 'Pack_Return', 'Out', 7, NULL, 400),
(15, 241, 'Pack_Paperless', 'Out', 7, 6, 400),
(16, 242, 'Pack_Paper', 'Out', 7, 6, 400),
(17, 251, 'Pick to Go Paper', 'Out', 7, 6, 400),
-- Carryover tasks (pending, no dependency)
(23, 200, 'Pick_Paperless (carryover)', 'Out', 1, NULL, 150),
(24, 211, 'Pick_Paper (carryover)', 'Out', 1, NULL, 150),
(25, 220, 'Induction (carryover)', 'Out', 2, NULL, 100),
(26, 221, 'DPS (carryover)', 'Out', 3, NULL, 100),
(27, 230, 'Rebin_Manual (carryover)', 'Out', 4, NULL, 80),
(28, 231, 'Rebin_DAS (carryover)', 'Out', 4, NULL, 80),
(29, 240, 'Pack (carryover)', 'Out', 5, NULL, 120),
(30, 260, 'Gift (carryover)', 'Out', 6, NULL, 60),
(31, 250, 'Pick to Go Paperless (carryover)', 'Out', 6, NULL, 60),
(32, 243, 'Pack_Return (carryover)', 'Out', 7, NULL, 60),
(33, 241, 'Pack_Paperless (carryover)', 'Out', 7, NULL, 60),
(34, 242, 'Pack_Paper (carryover)', 'Out', 7, NULL, 60),
(35, 251, 'Pick to Go Paper (carryover)', 'Out', 7, NULL, 60),
-- Sort
(18, 300, 'ShipSort', 'Sort', 8, 11, 700),
(36, 300, 'ShipSort (carryover)', 'Sort', 8, NULL, 100),
-- Other (no dependencies)
(19, 500, 'Maintenance', 'Other', 9, NULL, 400),
(20, 600, 'QA', 'Other', 9, NULL, 400),
(21, 400, 'Forklift', 'Other', 9, NULL, 400),
(22, 700, 'Management', 'Other', 9, NULL, 400),
(37, 500, 'Maintenance (carryover)', 'Other', 9, NULL, 60),
(38, 600, 'QA (carryover)', 'Other', 9, NULL, 60),
(39, 400, 'Forklift (carryover)', 'Other', 9, NULL, 60),
(40, 700, 'Management (carryover)', 'Other', 9, NULL, 60);
