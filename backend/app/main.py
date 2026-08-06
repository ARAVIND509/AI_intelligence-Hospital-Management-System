from fastapi import FastAPI

app = FastAPI(
    title="MediMind AI Backend",
    description="AI-Powered Hospital Intelligence System",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {
        "success": True,
        "message": "Welcome to MediMind AI Backend 🚀"
    }


@app.get("/health")
async def health():
    return {
        "success": True,
        "message": "Application is healthy",
        "data": {
            "status": "running"
        }
    }