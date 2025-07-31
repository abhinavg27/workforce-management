-- Migration: Add shift info columns to assignment table
ALTER TABLE assignment
ADD COLUMN shift_name VARCHAR(255),
ADD COLUMN shift_start VARCHAR(16),
ADD COLUMN shift_end VARCHAR(16);
