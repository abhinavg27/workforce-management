-- Migration: Add Gantt-compatible columns to assignment table
ALTER TABLE assignment
  ADD COLUMN worker_name VARCHAR(255),
  ADD COLUMN task_name VARCHAR(255),
  ADD COLUMN start_time DATETIME,
  ADD COLUMN end_time DATETIME,
  ADD COLUMN units_assigned INT,
  ADD COLUMN is_break BOOLEAN DEFAULT FALSE;

-- (Optional) If you want to drop old columns no longer needed, use:
-- ALTER TABLE assignment DROP COLUMN assigned_at;
