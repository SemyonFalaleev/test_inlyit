from sqlalchemy import select
from src.db.base import AsyncSessionLocal
from src.db.models.user import User

async def get_user_from_db(user_id: int):
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
    
    return user