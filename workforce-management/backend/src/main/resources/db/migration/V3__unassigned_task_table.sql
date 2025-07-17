-- Migration: Create unassigned_task table
CREATE TABLE IF NOT EXISTS unassigned_task (
    id VARCHAR(64) PRIMARY KEY,
    remaining_units INT NOT NULL,
    task_name VARCHAR(255)
);
