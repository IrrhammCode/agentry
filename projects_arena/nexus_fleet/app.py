"""
NexusFleet Production FastAPI Service & Autonomous Operations Gateway.
Enterprise-grade microservice incorporating:
- FastAPI with Pydantic v2 schemas and validation
- SQLite WAL persistence via database.py
- Embedded Agentry Sentry Guardrail Hook (Sub-15ms Blast Radius & Risk Interceptor)
- Complete REST CRUD API for fleet nodes and autonomous tasks
- Real-time fleet metrics and health diagnostics
- Static dashboard serving
"""

from __future__ import annotations

import os
import time
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

# Local database operations
from .database import (
    init_db,
    seed_data,
    inspect_db_state,
    get_nodes,
    get_node_by_id,
    get_node_by_name,
    create_node,
    update_node_status,
    get_tasks,
    get_task_by_id,
    get_tasks_by_node,
    create_task,
    update_task_status,
    get_db_connection,
)

# Agentry Sentinel Guard integration
try:
    from agentry.blast_radius import BlastRadiusEvaluator, BlastRadiusAssessment
    _evaluator = BlastRadiusEvaluator()
except ImportError:
    _evaluator = None

STATIC_DIR = Path(__file__).resolve().parent / "static"
INDEX_HTML = STATIC_DIR / "index.html"

# In-memory tracking of incidents blocked by Agentry Sentinel
_INCIDENT_HISTORY: List[Dict[str, Any]] = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager: initializes SQLite schema and seed records on startup."""
    init_db()
    seed_data()
    yield


app = FastAPI(
    title="NexusFleet Operations Gateway",
    description="Autonomous Agent Fleet Control & Dispatch Platform protected by Agentry",
    version="1.0.0",
    lifespan=lifespan,
)

# Cross-Origin Resource Sharing
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic Schemas (v2)
# ---------------------------------------------------------------------------

class NodeCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=64, description="Unique hostname/identifier")
    role: str = Field(..., min_length=2, max_length=32, description="Role: coordinator, worker, gateway, etc.")
    status: str = Field(default="online", description="Status: online, busy, idle, offline")
    ip_address: str = Field(..., min_length=7, max_length=45, description="IP address or host URI")


class NodeStatusUpdate(BaseModel):
    status: str = Field(..., description="Target status: online, busy, idle, offline")


class TaskCreate(BaseModel):
    node_id: int = Field(..., description="Target node ID")
    title: str = Field(..., min_length=3, max_length=128, description="Task title / objective")
    command: str = Field(..., min_length=1, description="Command or tool call to execute")
    risk_score: Optional[float] = Field(None, ge=0.0, le=1.0, description="Optional pre-computed risk score")


class TaskUpdate(BaseModel):
    status: Optional[str] = Field(None, description="pending, running, completed, failed, blocked")
    result: Optional[str] = Field(None, description="Execution stdout / result summary")


class GuardEvaluateRequest(BaseModel):
    command: str = Field(..., min_length=1, description="Command string or script payload to inspect")
    tool_name: str = Field(default="bash", description="Target tool: bash, python, sql, filesystem")


# ---------------------------------------------------------------------------
# System Endpoints
# ---------------------------------------------------------------------------

@app.get("/", response_class=FileResponse)
async def serve_dashboard():
    """Serves the interactive NexusFleet mission control dashboard."""
    if not INDEX_HTML.exists():
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"message": "Dashboard UI static assets not found. Access /docs for API."},
        )
    return FileResponse(str(INDEX_HTML), media_type="text/html")


@app.get("/api/v1/health")
async def health_check():
    """System health check and SQLite WAL diagnostics."""
    db_state = inspect_db_state()
    return {
        "status": "healthy",
        "service": "NexusFleet",
        "version": "1.0.0",
        "guardrail_engine": "Agentry TabPFN Sentinel" if _evaluator else "Heuristic Fallback",
        "database": db_state,
        "timestamp": time.time(),
    }


@app.get("/api/v1/metrics")
async def get_metrics():
    """Real-time fleet performance, task status distribution, and risk metrics."""
    nodes = get_nodes()
    tasks = get_tasks()
    
    total_nodes = len(nodes)
    online_nodes = sum(1 for n in nodes if n["status"] == "online")
    busy_nodes = sum(1 for n in nodes if n["status"] == "busy")
    idle_nodes = sum(1 for n in nodes if n["status"] == "idle")
    
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t["status"] == "completed")
    running_tasks = sum(1 for t in tasks if t["status"] == "running")
    pending_tasks = sum(1 for t in tasks if t["status"] == "pending")
    failed_tasks = sum(1 for t in tasks if t["status"] == "failed")
    blocked_tasks = sum(1 for t in tasks if t["status"] == "blocked")
    
    avg_risk = sum(t["risk_score"] for t in tasks) / total_tasks if total_tasks > 0 else 0.0
    
    return {
        "nodes": {
            "total": total_nodes,
            "online": online_nodes,
            "busy": busy_nodes,
            "idle": idle_nodes,
        },
        "tasks": {
            "total": total_tasks,
            "completed": completed_tasks,
            "running": running_tasks,
            "pending": pending_tasks,
            "failed": failed_tasks,
            "blocked": blocked_tasks,
        },
        "safety": {
            "average_risk_score": round(avg_risk, 3),
            "incidents_intercepted": len(_INCIDENT_HISTORY),
            "recent_incidents": _INCIDENT_HISTORY[-5:],
        },
    }


# ---------------------------------------------------------------------------
# Node Endpoints
# ---------------------------------------------------------------------------

@app.get("/api/v1/nodes")
async def list_nodes(
    role: Optional[str] = Query(None, description="Filter by role"),
    status: Optional[str] = Query(None, description="Filter by status"),
):
    """List all registered fleet nodes with optional filtering."""
    nodes = get_nodes()
    if role:
        nodes = [n for n in nodes if n["role"].lower() == role.lower()]
    if status:
        nodes = [n for n in nodes if n["status"].lower() == status.lower()]
    return {"nodes": nodes, "count": len(nodes)}


@app.get("/api/v1/nodes/{node_id}")
async def get_node_details(node_id: int):
    """Retrieve node details and all associated tasks."""
    node = get_node_by_id(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node #{node_id} not found.")
    tasks = get_tasks_by_node(node_id)
    return {"node": node, "tasks": tasks}


@app.post("/api/v1/nodes", status_code=status.HTTP_201_CREATED)
async def register_node(payload: NodeCreate):
    """Register a new node into the fleet."""
    existing = get_node_by_name(payload.name)
    if existing:
        raise HTTPException(status_code=400, detail=f"Node '{payload.name}' already registered.")
    
    node_id = create_node(
        name=payload.name,
        role=payload.role,
        status=payload.status,
        ip_address=payload.ip_address,
    )
    return {"message": "Node registered successfully.", "node_id": node_id}


@app.patch("/api/v1/nodes/{node_id}/status")
async def modify_node_status(node_id: int, payload: NodeStatusUpdate):
    """Update node operational status."""
    node = get_node_by_id(node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Node #{node_id} not found.")
    
    update_node_status(node_id, payload.status)
    return {"message": f"Node #{node_id} status updated to '{payload.status}'."}


# ---------------------------------------------------------------------------
# Agentry Guard & Task Dispatch Endpoints
# ---------------------------------------------------------------------------

@app.post("/api/v1/guard/evaluate")
async def evaluate_command_risk(payload: GuardEvaluateRequest):
    """
    Sub-15ms Semantic Blast Radius & Destructive Action Interceptor.
    Directly evaluates a command before agent dispatch.
    """
    if _evaluator:
        assessment = _evaluator.evaluate(tool_name=payload.tool_name, action_input=payload.command)
        return {
            "command": payload.command,
            "tool": payload.tool_name,
            "category": assessment.category,
            "score": assessment.score,
            "is_blocked": assessment.is_blocked,
            "action": assessment.recommended_action,
            "reason": assessment.violation_reason,
        }
    else:
        # Fallback keyword inspection
        is_blocked = any(bad in payload.command for bad in ["rm -rf", "DROP TABLE", "format ", "del /s"])
        return {
            "command": payload.command,
            "tool": payload.tool_name,
            "category": "CRITICAL" if is_blocked else "NONE",
            "score": 0.99 if is_blocked else 0.1,
            "is_blocked": is_blocked,
            "action": "KILL" if is_blocked else "PASS",
            "reason": "Dangerous keyword detected in payload" if is_blocked else None,
        }


@app.get("/api/v1/tasks")
async def list_tasks(
    status: Optional[str] = Query(None, description="Filter by status"),
    node_id: Optional[int] = Query(None, description="Filter by node ID"),
):
    """List fleet tasks with optional filtering."""
    tasks = get_tasks()
    if status:
        tasks = [t for t in tasks if t["status"].lower() == status.lower()]
    if node_id:
        tasks = [t for t in tasks if t["node_id"] == node_id]
    return {"tasks": tasks, "count": len(tasks)}


@app.post("/api/v1/tasks", status_code=status.HTTP_201_CREATED)
async def dispatch_task(payload: TaskCreate, strict: bool = Query(True, description="Strict Agentry blocking")):
    """
    Dispatches a task to a fleet node.
    INTERCEPTED BY AGENTRY SENTINEL:
    Evaluates blast radius before inserting/executing the command.
    """
    node = get_node_by_id(payload.node_id)
    if not node:
        raise HTTPException(status_code=404, detail=f"Target node #{payload.node_id} does not exist.")
    
    # 1. Agentry Blast Radius Evaluation
    if _evaluator:
        assessment = _evaluator.evaluate(tool_name="bash", action_input=payload.command)
        risk = assessment.score
        is_blocked = assessment.is_blocked
        reason = assessment.violation_reason
    else:
        is_blocked = any(bad in payload.command for bad in ["rm -rf", "DROP TABLE", "format "])
        risk = 0.95 if is_blocked else (payload.risk_score or 0.2)
        reason = "Catastrophic command detected" if is_blocked else None

    # 2. If blocked by Agentry Sentinel
    if is_blocked:
        incident = {
            "timestamp": time.time(),
            "node_id": payload.node_id,
            "node_name": node["name"],
            "command": payload.command,
            "risk_score": risk,
            "reason": reason,
        }
        _INCIDENT_HISTORY.append(incident)
        
        if strict:
            # Raise 403 Forbidden with Agentry remediation details
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": "AGENTRY_BLAST_RADIUS_VIOLATION",
                    "message": "Action immediately blocked by Agentry Sentinel runtime guard.",
                    "reason": reason,
                    "risk_score": risk,
                    "target_node": node["name"],
                },
            )
        else:
            # Non-strict mode: Record task directly into DB with 'blocked' state
            task_id = create_task(
                node_id=payload.node_id,
                title=payload.title,
                command=payload.command,
                risk_score=risk,
                status="blocked",
                result=f"BLOCKED BY AGENTRY: {reason}",
            )
            return {
                "message": "Task created in BLOCKED state due to Agentry Sentinel violation.",
                "task_id": task_id,
                "status": "blocked",
                "risk_score": risk,
            }

    # 3. Safe Command -> Create Task
    task_id = create_task(
        node_id=payload.node_id,
        title=payload.title,
        command=payload.command,
        risk_score=payload.risk_score if payload.risk_score is not None else risk,
        status="pending",
        result=None,
    )
    return {
        "message": "Task queued successfully.",
        "task_id": task_id,
        "status": "pending",
        "risk_score": risk,
    }


@app.patch("/api/v1/tasks/{task_id}")
async def update_task(task_id: int, payload: TaskUpdate):
    """Update task execution status and stdout result."""
    task = get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task #{task_id} not found.")
    
    new_status = payload.status or task["status"]
    update_task_status(task_id, status=new_status, result=payload.result)
    return {"message": f"Task #{task_id} updated.", "status": new_status}


@app.delete("/api/v1/tasks/{task_id}")
async def delete_task_record(task_id: int):
    """Delete a task record."""
    task = get_task_by_id(task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task #{task_id} not found.")
    
    with get_db_connection() as conn:
        conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    return {"message": f"Task #{task_id} deleted."}


# Mount static assets if directory exists
if STATIC_DIR.exists():
    app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")
