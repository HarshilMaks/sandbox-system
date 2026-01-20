"""API server for sandbox system control."""
from fastapi import FastAPI
from .routes import session, sandbox

app = FastAPI(
    title="Stateful Sandbox System API",
    description="Create, manage, and destroy isolated execution environments for AI agents"
)

app.include_router(session.router, prefix="/api/sessions", tags=["sessions"])
app.include_router(sandbox.router, prefix="/api/sandbox", tags=["sandbox"])


@app.get("/")
def root():
    return {"message": "Sandbox System API"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
