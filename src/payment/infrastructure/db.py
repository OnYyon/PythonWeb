from pathlib import Path

import asyncpg

SCHEMA_PATH = Path(__file__).with_name("sql") / "schema.sql"
SCHEMA_LOCK_ID = 917263548


class Database:
    def __init__(self, *, dsn: str, min_size: int = 1, max_size: int = 10) -> None:
        self._dsn = dsn
        self._min_size = min_size
        self._max_size = max_size
        self._pool: asyncpg.Pool | None = None

    async def connect(self) -> None:
        if self._pool is None:
            self._pool = await asyncpg.create_pool(
                dsn=self._dsn, min_size=self._min_size, max_size=self._max_size
            )
            await self._ensure_schema()

    async def _ensure_schema(self) -> None:
        if self._pool is None:
            return

        async with self._pool.acquire() as connection:
            await connection.execute("SELECT pg_advisory_lock($1)", SCHEMA_LOCK_ID)
            try:
                await connection.execute(SCHEMA_PATH.read_text(encoding="utf-8"))
            finally:
                await connection.execute(
                    "SELECT pg_advisory_unlock($1)", SCHEMA_LOCK_ID
                )

    async def disconnect(self) -> None:
        if self._pool is not None:
            await self._pool.close()
            self._pool = None

    @property
    def pool(self) -> asyncpg.Pool:
        if self._pool is None:
            raise RuntimeError("Database pool is not initialized")
        return self._pool
