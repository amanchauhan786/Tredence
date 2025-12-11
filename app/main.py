# (1.) FastAPI application entry point
# (2.) Initializes the workflow engine API server

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.routes import router
from app.workflows.code_review import register_code_review_tools


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    (1.) Application lifespan handler
    (2.) Registers tools on startup
    """
    # (1.) Register sample workflow tools
    # (2.) Makes handlers available for execution
    register_code_review_tools()
    yield


# (1.) Create FastAPI application instance
# (2.) Configure metadata for API documentation
app = FastAPI(
    title="Agent Workflow Engine",
    description="A minimal graph-based workflow execution system",
    version="1.0.0",
    lifespan=lifespan
)

# (1.) Include API routes
# (2.) All graph-related endpoints under /graph prefix
app.include_router(router, prefix="/graph", tags=["graph"])


@app.get("/health")
async def health_check():
    """
    (1.) Health check endpoint
    (2.) Returns service status for monitoring
    """
    return {"status": "healthy"}
