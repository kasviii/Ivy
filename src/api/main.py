import os
import uuid
import asyncio
from datetime import datetime
from typing import Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import json
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.researcher import run_research

app = FastAPI(
    title="Ivy — AI Research Agent",
    description="Autonomous literature review generator using LangGraph",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store
jobs = {}

class ResearchRequest(BaseModel):
    topic: str

class JobResponse(BaseModel):
    job_id: str
    topic: str
    status: str
    created_at: str

@app.get("/")
def root():
    return {"message": "Ivy Research Agent API", "status": "running", "version": "1.0.0"}

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.post("/research", response_model=JobResponse)
async def start_research(request: ResearchRequest, background_tasks: BackgroundTasks):
    job_id = str(uuid.uuid4())
    created_at = datetime.now().isoformat()

    jobs[job_id] = {
        "job_id": job_id,
        "topic": request.topic,
        "status": "queued",
        "created_at": created_at,
        "result": None,
        "papers": [],
        "error": None,
        "progress": []
    }

    background_tasks.add_task(run_research_job, job_id, request.topic)

    return JobResponse(
        job_id=job_id,
        topic=request.topic,
        status="queued",
        created_at=created_at
    )

async def run_research_job(job_id: str, topic: str):
    try:
        jobs[job_id]["status"] = "running"
        jobs[job_id]["progress"].append("🔍 Starting research...")

        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, run_research, topic)

        jobs[job_id]["status"] = "complete"
        jobs[job_id]["result"] = result["final_review"]
        jobs[job_id]["papers"] = result.get("papers", [])
        jobs[job_id]["progress"].append("✅ Research complete!")

    except Exception as e:
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["error"] = str(e)
        jobs[job_id]["progress"].append(f"❌ Error: {str(e)}")

@app.get("/research/{job_id}")
def get_job(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    return jobs[job_id]

@app.get("/research/{job_id}/status")
def get_status(job_id: str):
    if job_id not in jobs:
        raise HTTPException(status_code=404, detail="Job not found")
    job = jobs[job_id]
    return {
        "job_id": job_id,
        "status": job["status"],
        "progress": job["progress"]
    }

@app.get("/jobs")
def list_jobs():
    return [
        {
            "job_id": j["job_id"],
            "topic": j["topic"],
            "status": j["status"],
            "created_at": j["created_at"]
        }
        for j in jobs.values()
    ]