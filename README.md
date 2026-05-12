<div align="center">

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,24&height=160&section=header&text=AI%20Content%20Creator&fontSize=40&fontColor=fff&animation=twinkling&fontAlignY=36&desc=Automated%20Newsletter%20Generator%20Powered%20by%20Groq%20LLM&descAlignY=58&descSize=15" width="100%"/>

[![Python](https://img.shields.io/badge/Python_3.8+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![Groq](https://img.shields.io/badge/Groq_LLM-F55036?style=for-the-badge&logo=groq&logoColor=white)](https://groq.com/)
[![Resend](https://img.shields.io/badge/Resend-000000?style=for-the-badge&logo=mail&logoColor=white)](https://resend.com/)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

**Web scraping · Groq LLM summarization · Automated email delivery · Multi-source support**

</div>

---

## 🎯 What It Does

AI Content Creator scrapes content from any URL, RSS feed, or predefined news source — then uses **Groq's Llama LLM** to summarize, analyze, and package it into a polished newsletter delivered straight to your subscribers via email.

---

## ✨ Key Features

| Feature | Description |
|---|---|
| 🕷️ **Web Scraping** | Extract content from URLs, RSS feeds, and news sources |
| 🤖 **Groq LLM** | Llama-powered summarization and content analysis |
| 📧 **Email Delivery** | Automated newsletter sending via Resend API |
| 🎨 **Streamlit UI** | Full web interface with auth, scheduling, and style training |
| 🐦 **Twitter Integration** | Pull content from Twitter profiles and hashtags |
| 📺 **YouTube Integration** | Summarize YouTube video transcripts |
| 🖊️ **Style Training** | Train the AI on your writing voice from past newsletters |
| 🔐 **Auth System** | User login, session management, and profile persistence |

---

## 🏗️ How It Works

```
User adds sources (URLs, RSS, Twitter, YouTube)
        ↓
Scraper extracts raw content
        ↓
Groq Llama LLM summarizes + analyzes each article
        ↓
Digest assembled with user's trained writing style
        ↓
Resend API delivers newsletter to subscribers
        ↓
Delivery logged → next run scheduled automatically
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **UI** | Streamlit — web interface + scheduling dashboard |
| **AI/LLM** | Groq API + Llama 3 — summarization + style generation |
| **Scraping** | BeautifulSoup + feedparser — web + RSS extraction |
| **Email** | Resend API — transactional email delivery |
| **Auth** | Custom auth with local session management |
| **Integrations** | Twitter API · YouTube Data API |

---

## ⚡ Quick Start

### Prerequisites
- Python 3.8+
- Groq API key (free at [console.groq.com](https://console.groq.com))
- Resend API key (free at [resend.com](https://resend.com))

### Setup

```bash
# Clone
git clone https://github.com/Vijaykrishna2334/AI-Content_creater.git
cd AI-Content_creater

# Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp env_example.txt .env
```

Add to `.env`:
```env
GROQ_API_KEY=your_groq_api_key_here
RESEND_API_KEY=your_resend_api_key_here
FROM_EMAIL=noreply@yourdomain.com
```

```bash
# Run
streamlit run app.py
```

Open [http://localhost:8501](http://localhost:8501)

---

## 📁 Project Structure

```
AI-Content_creater/
├── app.py                    # Streamlit web app + UI
├── content_pipeline.py       # Core pipeline orchestrator
├── scraper.py                # Web + RSS scraping
├── groq_processor.py         # Groq LLM integration
├── email_sender.py           # Resend email delivery
├── auth.py                   # User authentication
├── style_training.py         # Writing style AI training
├── twitter_processor.py      # Twitter API integration
├── youtube_processor.py      # YouTube API integration
├── config/
│   └── sources.py            # Predefined news sources
├── utils/                    # Shared utilities
├── scripts/                  # Maintenance scripts
├── tests/                    # Test suite
├── env_example.txt           # Environment variables template
└── requirements.txt
```

---

## 🔌 Pipeline Usage

```python
from content_pipeline import ContentPipeline

pipeline = ContentPipeline(
    groq_api_key="your_groq_key",
    resend_api_key="your_resend_key"
)

results = pipeline.process_urls(
    urls=["https://techcrunch.com", "https://news.ycombinator.com"],
    email_recipients=["subscriber@example.com"],
    digest_title="Weekly AI Digest"
)

print(f"Processed {len(results['articles'])} articles")
```

---

## 📬 Contact

**Built by [Vijay Krishna](https://github.com/Vijaykrishna2334)**
- 📧 vijaykrishna2334@gmail.com
- 💼 [LinkedIn](https://linkedin.com/in/vijaykrishna2334)

<img src="https://capsule-render.vercel.app/api?type=waving&color=gradient&customColorList=12,20,24&height=80&section=footer" width="100%"/>
