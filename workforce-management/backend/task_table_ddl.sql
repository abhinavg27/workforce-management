-- DDL for task table with task_type column
CREATE TABLE task (
    id BIGINT PRIMARY KEY,
    skill_id INT NOT NULL,
    task_name VARCHAR(100) NOT NULL,
    task_type VARCHAR(20) NOT NULL,
    priority INT NOT NULL DEFAULT 0,
    dependent_task_id BIGINT NULL,
    task_count INT NOT NULL DEFAULT 1
);
