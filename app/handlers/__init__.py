from __future__ import annotations

from aiogram import Router

from app.handlers import alerts, help_support, search, start, watchlist


def get_root_router() -> Router:
    root = Router(name="root")
    # Order matters: commands/callbacks first, free-text catch-all (search) last.
    root.include_router(start.router)
    root.include_router(help_support.router)
    root.include_router(watchlist.router)
    root.include_router(alerts.router)
    root.include_router(search.router)
    return root
