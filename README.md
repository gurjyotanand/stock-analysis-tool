# 📈 Stock Analysis Tool with AI & Automation

This project analyzes your stock portfolio using real-time data from **Polygon.io**, generates technical insights using **OpenAI GPT-4o**, and sends updates to **Telegram**. It reads your positions from **Google Sheets**, processes data daily, and runs automatically via **GitHub Actions**.

---

## ⚙️ Features

- 🔁 **Automated Daily Analysis**
- 📊 **Live Price & P/L Calculations**
- 🤖 **AI-Generated Technical Analysis** (GPT-4o)
- 📤 **Telegram Alerts**
- 🧾 **Google Sheets Integration**
- ☁️ **GitHub Actions Cron Jobs**
- 🛡️ **Rate Limit Safe via Decorators**

---

## 📁 Project Structure

```

stock-analysis-tool/
├── main.py                    # Main script
├── .env                       # Secrets for local testing (excluded from Git)
├── credentials.json           # Google Sheets service account (not used directly)
├── requirements.txt           # Python dependencies
├── .github/
│   └── workflows/
│       └── stock-check.yml    # GitHub Actions automation

````

---

## 🧪 Local Setup

### 1. Clone the Repo

```bash
git clone https://github.com/yourusername/stock-analysis-tool.git
cd stock-analysis-tool
````

### 2. Set Up Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Create a `.env` File

```env
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
POLYGON_API_KEY=your_polygon_api_key
GOOGLE_CREDS_JSON={"type":"service_account", ...}  # Minified credentials.json
```

> 💡 Use [jsonformatter.org/minify](https://jsonformatter.org/minify) to convert your full `credentials.json` to a single line.

### 5. Run It Locally

```bash
python main.py
```

---

## ☁️ GitHub Actions Automation

### GitHub Workflow: `.github/workflows/stock-check.yml`

The script auto-runs every weekday at 10AM ET.

```yaml
on:
  schedule:
    - cron: "0 14 * * 1-5"  # 10 AM ET (UTC is 4 hours ahead)
  workflow_dispatch:
```

### Required GitHub Secrets

Set these in **Repo → Settings → Secrets and Variables → Actions**:

| Secret Name          | Description                              |
| -------------------- | ---------------------------------------- |
| `OPENAI_API_KEY`     | OpenAI GPT-4o API key                    |
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token                  |
| `TELEGRAM_CHAT_ID`   | Your Telegram chat/user ID               |
| `POLYGON_API_KEY`    | Polygon.io API Key                       |
| `GOOGLE_CREDS_JSON`  | Raw minified content of credentials.json |

---

## 📝 Google Sheet Format

Create a sheet like this:

| Ticker | BuyInPrice | Quantity |
| ------ | ---------- | -------- |
| AAPL   | 172.50     | 10       |
| TSLA   | 243.80     | 5        |

* Sheet name: `stock-sheet-gurjyot`
* Worksheet name: `Sheet1`

---

## 🛡️ Rate Limiting

* Polygon API: Limited to 5 calls/minute (free tier)
* `ratelimit` decorators ensure safe batching

---

## 📬 Output Example (Telegram)

```
📊 USD Stock Update (2025-06-26 10:00 AM ET)

💸 AAPL
- Price: $195.23 (+1.32%)
- Qty: 10 @ $172.50
- P/L: 🟢 +$227.30

🧠 AI View
- Daily Timeframe: Bullish
- Weekly Timeframe: Bullish
...
────────────
```

---

## 🚀 Future Improvements

* Add AI-generated buy/sell price thresholds
* Support for crypto portfolios
* Multilingual Telegram support
* Web UI dashboard with history tracking

---

## 👨‍💻 Author

**Gurjyot Anand**
DevOps Engineer | Cloud Architect | SaaS Builder
📍 Toronto, Canada
💼 [LinkedIn](https://www.linkedin.com/in/gurjyotanand/) | 💻 [GitHub](https://github.com/gurjyotanand)

---

## 📄 License

MIT – feel free to fork, customize, and use this tool.

```

---
