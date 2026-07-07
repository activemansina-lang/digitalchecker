from __future__ import annotations

import sys
import asyncio

print("STEP 0: main.py module loading", flush=True, file=sys.stderr)

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from loguru import logger

from app.config import settings
from app.handlers import get_root_router
from app.middlewares.i18n import I18nMiddleware
from app.middlewares.throttling import ThrottlingMiddleware
from app.services.cache import redis
from app.utils.logger import setup_logging
from app.workers.alert_worker import run_alert_worker

print("STEP 0.5: all imports finished", flush=True, file=sys.stderr)


async def main() -> None:
    print("STEP 1: entered main()", flush=True, file=sys.stderr)
    setup_logging()
    logger.info("Starting DigitalChecker bot...")

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    print("STEP 2: Bot object created", flush=True, file=sys.stderr)

    storage = RedisStorage(redis=redis)
    print("STEP 3: RedisStorage created", flush=True, file=sys.stderr)

    dp = Dispatcher(storage=storage)

    dp.message.middleware(ThrottlingMiddleware())
    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())

    dp.include_router(get_root_router())

    worker_task = asyncio.create_task(run_alert_worker(bot))

    try:
        print("STEP 4: calling delete_webhook", flush=True, file=sys.stderr)
        await bot.delete_webhook(drop_pending_updates=True)
        print("STEP 5: delete_webhook done, starting polling", flush=True, file=sys.stderr)
        await dp.start_polling(bot)
    finally:
        worker_task.cancel()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
