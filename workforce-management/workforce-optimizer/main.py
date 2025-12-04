from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from typing import List, Optional
from ortools.sat.python import cp_model
import datetime
import logging



app = FastAPI()
# Configure logger
import sys
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    stream=sys.stdout,
    force=True
)
logger = logging.getLogger("optimizer")

# --- Data Models ---
class Task(BaseModel):
    id: str
    name: str
    skill_id: int
    priority: int
    units: int
    dependencies: Optional[List[str]] = []
    type: Optional[str] = None  # For legend/coloring

class Worker(BaseModel):
    id: str
    name: str
    skills: List[int]
    productivity: dict  # skill_id -> units/hour
    shift_start: str  # '08:00'
    shift_end: str    # '16:00'
    break_minutes: int = 60

class Assignment(BaseModel):
    worker_id: str
    task_id: str
    task_name: Optional[str] = None
    start: str  # ISO datetime
    end: str    # ISO datetime
    units: int
    is_break: bool = False
    task_type: Optional[str] = None  # For legend/coloring

class OptimizeRequest(BaseModel):
    tasks: List[Task]
    workers: List[Worker]
    date: str  # 'YYYY-MM-DD'

class UnassignedTask(BaseModel):
    id: str
    remaining_units: int

class OptimizeResponse(BaseModel):
    assignments: List[Assignment]
    unassigned_tasks: List[UnassignedTask] = []

from ortools.sat.python.cp_model import INT32_MAX

# --- Optimizer Logic (CP-SAT) ---
@app.post("/optimize", response_model=OptimizeResponse)
async def optimize(req: OptimizeRequest, request: Request):
    # --- DEBUG: Print why tasks are unassigned ---
    for t in req.tasks:
        possible_workers = [w for w in req.workers if t.skill_id in w.skills]
        if not possible_workers:
            # logger.warning(f"Task {t.id} ('{t.name}') cannot be assigned: no worker has required skill_id {t.skill_id}.")
            continue
        for w in possible_workers:
            # Try to get productivity for this skill
            prod = (
                w.productivity.get(str(t.skill_id))
                or w.productivity.get(t.skill_id)
                or w.productivity.get(int(t.skill_id))
                or 1
            )
            # Calculate duration in minutes (use math.ceil for accuracy)
            import math
            duration = math.ceil((60.0 * t.units) / prod)
            # Parse shift start/end, handle overnight shifts
            shift_start = w.shift_start.split(":")
            shift_end = w.shift_end.split(":")
            start_min = int(shift_start[0]) * 60 + int(shift_start[1])
            end_min = int(shift_end[0]) * 60 + int(shift_end[1])
            if end_min <= start_min:
                # Overnight shift (e.g., 16:00 to 00:00 means 16:00 to next day 00:00)
                end_min += 24 * 60
            available = end_min - start_min - w.break_minutes
            if duration > available:
                logger.warning(f"Task {t.id} ('{t.name}') cannot be assigned to worker {w.id} ('{w.name}'): duration {duration} min exceeds available shift {available} min (prod={prod}).")
            # else:
                # logger.info(f"Task {t.id} ('{t.name}') could be assigned to worker {w.id} ('{w.name}') (duration {duration} min, available {available} min, prod={prod}).")
    # Log the incoming JSON payload
    try:
        body = await request.body()
        # logger.info("Received /optimize payload (raw): %s", body.decode('utf-8'))
        # Pretty print parsed input
        logger.info("Parsed input - date: %s", req.date)
        logger.info("Parsed input - workers:")
        #for w in req.workers:
        #    logger.info("  Worker: id=%s, name=%s, skills=%s, productivity=%s, shift_start=%s, shift_end=%s, break_minutes=%s",
        #                w.id, w.name, w.skills, w.productivity, w.shift_start, w.shift_end, w.break_minutes)
        logger.info("Parsed input - tasks:")
        # for t in req.tasks:
            #logger.info("  Task: id=%s, name=%s, skill_id=%s, priority=%s, units=%s, dependencies=%s", t.id, t.name, t.skill_id, t.priority, t.units, t.dependencies)
    except Exception as e:
        logger.warning(f"Could not log request body: {e}")
    # Real CP-SAT implementation for workforce assignment optimization
    if not req.tasks or not req.workers:
        raise HTTPException(status_code=400, detail="No tasks or workers provided.")


    model = cp_model.CpModel()
    assignments = []
    unassigned_tasks = []
    task_map = {t.id: t for t in req.tasks}
    def time_to_min(tstr):
        if not tstr:
            raise ValueError("Empty time string")
        parts = tstr.strip().split(":")
        if len(parts) == 2:
            h, m = map(int, parts)
        elif len(parts) == 3:
            h, m, _ = map(int, parts)
        else:
            raise ValueError(f"Invalid time format: {tstr}")
        minutes = h * 60 + m
        if h == 0 and m == 0 and (tstr == "00:00" or tstr == "00:00:00"):
            minutes = 24 * 60
        return minutes
    shift_bounds = {}
    for w in req.workers:
        shift_bounds[w.id] = (time_to_min(w.shift_start), time_to_min(w.shift_end))

    intervals = {}
    presences = {}
    start_vars = {}
    end_vars = {}
    unit_vars = {}
    split_unit_vars = {}
    import math
    for t in req.tasks:
        for w in req.workers:
            if t.skill_id not in w.skills:
                # logger.info(f"Worker {w.id} ('{w.name}') does not have skill {t.skill_id} for task {t.id} ('{t.name}')")
                continue
            prod = None
            for key in [str(t.skill_id), t.skill_id, int(t.skill_id)]:
                if key in w.productivity:
                    prod = w.productivity[key]
                    break
            if prod is None:
                prod = 1
                logger.warning(f"Productivity for worker {w.id} ('{w.name}') and skill {t.skill_id} not found, defaulting to 1.")
            shift_start_min, shift_end_min = shift_bounds[w.id]
            max_units = math.floor(prod * ((shift_end_min - shift_start_min - w.break_minutes) / 60.0))
            if max_units <= 0:
                # logger.warning(f"Worker {w.id} ('{w.name}') cannot work any units for skill {t.skill_id} in shift.")
                continue
            # Allow splitting: units assigned to this worker for this task
            split_units = model.NewIntVar(0, min(t.units, max_units), f"units_t{t.id}_w{w.id}")
            duration = model.NewIntVar(0, shift_end_min - shift_start_min, f"duration_t{t.id}_w{w.id}")
            # duration = ceil(60 * units / prod)
            # Use AddDivisionEquality for integer division in CP-SAT
            model.AddDivisionEquality(duration, split_units * 60 + prod - 1, prod)
            start = model.NewIntVar(shift_start_min, shift_end_min, f"start_t{t.id}_w{w.id}")
            end = model.NewIntVar(shift_start_min, shift_end_min, f"end_t{t.id}_w{w.id}")
            presence = model.NewBoolVar(f"presence_t{t.id}_w{w.id}")
            interval = model.NewOptionalIntervalVar(start, duration, end, presence, f"interval_t{t.id}_w{w.id}")
            intervals[(t.id, w.id)] = interval
            start_vars[(t.id, w.id)] = start
            end_vars[(t.id, w.id)] = end
            unit_vars[(t.id, w.id)] = t.units
            split_unit_vars[(t.id, w.id)] = split_units
            presences[(t.id, w.id)] = presence
            # Enforce: if presence==1 then split_units>0, if presence==0 then split_units==0
            model.Add(split_units > 0).OnlyEnforceIf(presence)
            model.Add(split_units == 0).OnlyEnforceIf(presence.Not())
            #logger.info(f"Productivity for task {t.id} ('{t.name}') with worker {w.id} ('{w.name}'): {prod} units/hour, start={start}, end={end}, split_units={split_units}, duration={duration}, presence={presence}, interval={interval}")

    # Diagnostics: If no intervals created, log reason
    if not intervals:
        logger.error("No intervals created for any task/worker combination. Check skills, productivity, and shift durations.")
        for t in req.tasks:
            for w in req.workers:
                logger.error(f"Task {t.id} ('{t.name}') and worker {w.id} ('{w.name}') - skill match: {t.skill_id in w.skills}")
        response = OptimizeResponse(assignments=[], unassigned_tasks=[t.id for t in req.tasks])
        import json
        logger.info("Optimize API response: %s", json.dumps(response.dict(), indent=2))
        return response

    # Each task: sum of split units assigned to all workers <= total units
    for t in req.tasks:
        possible_workers = [w.id for w in req.workers if (t.id, w.id) in intervals]
        if not possible_workers:
            continue
        model.Add(sum([split_unit_vars[(t.id, wid)] for wid in possible_workers]) <= t.units)

    # No overlap for each worker
    for w in req.workers:
        worker_intervals = [intervals[(t.id, w.id)] for t in req.tasks if (t.id, w.id) in intervals]
        if worker_intervals:
            model.AddNoOverlap(worker_intervals)

    # Task dependencies
    for t in req.tasks:
        if t.dependencies:
            for dep in t.dependencies:
                for w1 in req.workers:
                    for w2 in req.workers:
                        if (t.id, w1.id) in start_vars and (dep, w2.id) in end_vars:
                            # Only enforce if both are assigned
                            model.Add(start_vars[(t.id, w1.id)] >= end_vars[(dep, w2.id)]).OnlyEnforceIf([
                                presences[(t.id, w1.id)], presences[(dep, w2.id)]
                            ])

    # Break after 4 hours for each worker
    for w in req.workers:
        break_start = shift_bounds[w.id][0] + 240
        break_end = break_start + w.break_minutes
        for t in req.tasks:
            if (t.id, w.id) in intervals:
                s = start_vars[(t.id, w.id)]
                e = end_vars[(t.id, w.id)]
                before_break = model.NewBoolVar(f"before_break_t{t.id}_w{w.id}")
                after_break = model.NewBoolVar(f"after_break_t{t.id}_w{w.id}")
                model.Add(e <= break_start).OnlyEnforceIf(before_break)
                model.Add(s >= break_end).OnlyEnforceIf(after_break)
                model.AddBoolOr([before_break, after_break]).OnlyEnforceIf(presences[(t.id, w.id)])

    # Objective: maximize sum of priorities * units assigned
    model.Maximize(sum([task_map[t].priority * split_unit_vars[(t, w)] for (t, w) in split_unit_vars]))

    # Solve
    solver = cp_model.CpSolver()
    status = solver.Solve(model)
    # Build assignments and unassigned tasks
    assigned_units = {t.id: 0 for t in req.tasks}
    if status in [cp_model.OPTIMAL, cp_model.FEASIBLE]:
        for (t_id, w_id), interval in intervals.items():
            if solver.Value(presences[(t_id, w_id)]) and solver.Value(split_unit_vars[(t_id, w_id)]) > 0:
                start_min = solver.Value(start_vars[(t_id, w_id)])
                end_min = solver.Value(end_vars[(t_id, w_id)])
                units_assigned = solver.Value(split_unit_vars[(t_id, w_id)])
                date = req.date
                start_dt = datetime.datetime.fromisoformat(f"{date}T00:00") + datetime.timedelta(minutes=start_min)
                end_dt = datetime.datetime.fromisoformat(f"{date}T00:00") + datetime.timedelta(minutes=end_min)
                # Get task type and name for legend
                task_type = None
                task_name = None
                if t_id in task_map:
                    task_type = task_map[t_id].type
                    task_name = task_map[t_id].name
                assignments.append(Assignment(
                    worker_id=w_id,
                    task_id=t_id,
                    task_name=task_name,
                    start=start_dt.isoformat(),
                    end=end_dt.isoformat(),
                    units=units_assigned,
                    is_break=False,
                    task_type=task_type
                ))
                assigned_units[t_id] += units_assigned
        # Add break assignments for each worker
        for w in req.workers:
            break_start = shift_bounds[w.id][0] + 240
            break_end = break_start + w.break_minutes
            date = req.date
            start_dt = datetime.datetime.fromisoformat(f"{date}T00:00") + datetime.timedelta(minutes=break_start)
            end_dt = datetime.datetime.fromisoformat(f"{date}T00:00") + datetime.timedelta(minutes=break_end)
            assignments.append(Assignment(
                worker_id=w.id,
                task_id="0",
                task_name="Break",
                start=start_dt.isoformat(),
                end=end_dt.isoformat(),
                units=0,
                is_break=True,
                task_type="BREAK"
            ))
        # Any task not fully assigned is unassigned for remaining units
        for t in req.tasks:
            remaining = t.units - assigned_units[t.id]
            if remaining > 0:
                unassigned_tasks.append(UnassignedTask(id=t.id, remaining_units=remaining))
    else:
        # If infeasible, all tasks are unassigned for all units
        for t in req.tasks:
            unassigned_tasks.append(UnassignedTask(id=t.id, remaining_units=t.units))
    response = OptimizeResponse(assignments=assignments, unassigned_tasks=unassigned_tasks)
    # Log the response before sending to client
    # Pretty print using json.dumps for logging
    import json
    # logger.info("Optimize API response: %s", json.dumps(response.dict(), indent=2))
    return response
