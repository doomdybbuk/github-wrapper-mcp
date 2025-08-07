import os
from fastapi import FastAPI, HTTPException, Body
from pydantic import BaseModel
from dotenv import load_dotenv
from app.github_client import GitHubClient

# Load environment
load_dotenv()
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN is not set in environment")

# Initialize GitHub client and FastAPI
git_client = GitHubClient(GITHUB_TOKEN)
app = FastAPI(title="GitHub Service API")

# Request models
default = {"description": "Optional description", "private": True}

class RepoCreateRequest(BaseModel):
    name: str
    private: bool = True
    description: str = ""

class CollaboratorRequest(BaseModel):
    repo_name: str
    collaborator: str
    permission: str = "push"

# Endpoints
@app.post("/create-repo")
async def create_repo(req: RepoCreateRequest):
    try:
        repo = git_client.create_repo(req.name, private=req.private, description=req.description)
        return {"repo_url": repo.html_url}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/clone-url/{repo_name}")
async def get_clone_url(repo_name: str):
    try:
        url = git_client.get_clone_url(repo_name)
        return {"clone_url": url}
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.post("/add-collaborator")
async def add_collaborator(req: CollaboratorRequest):
    try:
        git_client.add_collaborator(req.repo_name, req.collaborator, permission=req.permission)
        return {"status": "success"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.post("/add-codeql-workflow")
async def add_codeql_workflow(repo_name: str = Body(..., embed=True)):
    codeql_yaml = """
name: "CodeQL"
on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
jobs:
  analyze:
    name: Analyze
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: github/codeql-action/init@v3
        with:
          languages: python
      - uses: github/codeql-action/analyze@v3
"""
    workflow_path = ".github/workflows/codeql.yml"
    try:
        git_client.add_workflow_file(repo_name, workflow_path, codeql_yaml, "Add CodeQL workflow")
        return {"status": "CodeQL workflow added"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
