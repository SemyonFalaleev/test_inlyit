from fastapi.responses import JSONResponse
import uvicorn
from fastapi import FastAPI, Request

from src.config import settings
from src.utils.tg import bot

from src.routers.user import router as user_router
from src.routers.advertisement import router as adv_router
from src.routers.category import router as cat_router
from src.routers.auth import router as auth_router
from src.routers.complaint import router as comp_router
from src.routers.review import router as review_router
from src.utils.logg import logger, log_request_middleware


app = FastAPI()

@app.exception_handler(Exception)
async def global_handler(request: Request, exc: Exception):
    await bot.send_message(
        chat_id=settings.telegram_chat_id,
        text=f"🔥 Ошибка в {request.url}:\n{str(exc)}"
    )
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal Server Error"}
    )

app.middleware("http")(log_request_middleware)

app.include_router(user_router)
app.include_router(adv_router)
app.include_router(cat_router)
app.include_router(auth_router)
app.include_router(comp_router)
app.include_router(review_router)

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)