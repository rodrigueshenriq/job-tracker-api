
from fastapi import FastAPI
from database.database import Base, engine
from routers import agent, applications

Base.metadata.create_all(bind=engine)

app = FastAPI()
app.include_router(applications.router, prefix="/applications", tags=["Job Applications"])
app.include_router(agent.tool_router, prefix="/agent", tags=["Agent Demo"])
app.include_router(agent.confirmation_router, prefix="/agent", tags=["Human Approval"])

@app.get("/")
def read_root():
    return {"message": "Welcome to the Job Tracker API!"}
