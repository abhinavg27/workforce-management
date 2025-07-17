
# Workforce Optimizer Python Microservice

Python FastAPI microservice for advanced workforce assignment optimization using Google OR-Tools.

## Features
- Assigns and schedules tasks to workers based on shift, skills, productivity, priority, dependencies
- Supports task splitting, breaks, shift logic, and Gantt-compatible output
- REST API for integration with Java/Spring backend

## Getting Started
1. Install dependencies:
   ```sh
   pip install -r requirements.txt
   ```
2. Start the service:
   ```sh
   uvicorn main:app --reload
   or python3 -m uvicorn main:app --reload
   ```

## API Usage
- POST to `/optimize` with JSON payload of workers, tasks, shifts, etc.
- Returns assignments in Gantt-compatible format:
  ```json
  {
    "assignments": [
      { "worker_id": "...", "task_id": "...", "task_name": "...", "start": "...", "end": "...", "units": 0, "is_break": true, "task_type": "BREAK" },
      ...
    ],
    "unassigned_tasks": [ ... ]
  }
  ```

## Integration
- Backend calls `/optimize` and persists results in DB

## Requirements
- Python 3.10+
