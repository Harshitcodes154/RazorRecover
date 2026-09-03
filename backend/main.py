from fastapi import FastAPI
from backend.api.recovery import router as recovery_router

app = FastAPI(
    title="RazorRecover",
    description="Autonomous AI Revenue Recovery Agent",
    version="1.0.0",
)

app.include_router(recovery_router)


@app.get("/")
def root():
    return {
        "project": "RazorRecover",
        "status": "running",
        "message": "Autonomous Revenue Recovery Agent is online"
    }


@app.get("/health")
def health():
    return {
        "status": "healthy"
    }