# AI Content Creator - Newsletter Generator

A complete content generation and distribution system that scrapes content from various sources, processes it with AI, and sends personalized newsletters via email.

## 🚀 Features

- **Web Scraping**: Extract content from URLs and RSS feeds
- **AI Processing**: Use Groq LLM for content summarization and analysis
- **Email Distribution**: Send newsletters via Resend email service
- **Streamlit UI**: User-friendly web interface
- **Multiple Sources**: Support for custom URLs, RSS feeds, and predefined news sources

## 📋 Prerequisites

- Python 3.8+
- Groq API key
- Resend API key
- Valid email domain (for sending emails)

## 🛠️ Installation

1. **Clone the repository**
   ```bash
   git clone <your-repo-url>
   cd AI-Content_creater
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   ```
   
   Edit `.env` and add your API keys:
   ```
   GROQ_API_KEY=your_groq_api_key_here
   RESEND_API_KEY=your_resend_api_key_here
   FROM_EMAIL=noreply@yourdomain.com
   ```

## 🚀 Usage

### Running the Streamlit App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Using the Pipeline Directly

```python
from content_pipeline import ContentPipeline

# Initialize pipeline
pipeline = ContentPipeline(
    groq_api_key="your_groq_key",
    resend_api_key="your_resend_key"
)

# Process URLs
urls = ["https://example.com", "https://news.ycombinator.com"]
results = pipeline.process_urls(
    urls=urls,
    email_recipients=["test@example.com"],
    digest_title="My Newsletter"
)

print(f"Processed {len(results['articles'])} articles")
```

## 📁 Project Structure

```
AI-Content_creater/
<<<<<<< HEAD
├── app.py                    # Streamlit web application
├── content_pipeline.py       # Main pipeline orchestrator
├── scraper.py               # Web scraping functionality
├── groq_processor.py        # Groq LLM integration
├── email_sender.py          # Resend email service
├── auth.py                  # Authentication system
├── db.py                    # Database operations
├── local_cache.py           # Local caching system
├── local_storage.py         # Local storage management
├── style_training.py        # Writing style training
├── writing_styles.py        # Writing style management
├── twitter_processor.py     # Twitter integration
├── youtube_processor.py     # YouTube integration
├── requirements.txt         # Python dependencies
├── .gitignore              # Git ignore rules
├── env_example.txt         # Environment variables template
├── sources.json            # News sources configuration
├── LICENSE                  # MIT License
├── README.md               # This file
├── config/
│   └── sources.py          # Predefined news sources
├── utils/
│   ├── __init__.py
│   └── misc.py             # Utility functions
├── scripts/                # Maintenance scripts
│   ├── cleanup_users_uploaded_newsletters.py
│   ├── run_cleanup.ps1
│   └── README.md
├── tests/                  # Test files
│   ├── __init__.py
│   └── test_basic.py
└── docs/                   # Documentation
    ├── CODE_OF_CONDUCT.md
    └── CONTRIBUTING.md
=======
├── app.py                 # Streamlit web application
├── content_pipeline.py    # Main pipeline orchestrator
├── scraper.py            # Web scraping functionality
├── groq_processor.py     # Groq LLM integration
├── email_sender.py       # Resend email service
├── requirements.txt      # Python dependencies
├── .gitignore           # Git ignore rules
├── env_example.txt      # Environment variables template
└── config/
    └── sources.py       # Predefined news sources
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15
```

## 🔧 Configuration

### API Keys

1. **Groq API Key**: Get from [console.groq.com](https://console.groq.com)
2. **Resend API Key**: Get from [resend.com](https://resend.com)

### Email Configuration

- Set up a domain with Resend
- Configure DNS records as required by Resend
- Use a valid sender email address

## 📊 Pipeline Flow

1. **Input**: URLs, RSS feeds, or predefined sources
2. **Scraping**: Extract content using BeautifulSoup and feedparser
3. **Processing**: Summarize and analyze with Groq LLM
4. **Digest Creation**: Generate formatted newsletter content
5. **Email Sending**: Distribute via Resend email service

## 🛠️ Customization

### Adding New Sources

Edit `config/sources.py` to add new news sources:

```python
NEWS_SOURCES = {
    "Technology": [
        {
            "name": "TechCrunch",
            "url": "https://techcrunch.com",
            "description": "Latest tech news"
        }
    ]
}
```

### Modifying Scraping Logic

Edit `scraper.py` to customize content extraction:

```python
def scrape_url(self, url: str) -> Dict[str, str]:
    # Custom scraping logic here
    pass
```

### Customizing AI Processing

Edit `groq_processor.py` to modify summarization prompts:

```python
def summarize_article(self, article: Dict[str, str]) -> str:
    # Custom summarization logic here
    pass
```

## 🐛 Troubleshooting

### Common Issues

1. **Streamlit Context Warning**: Run with `streamlit run app.py` instead of `python app.py`
2. **API Key Errors**: Ensure environment variables are set correctly
3. **Email Sending Fails**: Check Resend configuration and domain setup
4. **Scraping Issues**: Some websites may block automated requests

### Debug Mode

Enable debug logging by modifying the logging level:

```python
logging.basicConfig(level=logging.DEBUG)
```

## 📝 License

This project is licensed under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

<<<<<<< HEAD
## 🚀 GitHub Ready

This repository is now properly structured for GitHub with:

- **Clean Structure**: Organized files into logical directories (`docs/`, `tests/`, `scripts/`)
- **Security**: Comprehensive `.gitignore` to exclude sensitive data and temporary files
- **Documentation**: Complete setup and usage instructions
- **Testing**: Basic test framework included
- **Maintenance**: Scripts for cleanup and maintenance

### Files Excluded from GitHub:
- Virtual environment (`venv/`)
- User data (`users.json`, `sessions.json`, `content_cache.json`)
- Cache files (`__pycache__/`, `*.pyc`)
- Development documentation and notes
- Temporary files and backups

### Before First Push:
1. Create a virtual environment: `python -m venv venv`
2. Activate it: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Linux/Mac)
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `env_example.txt` to `.env` and add your API keys
5. Run tests: `python -m pytest tests/`

=======
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15
## 📞 Support

For issues and questions:
- Check the troubleshooting section
- Review the logs for error messages
- Ensure all API keys are valid and properly configured