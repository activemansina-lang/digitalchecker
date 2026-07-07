STRINGS = {
    "welcome": "👋 Welcome to <b>DigitalChecker</b>!\n\nJust send the name of any cryptocurrency or Telegram NFT Gift to get instant data. No commands needed.\n\nExample: <code>bitcoin</code>, <code>btc</code>, or <code>Plush Pepe</code>",
    "choose_language": "🌐 Choose your preferred language:",
    "language_set": "✅ Language set to English.",
    "help": (
        "📖 <b>How to use</b>\n\n"
        "Just send the asset name:\n"
        "• <code>btc</code>, <code>bitcoin</code>\n"
        "• <code>eth</code>, <code>ethereum</code>\n"
        "• <code>ton</code>\n"
        "• <code>Plush Pepe</code> (NFT Gift)\n\n"
        "Commands:\n"
        "/start - Start and choose language\n"
        "/help - This help message\n"
        "/support - Contact support"
    ),
    "support": "🛟 For support, contact: {link}",
    "not_found": "❌ Nothing found for \"{query}\". Please try another name.",
    "searching_error": "⚠️ Error fetching data. Please try again shortly.",
    "crypto_card": (
        "💰 <b>{name}</b> ({symbol})\n\n"
        "Price: <b>${price:,.4f}</b>\n"
        "24h Change: {change_emoji} <b>{change:+.2f}%</b>\n"
        "Market Rank: #{rank}\n"
        "Market Cap: ${market_cap:,.0f}\n"
        "24h Volume: ${volume:,.0f}\n"
        "Circulating Supply: {supply}\n"
        "All-Time High (ATH): ${ath:,.4f}\n"
        "All-Time Low (ATL): ${atl:,.4f}"
    ),
    "nft_card": (
        "🎁 <b>{name}</b>\n"
        "Collection: {collection}\n\n"
        "Floor Price: {floor:,.2f} TON\n"
        "Last Sale: {last_sale:,.2f} TON\n"
        "Average Price: {average:,.2f} TON\n"
        "Estimated Value: ${estimated_usd:,.2f}\n"
        "Rarity Score: {rarity:.1f}\n\n"
        "⚠️ NFT Gift data comes from our internal catalog's latest update (Telegram has no official public market API)."
    ),
    "added_to_watchlist": "⭐️ Added to your watchlist.",
    "already_in_watchlist": "ℹ️ This is already in your watchlist.",
    "removed_from_watchlist": "🗑 Removed from your watchlist.",
    "watchlist_empty": "Your watchlist is empty.",
    "watchlist_title": "⭐️ <b>Your watchlist:</b>",
    "alert_prompt": "🔔 Enter the target USD price for <b>{name}</b> (e.g. 150000):",
    "alert_created": "✅ Price alert set for {name} at ${target:,.4f}.",
    "alert_invalid_number": "❌ Please enter a valid number.",
    "alert_triggered": "🔔 Alert! {name} reached your target of ${target:,.4f}.\nCurrent price: ${current:,.4f}",
    "alerts_list_title": "🔔 <b>Your active alerts:</b>",
    "alerts_empty": "You have no active alerts.",
    "buttons": {
        "add_watchlist": "⭐️ Add to watchlist",
        "remove_watchlist": "🗑 Remove from watchlist",
        "set_alert": "🔔 Set price alert",
        "refresh": "🔄 Refresh",
        "back": "🔙 Back",
        "fa": "🇮🇷 فارسی",
        "en": "🇺🇸 English",
    },
}
