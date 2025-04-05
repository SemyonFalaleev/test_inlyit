from typing import List
import uvicorn
from fastapi import FastAPI
from src.routers.user import router as user_router
from src.routers.advertisement import router as adv_router
from src.routers.category import router as cat_router
from src.routers.auth import router as auth_router
app = FastAPI()

app.include_router(user_router)
app.include_router(adv_router)
app.include_router(cat_router)
app.include_router(auth_router)



if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)