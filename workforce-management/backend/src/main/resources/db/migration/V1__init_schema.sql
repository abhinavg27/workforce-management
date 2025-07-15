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
    assigned_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);
