from fastapi import FastAPI
from workout_api.routers import api_router

app = FastAPI(title='workoutAPI')
app.include_router(api_router)

