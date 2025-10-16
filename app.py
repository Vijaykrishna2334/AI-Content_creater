import streamlit as st
import os
from utils.content_pipeline import ContentPipeline
from dotenv import load_dotenv
from datetime import datetime # ADDED: For handling dates and times
from apscheduler.schedulers.background import BackgroundScheduler # ADDED: For scheduling jobs

# Load environment variables
load_dotenv()
import streamlit_shadcn_ui as ui
from config.sources import NEWS_SOURCES

st.set_page_config(page_title="CreatorPulse", page_icon="📰", layout="wide")

# --- SCHEDULER SETUP (NEW) ---
# Initialize the scheduler and store it in session state to ensure it runs only once.
if 'scheduler' not in st.session_state:
    st.session_state.scheduler = BackgroundScheduler()
    st.session_state.scheduler.start()
    st.session_state.scheduled_jobs = [] # Keep track of job info

# --- JOB FUNCTION (NEW) ---
# This function contains the core logic. It will be called by the scheduler.
# It can't use session_state, so we must pass all required data as arguments.
def generate_and_send_newsletter(groq_key, resend_key, from_addr, to_addr, urls, rss_urls, title):
    """
    Initializes the pipeline and processes the newsletter.
    This function is designed to be run in the background.
    """
    print(f"[{datetime.now()}] Running scheduled job for {to_addr} with title '{title}'")
    try:
        pipeline = ContentPipeline(
            groq_api_key=groq_key,
            resend_api_key=resend_key,
            from_email=from_addr
        )
        pipeline.process_mixed_sources(
            urls=urls,
            rss_urls=rss_urls,
            max_rss_items=5,
            email_recipients=[to_addr],
            digest_title=title
        )
        print(f"[{datetime.now()}] Successfully completed job for {to_addr}")
    except Exception as e:
        print(f"[{datetime.now()}] ERROR in scheduled job for {to_addr}: {e}")

# --- APP UI ---
st.title("📰 CreatorPulse: Your AI Newsletter")
st.caption("Get curated AI insights, on-demand or on your schedule.")

# Initialize session state for pipeline
if 'pipeline' not in st.session_state:
    st.session_state.pipeline = None

# Sidebar for API configuration
with st.sidebar:
    st.header("🔧 Configuration")
    
    # API Keys
    groq_api_key = st.text_input("Groq API Key", type="password", help="Enter your Groq API key", value=os.getenv('GROQ_API_KEY', ''))
    resend_api_key = st.text_input("Resend API Key", type="password", help="Enter your Resend API key", value=os.getenv('RESEND_API_KEY', ''))
    
    # Email settings
    from_email = st.text_input("From Email", value=os.getenv('FROM_EMAIL', 'noreply@yourdomain.com'), help="Sender email address")
    
    # Initialize pipeline if API keys are provided
    if groq_api_key and resend_api_key:
        try:
            if not st.session_state.pipeline: # Only initialize if not already done
                st.session_state.pipeline = ContentPipeline(
                    groq_api_key=groq_api_key,
                    resend_api_key=resend_api_key,
                    from_email=from_email
                )
            st.success("✅ Pipeline initialized!")
        except Exception as e:
            st.error(f"❌ Pipeline failed: {str(e)}")
    else:
        st.warning("⚠️ Enter API keys to start")
    
    # --- ADDED: Display Scheduled Jobs in Sidebar ---
    st.header("⏰ Scheduled Newsletters")
    if st.session_state.scheduled_jobs:
        for job_info in st.session_state.scheduled_jobs:
            st.info(f"To: {job_info['email']}\nOn: {job_info['time'].strftime('%b %d, %Y at %I:%M %p')}")
    else:
        st.write("No jobs scheduled.")

# Step 1: Topic Selection
st.subheader("1. Choose Your Topics")
selected_categories = ui.tabs(options=list(NEWS_SOURCES.keys()), default_value='AI', key="topic_tabs")
st.write(f"You selected: **{selected_categories}**")

# Step 2: Email Input
st.subheader("2. Enter Your Email")
user_email = ui.input(default_value="", type="email", placeholder="your@email.com", key="email_input")

# Step 3: Custom URLs (Optional)
st.subheader("3. Add Custom Sources (Optional)")
custom_urls = st.text_area("Enter custom URLs (one per line)", placeholder="https://example.com\nhttps://news.ycombinator.com", height=100)
custom_rss = st.text_area("Enter RSS feeds (one per line)", placeholder="https://feeds.bbci.co.uk/news/rss.xml", height=100)

# --- MODIFIED: Step 4: Scheduling and Generation ---
st.subheader("4. Choose When to Send")
schedule_toggle = st.toggle("Schedule for a later time?", key="schedule_toggle")

if schedule_toggle:
    col1, col2 = st.columns(2)
    with col1:
        schedule_date = st.date_input("Select a date")
    with col2:
        schedule_time = st.time_input("Select a time")
    
    # Combine date and time into a single datetime object
    scheduled_datetime = datetime.combine(schedule_date, schedule_time)

# --- MODIFIED: Button Logic ---
button_text = "🗓️ Schedule Newsletter" if schedule_toggle else "🚀 Generate Now"
if ui.button(button_text, key="generate_btn"):
    if not st.session_state.pipeline:
        st.error("❌ Please configure API keys first")
    elif not user_email:
        st.error("❌ Please enter your email address")
    else:
        # Get sources for selected category
        selected_sources = NEWS_SOURCES.get(selected_categories, [])
        urls = [source['url'] for source in selected_sources]
        
        # Add custom URLs
        if custom_urls:
            urls.extend([url.strip() for url in custom_urls.split('\n') if url.strip()])
        
        # Add RSS feeds
        rss_urls = [url.strip() for url in custom_rss.split('\n') if url.strip()] if custom_rss else []
        
        if not urls and not rss_urls:
            st.error("❌ No sources selected. Please choose topics or add custom URLs.")
        
        # --- MODIFIED: Conditional Logic for Run Now vs. Schedule ---
        elif schedule_toggle:
            # --- SCHEDULE LOGIC ---
            if scheduled_datetime <= datetime.now():
                st.error("❌ Scheduled time must be in the future.")
            else:
                st.session_state.scheduler.add_job(
                    generate_and_send_newsletter,
                    trigger='date',
                    run_date=scheduled_datetime,
                    args=[groq_api_key, resend_api_key, from_email, user_email, urls, rss_urls, f"Your {selected_categories} Newsletter"]
                )
                # Store job info for display
                st.session_state.scheduled_jobs.append({'email': user_email, 'time': scheduled_datetime})
                st.success(f"✅ Newsletter scheduled for {scheduled_datetime.strftime('%A, %B %d at %I:%M %p')}!")
        
        else:
            # --- RUN NOW LOGIC (Same as before) ---
            with st.spinner("🔄 Generating your personalized newsletter..."):
                results = st.session_state.pipeline.process_mixed_sources(
                    urls=urls,
                    rss_urls=rss_urls,
                    max_rss_items=5,
                    email_recipients=[user_email],
                    digest_title=f"Your {selected_categories} Newsletter"
                )
                
                if results["success"]:
                    st.success(f"✅ Newsletter generated! Processed {len(results['articles'])} articles.")
                    st.subheader("📰 Your Newsletter")
                    st.markdown(results["digest_content"])
                    if "email_response" in results and "error" not in results["email_response"]:
                        st.success("📧 Newsletter sent to your email!")
                    else:
                        st.warning(f"⚠️ Email sending failed: {results.get('email_response', {}).get('error', 'Unknown error')}")
                    st.session_state.last_results = results
                else:
                    st.error(f"❌ Newsletter generation failed: {results['error']}")

# Display last results if available (for "Generate Now" option)
if 'last_results' in st.session_state and st.session_state.last_results:
    with st.expander("📊 View Article Details"):
        pass

# --- ADDED: Database Dashboard Section ---
st.sidebar.markdown("---")
st.sidebar.header("📊 Database Status")

# Add a button to refresh database stats
if st.sidebar.button("🔄 Refresh Stats"):
    st.rerun()

try:
    from db import get_client, get_recent_content
    
    # Get database client
    client = get_client()
    
    # Get recent content
    content = get_recent_content(limit=10)
    
    # Query specific tables
    users = client.table('users').select('*').execute()
    sources = client.table('sources').select('*').execute()
    
    # Display stats in sidebar
    st.sidebar.metric("👥 Users", len(users.data))
    st.sidebar.metric("📰 Sources", len(sources.data))
    st.sidebar.metric("📄 Content Items", len(content))
    
    # Show recent content in main area
    if content:
        st.subheader("📄 Recent Content")
        for item in content[:5]:  # Show last 5 items
            with st.expander(f"📰 {item.get('title', 'Untitled')[:50]}..."):
                st.write(f"**Source:** {item.get('source_url', 'N/A')}")
                st.write(f"**Created:** {item.get('created_at', 'N/A')}")
                st.write(f"**Summary:** {item.get('summary', 'No summary available')[:200]}...")
    else:
        st.info("No content generated yet. Create your first newsletter!")
        
except Exception as e:
    st.sidebar.error(f"Database connection failed: {str(e)}")
    st.sidebar.info("Make sure SUPABASE_URL and SUPABASE_ANON_KEY are set in your .env file")