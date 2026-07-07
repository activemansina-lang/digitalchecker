from __future__ import annotations

import asyncio

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


async def main() -> None:
    setup_logging()
    logger.info("Starting DigitalChecker bot...")

    bot = Bot(token=settings.bot_token, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
    storage = RedisStorage(redis=redis)
    dp = Dispatcher(storage=storage)

    dp.message.middleware(ThrottlingMiddleware())
    dp.message.middleware(I18nMiddleware())
    dp.callback_query.middleware(I18nMiddleware())

    dp.include_router(get_root_router())

    worker_task = asyncio.create_task(run_alert_worker(bot))

    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(bot)
    finally:
        worker_task.cancel()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
