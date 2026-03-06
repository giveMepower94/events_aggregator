from sqlalchemy.ext.asyncio import (AsyncSession,
                                    AsyncEngine,
                                    create_async_engine,
                                    async_sessionmaker)
from typing import AsyncGenerator


from src.events_agg.core.config import settings


# Создаем движок
engine: AsyncEngine = create_async_engine(settings.database_url,
                                          future=True,
                                          echo=False)

# Создаем асинхронную локальную сессию
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession
)


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
