# DigitalChecker 🤖

ربات تلگرام چندزبانه برای دریافت آنی قیمت ارزهای دیجیتال و Telegram NFT Gifts — کافیه اسم دارایی رو بفرستی، بدون دستور خاص.

## معماری

```
app/
  config.py            تنظیمات (env)
  database/            مدل‌های SQLAlchemy + engine async
  services/             crypto_service (CoinGecko), nft_service (کاتالوگ داخلی),
                         search_service (تشخیص فارسی/انگلیسی + کریپتو/NFT), alert_service, cache (Redis)
  handlers/             start, help/support, search (متن آزاد), watchlist, alerts
  middlewares/           throttling (rate limit), i18n
  workers/               alert_worker.py - چک دوره‌ای هشدارهای قیمتی
alembic/                 مایگریشن دیتابیس
scripts/seed_nft_gifts.py  دیتای اولیه NFT Gift
```

## نکته مهم درباره‌ی NFT Gift

تلگرام **API عمومی رسمی** برای قیمت NFT Gift ارائه نمی‌کند. قیمت‌ها فقط در مارکت‌پلیس‌هایی مثل Fragment/Portals/Tonnel قابل مشاهده‌اند که API عمومی پایداری ندارند. به همین دلیل این پروژه یک جدول کاتالوگ داخلی (`nft_gifts`) دارد که با اسکریپت `scripts/seed_nft_gifts.py` پر می‌شود؛ در آینده کافیه `NftService` را به یک منبع واقعی (اسکرپینگ/API) وصل کنید — بقیه‌ی ربات نیازی به تغییر ندارد.

## اجرا با Docker Compose (لوکال)

```bash
cp .env.example .env   # BOT_TOKEN رو بذار
docker compose up --build -d
docker compose exec bot python -m scripts.seed_nft_gifts
```

## دیپلوی روی Railway

1. ریپازیتوری رو به Railway وصل کن (New Project → Deploy from GitHub) یا با CLI:
   ```bash
   npm i -g @railway/cli
   railway login
   railway init
   railway up
   ```
2. از Railway Marketplace دو پلاگین اضافه کن: **PostgreSQL** و **Redis** — Railway به‌صورت خودکار متغیرهای `DATABASE_URL` و `REDIS_URL` رو به سرویس bot تزریق می‌کنه.
3. در تب Variables سرویس، این‌ها رو دستی ست کن:
   - `BOT_TOKEN`
   - `SUPPORT_CHAT_LINK`
4. Railway از `railway.json` استفاده می‌کنه (بیلد با Dockerfile، اجرای `alembic upgrade head && python -m app.main`).
5. بعد از اولین دیپلوی، یک‌بار دیتای NFT رو seed کن:
   ```bash
   railway run python -m scripts.seed_nft_gifts
   ```

## دستورات ربات

- `/start` — شروع و انتخاب زبان
- `/help` — راهنما
- `/support` — پشتیبانی
- `/watchlist` — لیست علاقه‌مندی‌ها
- `/alerts` — هشدارهای فعال

برای استفاده، کافیه هر نام ارز یا NFT رو مستقیم بفرستی (فارسی یا انگلیسی) — هم در چت خصوصی و هم داخل گروه/سوپرگروه (privacy mode بات رو در BotFather خاموش کن تا پیام‌های گروه رو ببینه).

## Migration جدید ساختن

```bash
alembic revision --autogenerate -m "توضیح تغییر"
alembic upgrade head
```

## محدودیت‌های شناخته‌شده / بهبودهای پیشنهادی

- جستجوی کریپتو از CoinGecko عمومی استفاده می‌کنه (rate limit ~10-30 req/min)؛ برای ترافیک بالا یک API key پولی (`COINGECKO_API_KEY`) یا لایه کش سنگین‌تر لازمه.
- تشخیص Contract Address فعلاً فقط شبکه Ethereum رو امتحان می‌کنه؛ برای BSC/Polygon/... باید platform اضافه بشه.
- هشدارهای درصدی (`percent_up`/`percent_down`) در سرویس پیاده شدن ولی UI فعلی فقط فرم «هدف قیمتی» رو می‌سازه؛ برای فعال‌سازی کامل باید یک مرحله انتخاب نوع هشدار به FSM اضافه بشه.
- کاتالوگ NFT باید به‌صورت دوره‌ای (کرون یا اسکریپت ادمین) آپدیت بشه چون منبع زنده‌ای وجود نداره.
