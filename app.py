import streamlit as st
import os
import json
from content_pipeline import ContentPipeline
from dotenv import load_dotenv
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from auth import AuthManager, get_current_user
from local_storage import local_storage
from style_training import StyleAnalyzer, generate_style_prompt

# Load environment variables
load_dotenv()

# Set API keys from environment or use defaults
if not os.getenv('RESEND_API_KEY'):
    os.environ['RESEND_API_KEY'] = 're_65HYTE8T_HbZMHP675rVtDajK6f7omhY6'

# Debug: Print API key status (remove this in production)
print(f"DEBUG: GROQ_API_KEY loaded: {bool(os.getenv('GROQ_API_KEY'))}")
print(f"DEBUG: RESEND_API_KEY loaded: {bool(os.getenv('RESEND_API_KEY'))}")
print(f"DEBUG: FROM_EMAIL: {os.getenv('FROM_EMAIL', 'Not set')}")

# Set YouTube Data API key from environment
if os.getenv('YOUTUBE_DATA_API_KEY'):
    os.environ['YOUTUBE_DATA_API_KEY'] = os.getenv('YOUTUBE_DATA_API_KEY')

# Set YouTube proxy URL from environment
if os.getenv('YOUTUBE_PROXY_URL'):
    os.environ['YOUTUBE_PROXY_URL'] = os.getenv('YOUTUBE_PROXY_URL')
import streamlit_shadcn_ui as ui
from config.sources import NEWS_SOURCES

st.set_page_config(page_title="CreatorPulse", page_icon="📰", layout="wide")

# ============================================
# MODERN CSS STYLING SYSTEM
# ============================================
def inject_custom_css():
    """Inject modern, premium CSS styling"""
    st.markdown("""
    <style>
    /* ===== IMPORTS ===== */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
    
    /* ===== ROOT VARIABLES ===== */
    :root {
        --primary: #6366f1;
        --primary-light: #818cf8;
        --secondary: #8b5cf6;
        --accent: #ec4899;
        --accent-light: #f472b6;
        --success: #10b981;
        --warning: #f59e0b;
        --dark-bg: #0a0a0f;
        --card-bg: rgba(255, 255, 255, 0.03);
        --card-border: rgba(255, 255, 255, 0.08);
        --text-primary: #ffffff;
        --text-secondary: #94a3b8;
        --text-muted: #64748b;
        --gradient-1: linear-gradient(135deg, #6366f1 0%, #8b5cf6 50%, #ec4899 100%);
        --gradient-2: linear-gradient(135deg, #0ea5e9 0%, #6366f1 100%);
        --glass-bg: rgba(255, 255, 255, 0.05);
        --glass-border: rgba(255, 255, 255, 0.1);
    }
    
    /* ===== GLOBAL STYLES ===== */
    .stApp {
        background: var(--dark-bg);
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }
    
    .stApp > header {
        background: transparent !important;
    }
    
    /* Hide Streamlit branding */
    #MainMenu, footer, header[data-testid="stHeader"] {
        visibility: hidden;
    }
    
    /* ===== SIDEBAR STYLING ===== */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0f0f1a 0%, #151525 100%) !important;
        border-right: 1px solid var(--glass-border);
    }
    
    [data-testid="stSidebar"] .stRadio > label {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 12px;
        padding: 12px 16px;
        margin: 4px 0;
        transition: all 0.3s ease;
    }
    
    [data-testid="stSidebar"] .stRadio > label:hover {
        background: rgba(99, 102, 241, 0.15);
        border-color: var(--primary);
        transform: translateX(4px);
    }
    
    /* ===== BUTTON STYLES ===== */
    .stButton > button {
        background: var(--gradient-1) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 12px 28px !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 8px 25px rgba(99, 102, 241, 0.4) !important;
    }
    
    .stButton > button[kind="secondary"] {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        box-shadow: none !important;
    }
    
    .stButton > button[kind="secondary"]:hover {
        background: rgba(99, 102, 241, 0.15) !important;
        border-color: var(--primary) !important;
    }
    
    /* ===== INPUT STYLES ===== */
    .stTextInput > div > div > input,
    .stTextArea textarea,
    .stSelectbox > div > div,
    .stNumberInput input,
    .stTimeInput input {
        background: rgba(30, 30, 45, 0.9) !important;
        border: 1px solid rgba(99, 102, 241, 0.3) !important;
        border-radius: 12px !important;
        color: #ffffff !important;
        padding: 12px 16px !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput > div > div > input::placeholder,
    .stTextArea textarea::placeholder {
        color: #94a3b8 !important;
        opacity: 1 !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stTextArea textarea:focus {
        border-color: var(--primary) !important;
        box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.3) !important;
        background: rgba(40, 40, 60, 0.95) !important;
    }
    
    /* Input labels */
    .stTextInput label,
    .stTextArea label,
    .stSelectbox label,
    .stNumberInput label,
    .stTimeInput label,
    .stCheckbox label {
        color: #e2e8f0 !important;
        font-weight: 500 !important;
    }
    
    /* Selectbox dropdown */
    .stSelectbox > div > div > div {
        color: #ffffff !important;
    }
    
    /* ===== METRIC CARDS ===== */
    [data-testid="metric-container"] {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 16px !important;
        padding: 20px !important;
        backdrop-filter: blur(10px);
    }
    
    /* ===== TAB STYLES ===== */
    .stTabs [data-baseweb="tab-list"] {
        background: var(--glass-bg);
        border-radius: 16px;
        padding: 6px;
        gap: 8px;
        border: 1px solid var(--glass-border);
    }
    
    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border-radius: 12px !important;
        color: var(--text-secondary) !important;
        padding: 12px 24px !important;
        font-weight: 500 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: var(--gradient-1) !important;
        color: white !important;
    }
    
    /* ===== EXPANDER STYLES ===== */
    .streamlit-expanderHeader {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
    }
    
    /* ===== FORM STYLES ===== */
    [data-testid="stForm"] {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 24px;
        backdrop-filter: blur(10px);
    }
    
    /* ===== ALERT STYLES ===== */
    .stAlert {
        background: var(--glass-bg) !important;
        border: 1px solid var(--glass-border) !important;
        border-radius: 12px !important;
        backdrop-filter: blur(10px);
    }
    
    /* ===== CUSTOM CLASSES ===== */
    .hero-container {
        text-align: center;
        padding: 60px 20px;
        margin-bottom: 40px;
    }
    
    .hero-title {
        font-size: 4rem;
        font-weight: 800;
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 16px;
        line-height: 1.1;
    }
    
    .hero-subtitle {
        font-size: 1.4rem;
        color: var(--text-secondary);
        max-width: 600px;
        margin: 0 auto 40px;
        line-height: 1.6;
    }
    
    .feature-card {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 32px;
        text-align: center;
        transition: all 0.4s ease;
        backdrop-filter: blur(10px);
        height: 100%;
    }
    
    .feature-card:hover {
        transform: translateY(-8px);
        border-color: var(--primary);
        box-shadow: 0 20px 40px rgba(99, 102, 241, 0.2);
    }
    
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 16px;
        display: block;
    }
    
    .feature-title {
        font-size: 1.3rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 12px;
    }
    
    .feature-desc {
        color: var(--text-secondary);
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    .glass-card {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 20px;
        padding: 32px;
        backdrop-filter: blur(10px);
    }
    
    .gradient-text {
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
    }
    
    .stats-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
        gap: 20px;
        margin: 30px 0;
    }
    
    .stat-card {
        background: var(--glass-bg);
        border: 1px solid var(--glass-border);
        border-radius: 16px;
        padding: 24px;
        text-align: center;
        transition: all 0.3s ease;
    }
    
    .stat-card:hover {
        border-color: var(--primary);
        transform: translateY(-4px);
    }
    
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        background: var(--gradient-1);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    .stat-label {
        color: var(--text-secondary);
        font-size: 0.9rem;
        margin-top: 8px;
    }
    
    .section-header {
        font-size: 2rem;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 8px;
    }
    
    .section-subheader {
        color: var(--text-secondary);
        font-size: 1.1rem;
        margin-bottom: 32px;
    }
    
    /* ===== ANIMATIONS ===== */
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    @keyframes pulse-glow {
        0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.3); }
        50% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.5); }
    }
    
    .animate-float {
        animation: float 3s ease-in-out infinite;
    }
    
    .animate-pulse {
        animation: pulse-glow 2s ease-in-out infinite;
    }
    
    /* ===== SCROLLBAR ===== */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: var(--dark-bg);
    }
    
    ::-webkit-scrollbar-thumb {
        background: var(--glass-border);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: var(--primary);
    }
    </style>
    """, unsafe_allow_html=True)

# Inject CSS on every page load
inject_custom_css()

# Initialize managers
auth_manager = AuthManager()
style_analyzer = StyleAnalyzer()

# --- SCHEDULER SETUP ---
if 'scheduler' not in st.session_state:
    st.session_state.scheduler = BackgroundScheduler()
    st.session_state.scheduler.start()
    st.session_state.scheduled_jobs = []

def restore_scheduled_jobs():
    """Restore scheduled jobs from user data on app startup"""
    try:
        # Get all users with auto-delivery enabled
        users_data = auth_manager.get_all_users()
        
        for user_data in users_data:
            delivery_settings = user_data.get('delivery_settings', {})
            if delivery_settings.get('auto_delivery', False):
                # Check if job already exists
                job_id = f"newsletter_{user_data['user_id']}"
                existing_jobs = [job.id for job in st.session_state.scheduler.get_jobs()]
                
                if job_id not in existing_jobs:
                    # Restore the job
                    delivery_time = datetime.strptime(delivery_settings.get('time', '08:00'), '%H:%M').time()
                    
                    # Get sources from local storage
                    try:
                        sources = local_storage.get_user_sources(user_data['user_id'])
                    except Exception as e:
                        print(f"[{datetime.now()}] Warning: Failed to get sources from local storage: {e}")
                        sources = user_data.get('sources', [])
                    
                    style_profile = user_data.get('style_profile')
                    
                    if sources and style_profile:
                        create_scheduled_job(
                            user_data['user_id'],
                            delivery_time,
                            delivery_settings.get('email', user_data.get('email', '')),
                            sources,
                            style_profile
                        )
                        print(f"[{datetime.now()}] Restored scheduled job for user {user_data['user_id']}")
    except Exception as e:
        print(f"[{datetime.now()}] ERROR restoring scheduled jobs: {e}")

# Restore jobs on startup
restore_scheduled_jobs()

def generate_and_send_newsletter(groq_key, resend_key, from_addr, to_addr, urls, rss_urls, title, youtube_urls=None, twitter_urls=None, writing_style='professional'):
    """Generate and send newsletter in background"""
    print(f"[{datetime.now()}] Running scheduled job for {to_addr} with title '{title}'")
    try:
        pipeline = ContentPipeline(
            groq_api_key=groq_key,
            resend_api_key=resend_key,
            from_email=from_addr
        )
        pipeline.process_mixed_sources(
            urls=urls or [],
            rss_urls=rss_urls or [],
            youtube_urls=youtube_urls or [],
            twitter_urls=twitter_urls or [],
            max_rss_items=5,
            email_recipients=[to_addr],
            digest_title=title,
            writing_style=writing_style
        )
        print(f"[{datetime.now()}] Successfully completed job for {to_addr}")
    except Exception as e:
        print(f"[{datetime.now()}] ERROR in scheduled job for {to_addr}: {e}")

def create_scheduled_job(user_id, delivery_time, email, sources, style_profile):
    """Create a scheduled job for automatic newsletter delivery"""
    try:
        job_id = f"newsletter_{user_id}"
        
        # Remove existing job if it exists
        existing_jobs = [job.id for job in st.session_state.scheduler.get_jobs()]
        if job_id in existing_jobs:
            st.session_state.scheduler.remove_job(job_id)
        
        # Prepare source URLs
        urls = [s['url'] for s in sources if s['type'] in ['Website', 'Other']]
        rss_urls = [s['url'] for s in sources if s['type'] == 'RSS Feed']
        youtube_urls = [s['url'] for s in sources if s['type'] in ['YouTube Video', 'YouTube Channel']]
        twitter_urls = [s['url'] for s in sources if s['type'] in ['Twitter Profile', 'Twitter Hashtag']]
        
        # Get writing style from style profile
        if style_profile:
            if style_profile.get('style_type') == 'predefined':
                # For predefined styles, map the tone to writing style
                tone = style_profile.get('tone', 'professional')
                if tone == 'formal':
                    writing_style = 'professional'
                elif tone == 'casual':
                    writing_style = 'casual'
                elif tone == 'technical':
                    writing_style = 'technical'
                else:
                    writing_style = 'professional'  # Default fallback
            else:
                # For trained styles, use the dominant tone
                writing_style = style_profile.get('dominant_tone', 'professional')
                # Map trained style tones to writing styles
                if writing_style in ['formal', 'professional', 'serious']:
                    writing_style = 'professional'
                elif writing_style in ['casual', 'friendly']:
                    writing_style = 'casual'
                elif writing_style in ['technical']:
                    writing_style = 'technical'
                else:
                    writing_style = 'professional'  # Default fallback
        else:
            writing_style = 'professional'  # Default style
        
        # Add new scheduled job
        st.session_state.scheduler.add_job(
            generate_and_send_newsletter,
            'cron',
            hour=delivery_time.hour,
            minute=delivery_time.minute,
            id=job_id,
            args=[
                os.getenv('GROQ_API_KEY'),
                os.getenv('RESEND_API_KEY'),
                os.getenv('FROM_EMAIL', 'noreply@yourdomain.com'),
                email,
                urls,
                rss_urls,
                f"Daily Newsletter - {datetime.now().strftime('%B %d, %Y')}",
                youtube_urls,
                twitter_urls,
                writing_style
            ],
            replace_existing=True
        )
        
        
        # Track job info
        job_info = {
            'user_id': user_id,
            'email': email,
            'delivery_time': delivery_time.strftime('%H:%M'),
            'sources_count': len(sources),
            'created_at': datetime.now().isoformat()
        }
        
        # Update scheduled jobs list
        st.session_state.scheduled_jobs = [job for job in st.session_state.scheduled_jobs if job['user_id'] != user_id]
        st.session_state.scheduled_jobs.append(job_info)
        
        print(f"[{datetime.now()}] Created scheduled job for {email} at {delivery_time.strftime('%H:%M')}")
        return True
        
    except Exception as e:
        print(f"[{datetime.now()}] ERROR creating scheduled job: {e}")
        return False

def remove_scheduled_job(user_id):
    """Remove scheduled job for a user"""
    try:
        job_id = f"newsletter_{user_id}"
        existing_jobs = [job.id for job in st.session_state.scheduler.get_jobs()]
        if job_id in existing_jobs:
            st.session_state.scheduler.remove_job(job_id)
        
        
        # Remove from tracked jobs
        st.session_state.scheduled_jobs = [job for job in st.session_state.scheduled_jobs if job['user_id'] != user_id]
        
        print(f"[{datetime.now()}] Removed scheduled job for user {user_id}")
        return True
        
    except Exception as e:
        print(f"[{datetime.now()}] ERROR removing scheduled job: {e}")
        return False

def show_login_page():
    """Display modern login/signup page with hero section"""
    
    # Hero Section
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title animate-float">📰 CreatorPulse</div>
        <div class="hero-subtitle">
            Your AI-powered content co-pilot for Independent Creators. 
            Transform any source into stunning newsletters in seconds.
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Feature Cards Section
    st.markdown('<h2 style="text-align: center; color: white; margin-bottom: 8px;">Why Choose CreatorPulse?</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align: center; color: #94a3b8; margin-bottom: 40px;">Everything you need to create professional newsletters</p>', unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🌐</span>
            <div class="feature-title">Multi-Source Scraping</div>
            <div class="feature-desc">Aggregate content from websites, RSS feeds, YouTube, and Twitter automatically</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">🤖</span>
            <div class="feature-title">AI-Powered</div>
            <div class="feature-desc">Groq LLM summarizes and transforms content into engaging newsletters</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">✨</span>
            <div class="feature-title">Style Training</div>
            <div class="feature-desc">Train the AI on your unique writing voice for personalized content</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="feature-card">
            <span class="feature-icon">📧</span>
            <div class="feature-title">Auto-Delivery</div>
            <div class="feature-desc">Schedule automatic newsletter delivery to your subscribers</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Login/Signup Section with centered layout
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        st.markdown("""
        <div style="text-align: center; margin-bottom: 24px;">
            <h2 style="color: white; margin-bottom: 8px;">Get Started</h2>
            <p style="color: #94a3b8;">Join thousands of creators using CreatorPulse</p>
        </div>
        """, unsafe_allow_html=True)
        
        tab1, tab2 = st.tabs(["🔐 Login", "✨ Sign Up"])
        
        with tab1:
            with st.form("login_form", clear_on_submit=False):
                st.markdown('<p style="color: #94a3b8; margin-bottom: 16px;">Welcome back! Enter your credentials</p>', unsafe_allow_html=True)
                email = st.text_input("📧 Email", placeholder="your@email.com")
                password = st.text_input("🔒 Password", type="password", placeholder="Enter your password")
                
                col_btn1, col_btn2 = st.columns([2, 1])
                with col_btn1:
                    login_btn = st.form_submit_button("Login to Dashboard", type="primary", use_container_width=True)
                
                if login_btn:
                    if email and password:
                        result = auth_manager.login(email, password)
                        if result["success"]:
                            st.session_state.user = result["user"]
                            st.session_state.session_id = result["session_id"]
                            st.success("✅ Login successful! Redirecting...")
                            st.rerun()
                        else:
                            st.error(f"❌ {result['error']}")
                    else:
                        st.error("Please fill in all fields")
        
        with tab2:
            with st.form("signup_form", clear_on_submit=False):
                st.markdown('<p style="color: #94a3b8; margin-bottom: 16px;">Create your free account</p>', unsafe_allow_html=True)
                name = st.text_input("👤 Full Name", placeholder="John Doe")
                email = st.text_input("📧 Email", placeholder="your@email.com", key="signup_email")
                password = st.text_input("🔒 Password", type="password", placeholder="Min. 6 characters", key="signup_password")
                confirm_password = st.text_input("🔒 Confirm Password", type="password", placeholder="Confirm your password")
                
                signup_btn = st.form_submit_button("Create Free Account", type="primary", use_container_width=True)
                
                if signup_btn:
                    if name and email and password and confirm_password:
                        if password != confirm_password:
                            st.error("❌ Passwords do not match")
                        elif len(password) < 6:
                            st.error("❌ Password must be at least 6 characters")
                        else:
                            result = auth_manager.signup(email, password, name)
                            if result["success"]:
                                st.success("✅ Account created successfully! Please login.")
                                st.balloons()
                            else:
                                st.error(f"❌ {result['error']}")
                    else:
                        st.error("Please fill in all fields")
    
    # Footer
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("""
    <div style="text-align: center; padding: 40px 20px; border-top: 1px solid rgba(255,255,255,0.1);">
        <p style="color: #64748b; font-size: 0.9rem;">
            Built with ❤️ for Independent Creators | Powered by Groq AI
        </p>
    </div>
    """, unsafe_allow_html=True)

def show_main_app():
    """Display main application interface"""
    user = get_current_user()
    
    # Sidebar navigation with modern styling
    with st.sidebar:
        # User profile section
        st.markdown(f"""
        <div style="text-align: center; padding: 20px 0; border-bottom: 1px solid rgba(255,255,255,0.1); margin-bottom: 20px;">
            <div style="width: 60px; height: 60px; background: linear-gradient(135deg, #6366f1, #8b5cf6); border-radius: 50%; margin: 0 auto 12px; display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">
                {user['name'][0].upper()}
            </div>
            <div style="color: white; font-weight: 600; font-size: 1.1rem;">{user['name']}</div>
            <div style="color: #64748b; font-size: 0.85rem;">{user.get('email', '')}</div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        st.markdown('<p style="color: #64748b; font-size: 0.8rem; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 12px;">Navigation</p>', unsafe_allow_html=True)
        
        page = st.radio("Navigate", [
            "🏠 Dashboard",
            "📝 Style Training", 
            "🔗 Source Management",
            "📰 Generate Draft",
            "⚙️ Settings"
        ], label_visibility="collapsed")
        
        st.markdown("<br><br>", unsafe_allow_html=True)
        
        # Logout button
        if st.button("🚪 Logout", use_container_width=True, type="secondary"):
            if 'session_id' in st.session_state:
                auth_manager.logout(st.session_state.session_id)
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
    
    # Main content area
    if page == "🏠 Dashboard":
        show_dashboard(user)
    elif page == "📝 Style Training":
        show_style_training(user)
    elif page == "🔗 Source Management":
        show_source_management(user)
    elif page == "📰 Generate Draft":
        show_draft_generation(user)
    elif page == "⚙️ Settings":
        show_settings(user)

def show_dashboard(user):
    """Display modern user dashboard"""
    
    # Dashboard Header
    st.markdown(f"""
    <div style="margin-bottom: 32px;">
        <h1 style="color: white; font-size: 2.5rem; font-weight: 700; margin-bottom: 8px;">
            Welcome back, <span class="gradient-text">{user['name'].split()[0]}</span>! 👋
        </h1>
        <p style="color: #94a3b8; font-size: 1.1rem;">
            Here's what's happening with your newsletters today
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if user has auto-delivery enabled
    user_job = next((job for job in st.session_state.scheduled_jobs if job['user_id'] == user['user_id']), None)
    
    # Get user stats
    try:
        sources = local_storage.get_user_sources(user['user_id'])
        sources_count = len(sources) if sources else 0
    except:
        sources_count = 0
    
    has_style = user.get('style_profile') is not None
    
    # Modern Stat Cards
    st.markdown("""
    <div class="stats-grid">
        <div class="stat-card">
            <div class="stat-value">{}</div>
            <div class="stat-label">📧 Auto-Delivery</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{}</div>
            <div class="stat-label">🔗 Content Sources</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">{}</div>
            <div class="stat-label">✨ Writing Style</div>
        </div>
        <div class="stat-card">
            <div class="stat-value">∞</div>
            <div class="stat-label">📰 Newsletters</div>
        </div>
    </div>
    """.format(
        "ON" if user_job else "OFF",
        sources_count,
        "Trained" if has_style else "Default"
    ), unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Status Alert
    if user_job:
        st.markdown(f"""
        <div style="background: linear-gradient(135deg, rgba(16, 185, 129, 0.15), rgba(6, 78, 59, 0.2)); border: 1px solid rgba(16, 185, 129, 0.3); border-radius: 16px; padding: 20px; margin-bottom: 24px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 1.5rem;">✅</span>
                <div>
                    <div style="color: #10b981; font-weight: 600; font-size: 1.1rem;">Auto-Delivery Active</div>
                    <div style="color: #94a3b8;">Next newsletter at <strong style="color: white;">{user_job['delivery_time']}</strong> to <strong style="color: white;">{user_job['email']}</strong></div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1)); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 16px; padding: 20px; margin-bottom: 24px;">
            <div style="display: flex; align-items: center; gap: 12px;">
                <span style="font-size: 1.5rem;">💡</span>
                <div>
                    <div style="color: #818cf8; font-weight: 600; font-size: 1.1rem;">Set Up Auto-Delivery</div>
                    <div style="color: #94a3b8;">Go to <strong style="color: white;">Settings</strong> to enable automatic newsletter delivery</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Quick Actions
    st.markdown('<h3 style="color: white; margin-bottom: 16px;">⚡ Quick Actions</h3>', unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card" style="padding: 24px;">
            <span style="font-size: 2rem;">📰</span>
            <div style="color: white; font-weight: 600; margin: 12px 0 8px;">Generate Newsletter</div>
            <div style="color: #94a3b8; font-size: 0.9rem;">Create a new draft from your sources</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="feature-card" style="padding: 24px;">
            <span style="font-size: 2rem;">🔗</span>
            <div style="color: white; font-weight: 600; margin: 12px 0 8px;">Manage Sources</div>
            <div style="color: #94a3b8; font-size: 0.9rem;">Add websites, RSS, YouTube channels</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="feature-card" style="padding: 24px;">
            <span style="font-size: 2rem;">✨</span>
            <div style="color: white; font-weight: 600; margin: 12px 0 8px;">Train Your Style</div>
            <div style="color: #94a3b8; font-size: 0.9rem;">Upload newsletters to train AI on your voice</div>
        </div>
        """, unsafe_allow_html=True)

def load_user_data_fallback(user_id):
    """Load user data from local file as fallback"""
    import json
    import os
    
    user_file = f"users/{user_id}.json"
    if os.path.exists(user_file):
        try:
            with open(user_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading user data from file: {e}")
    return None

def show_style_training(user):
    """Display style training interface"""
    
    # Modern page header
    st.markdown("""
    <div style="margin-bottom: 32px;">
        <h1 style="color: white; font-size: 2.5rem; font-weight: 700; margin-bottom: 8px;">
            <span class="gradient-text">📝 Style Training</span>
        </h1>
        <p style="color: #94a3b8; font-size: 1.1rem;">
            Upload your past newsletters to train the AI on your unique voice
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Try to load user data from local file if database fails
    if not user or not user.get('style_profile'):
        fallback_user = load_user_data_fallback(user.get('user_id', ''))
        if fallback_user and fallback_user.get('style_profile'):
            user = fallback_user
            st.info("📁 Loaded style profile from local storage")
    
    # Check if user already has style profile (either predefined or trained)
    has_style_profile = ('style_profile' in user and 
                        user['style_profile'] is not None and 
                        isinstance(user['style_profile'], dict) and
                        user['style_profile'].get('style_type') is not None)
    
    if has_style_profile:
        newsletter_count = user['style_profile'].get('newsletter_count', 0)
        style_type = user['style_profile'].get('style_type', 'trained')
        style_name = user['style_profile'].get('style_name', 'Custom Style')
        
        if style_type == 'predefined':
            st.success(f"✅ {style_name} style selected")
        else:
            st.success(f"✅ Style profile trained with {newsletter_count} newsletters")
        
        # Show style profile details
        with st.expander("View Style Profile Details"):
            st.json(user['style_profile'])
        
        # Action buttons
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Retrain Style Profile", use_container_width=True):
                st.session_state.retrain_style = True
                st.rerun()
        with col2:
            if st.button("Train Custom Style", use_container_width=True, type="secondary"):
                st.session_state.train_custom_style = True
                st.rerun()
        with col3:
            if st.button("🗑️ Delete Style Profile", use_container_width=True, type="secondary"):
                try:
                    # Delete the style profile
                    auth_manager.update_user_data(user['user_id'], {
                        'style_profile': None
                    })
                    # Update session state immediately
                    st.session_state.user['style_profile'] = None
                    st.success("✅ Style profile deleted successfully!")
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"Error deleting style profile: {str(e)}")
    
    # Show predefined writing styles for users without training data
    if not has_style_profile:
        st.subheader("📝 Predefined Writing Styles")
        st.caption("Choose from our professionally crafted writing styles if you don't have training data")
        
        # Define the 3 predefined styles
        predefined_styles = {
        "professional": {
            "name": "Professional Newsletter",
            "description": "Formal, business-focused style perfect for corporate communications",
            "characteristics": ["Formal tone", "Data-driven", "Structured", "Objective", "Clear and concise"],
            "icon": "💼"
        },
        "casual": {
            "name": "Casual & Engaging", 
            "description": "Friendly, conversational style great for community newsletters",
            "characteristics": ["Conversational", "Personal", "Engaging", "Approachable", "Community-focused"],
            "icon": "😊"
        },
        "technical": {
            "name": "Technical Deep Dive",
            "description": "Detailed, technical style ideal for developers and researchers",
            "characteristics": ["Highly detailed", "Technical language", "Code examples", "Data insights", "Precise"],
            "icon": "🔬"
            }
        }
        
        # Display the 3 styles in columns
        col1, col2, col3 = st.columns(3)
        
        with col1:
            with st.container():
                st.markdown(f"### {predefined_styles['professional']['icon']} {predefined_styles['professional']['name']}")
                st.write(predefined_styles['professional']['description'])
                st.caption("**Characteristics:**")
                for char in predefined_styles['professional']['characteristics']:
                    st.caption(f"• {char}")
                if st.button("Select Professional", key="select_professional", use_container_width=True):
                    # Create a predefined style profile
                    style_profile = {
                        'newsletter_count': 0,
                        'style_type': 'predefined',
                        'style_name': 'Professional Newsletter',
                        'characteristics': predefined_styles['professional']['characteristics'],
                        'tone': 'formal',
                        'formality': 'high',
                        'persona': 'professional',
                        'created_at': datetime.now().isoformat()
                    }
                    auth_manager.update_user_data(user['user_id'], {
                        'style_profile': style_profile
                    })
                    # Update session state immediately
                    st.session_state.user['style_profile'] = style_profile
                    # Clear any training session state
                    if 'train_custom_style' in st.session_state:
                        del st.session_state.train_custom_style
                    if 'retrain_style' in st.session_state:
                        del st.session_state.retrain_style
                    st.success("✅ Professional style selected!")
                    st.rerun()
        
        with col2:
            with st.container():
                st.markdown(f"### {predefined_styles['casual']['icon']} {predefined_styles['casual']['name']}")
                st.write(predefined_styles['casual']['description'])
                st.caption("**Characteristics:**")
                for char in predefined_styles['casual']['characteristics']:
                    st.caption(f"• {char}")
                if st.button("Select Casual", key="select_casual", use_container_width=True):
                    # Create a predefined style profile
                    style_profile = {
                        'newsletter_count': 0,
                        'style_type': 'predefined',
                        'style_name': 'Casual & Engaging',
                        'characteristics': predefined_styles['casual']['characteristics'],
                        'tone': 'casual',
                        'formality': 'low',
                        'persona': 'conversational',
                        'created_at': datetime.now().isoformat()
                    }
                    auth_manager.update_user_data(user['user_id'], {
                        'style_profile': style_profile
                    })
                    # Update session state immediately
                    st.session_state.user['style_profile'] = style_profile
                    # Clear any training session state
                    if 'train_custom_style' in st.session_state:
                        del st.session_state.train_custom_style
                    if 'retrain_style' in st.session_state:
                        del st.session_state.retrain_style
                    st.success("✅ Casual style selected!")
                    st.rerun()
        
        with col3:
            with st.container():
                st.markdown(f"### {predefined_styles['technical']['icon']} {predefined_styles['technical']['name']}")
                st.write(predefined_styles['technical']['description'])
                st.caption("**Characteristics:**")
                for char in predefined_styles['technical']['characteristics']:
                    st.caption(f"• {char}")
                if st.button("Select Technical", key="select_technical", use_container_width=True):
                    # Create a predefined style profile
                    style_profile = {
                        'newsletter_count': 0,
                        'style_type': 'predefined',
                        'style_name': 'Technical Deep Dive',
                        'characteristics': predefined_styles['technical']['characteristics'],
                        'tone': 'technical',
                        'formality': 'high',
                        'persona': 'expert',
                        'created_at': datetime.now().isoformat()
                    }
                    auth_manager.update_user_data(user['user_id'], {
                        'style_profile': style_profile
                    })
                    # Update session state immediately
                    st.session_state.user['style_profile'] = style_profile
                    # Clear any training session state
                    if 'train_custom_style' in st.session_state:
                        del st.session_state.train_custom_style
                    if 'retrain_style' in st.session_state:
                        del st.session_state.retrain_style
                    st.success("✅ Technical style selected!")
                    st.rerun()
        
        st.divider()
    
    # Show options for users without any style profile
    if not has_style_profile and 'train_custom_style' not in st.session_state:
        st.subheader("🎯 Choose Your Writing Style")
        st.caption("Select a predefined style or train a custom one with your own content")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📝 Use Predefined Style", use_container_width=True, type="primary"):
                st.info("👆 Scroll up to select from Professional, Casual, or Technical styles")
        with col2:
            if st.button("🎓 Train Custom Style", use_container_width=True, type="secondary"):
                st.session_state.train_custom_style = True
                st.rerun()
        
        st.divider()
    
    # Show upload interface only when user wants to train custom style
    if 'retrain_style' in st.session_state or 'train_custom_style' in st.session_state:
        # Back button
        if st.button("← Back to Style Selection", type="secondary"):
            if 'retrain_style' in st.session_state:
                del st.session_state.retrain_style
            if 'train_custom_style' in st.session_state:
                del st.session_state.train_custom_style
            # Use session state to trigger UI update without full rerun
            st.session_state.style_back_clicked = True
        
        st.subheader("Upload Past Newsletters")
        
        # Initialize session state for uploaded newsletters
        if 'uploaded_newsletters' not in st.session_state:
            st.session_state.uploaded_newsletters = []
        
        # Load existing newsletters from database/local storage
        def load_persisted_newsletters():
            try:
                # Try to get from database first
                user_data = auth_manager.get_user_data(user['user_id'])
                if user_data and 'uploaded_newsletters' in user_data:
                    return user_data['uploaded_newsletters']
            except Exception as e:
                print(f"Error loading newsletters from database: {e}")
            
            # Fallback to local file
            try:
                import json
                import os
                user_file = f"users/{user['user_id']}.json"
                if os.path.exists(user_file):
                    with open(user_file, 'r') as f:
                        user_data = json.load(f)
                        return user_data.get('uploaded_newsletters', [])
            except Exception as e:
                print(f"Error loading newsletters from local file: {e}")
            
            return []
        
        # Load persisted newsletters if session state is empty
        if not st.session_state.uploaded_newsletters:
            persisted_newsletters = load_persisted_newsletters()
            st.session_state.uploaded_newsletters = persisted_newsletters
        
        # Function to save newsletters to persistent storage
        def save_newsletters_to_storage(newsletters):
            try:
                # Try to save to database first
                # Deduplicate by title before saving
                unique = {}
                for nl in newsletters:
                    unique[nl.get('title', '')] = nl
                deduped = list(unique.values())

                auth_manager.update_user_data(user['user_id'], {
                    'uploaded_newsletters': deduped
                })
                print(f"Saved {len(deduped)} newsletters to database")
            except Exception as e:
                print(f"Database save failed: {e}")
                # Fallback to local file
                try:
                    import json
                    import os
                    os.makedirs('users', exist_ok=True)
                    user_file = f"users/{user['user_id']}.json"
                    
                    # Load existing user data
                    if os.path.exists(user_file):
                        with open(user_file, 'r') as f:
                            user_data = json.load(f)
                    else:
                        user_data = user.copy()
                    
                    # Update with newsletters (deduplicated by title)
                    unique = {}
                    for nl in newsletters:
                        unique[nl.get('title', '')] = nl
                    user_data['uploaded_newsletters'] = list(unique.values())
                    
                    # Save to file
                    with open(user_file, 'w') as f:
                        json.dump(user_data, f, indent=2)
                    
                    print(f"Saved {len(newsletters)} newsletters to local file")
                except Exception as file_error:
                    print(f"Local file save failed: {file_error}")
        
        # Debug: Show session state status
        st.write(f"🔍 Debug: Session state has {len(st.session_state.uploaded_newsletters)} newsletters")
        
        # File upload
        uploaded_files = st.file_uploader(
            "Upload your past newsletters (CSV, TXT, or JSON)",
            accept_multiple_files=True,
            type=['csv', 'txt', 'json'],
            key="file_uploader"
        )
        
        # Process uploaded files immediately
        if uploaded_files:
            for file in uploaded_files:
                # Only process if file (or its rows) haven't been added before
                already_processed = any(nl['title'].startswith(file.name) for nl in st.session_state.uploaded_newsletters)
                if already_processed:
                    continue

                content = file.read().decode('utf-8')

                # Check if it's a CSV file
                if file.name.lower().endswith('.csv'):
                    try:
                        import pandas as pd
                        import io

                        # Read CSV content
                        df = pd.read_csv(io.StringIO(content))

                        # Collect new newsletters for this file
                        new_newsletters = []

                        # Process each row as a separate newsletter
                        for index, row in df.iterrows():
                            # Try to find content in common column names
                            content_text = ""
                            for col in df.columns:
                                if any(keyword in col.lower() for keyword in ['content', 'text', 'body', 'newsletter', 'article']):
                                    content_text = str(row[col])
                                    break

                            # If no content column found, use all text columns
                            if not content_text:
                                content_text = " ".join([str(row[col]) for col in df.columns if pd.notna(row[col])])

                            if content_text and content_text.strip():
                                newsletter_data = {
                                    'title': f'{file.name} - Row {index + 1}',
                                    'content': content_text.strip(),
                                    'source': 'csv_upload'
                                }
                                new_newsletters.append(newsletter_data)

                        if new_newsletters:
                            st.session_state.uploaded_newsletters.extend(new_newsletters)
                            # Save once per file
                            save_newsletters_to_storage(st.session_state.uploaded_newsletters)

                    except Exception as e:
                        st.warning(f"Could not parse CSV file {file.name}: {str(e)}")
                        # Fallback to treating entire file as one newsletter
                        newsletter_data = {
                            'title': file.name,
                            'content': content,
                            'source': 'upload'
                        }
                        st.session_state.uploaded_newsletters.append(newsletter_data)
                        # Save once
                        save_newsletters_to_storage(st.session_state.uploaded_newsletters)
                else:
                    # For non-CSV files, treat as single newsletter
                    newsletter_data = {
                        'title': file.name,
                        'content': content,
                        'source': 'upload'
                    }
                    st.session_state.uploaded_newsletters.append(newsletter_data)
                    # Save once
                    save_newsletters_to_storage(st.session_state.uploaded_newsletters)
        
        # Display uploaded newsletters with delete option
        if st.session_state.uploaded_newsletters:
            st.subheader(f"📄 Uploaded Newsletters ({len(st.session_state.uploaded_newsletters)})")
            
            for i, newsletter in enumerate(st.session_state.uploaded_newsletters):
                col1, col2, col3 = st.columns([3, 2, 1])
                with col1:
                    st.write(f"**{newsletter['title']}**")
                with col2:
                    st.caption(f"{len(newsletter['content'])} characters • {newsletter['source']}")
                with col3:
                    if st.button("🗑️", key=f"delete_nl_{i}", help="Delete this newsletter"):
                        st.session_state.uploaded_newsletters.pop(i)
                        # Save updated list to persistent storage
                        save_newsletters_to_storage(st.session_state.uploaded_newsletters)
                        # Use session state to trigger UI update without full rerun
                        st.session_state.newsletter_deleted = True
            
            # Clear all button
            if st.button("🗑️ Clear All", type="secondary"):
                st.session_state.uploaded_newsletters = []
                # Save empty list to persistent storage
                save_newsletters_to_storage(st.session_state.uploaded_newsletters)
                # Use session state to trigger UI update without full rerun
                st.session_state.newsletters_cleared = True
        
        # Manual input
        st.subheader("Or Paste Newsletter Content")
        manual_input = st.text_area(
            "Paste newsletter content here (one per line, separate with '---')",
            height=200,
            placeholder="Newsletter 1 content\n---\nNewsletter 2 content\n---\n...",
            key="manual_input"
        )
        
        if st.button("Analyze Style", type="primary"):
            # Start with uploaded newsletters from session state
            newsletters = st.session_state.uploaded_newsletters.copy()
            
            
            # Process manual input
            if manual_input:
                manual_newsletters = manual_input.split('---')
                for i, content in enumerate(manual_newsletters):
                    if content.strip():
                        newsletter_data = {
                            'title': f'Manual Newsletter {i+1}',
                            'content': content.strip(),
                            'source': 'manual'
                        }
                        newsletters.append(newsletter_data)
                        # Add to session state and save to persistent storage
                        st.session_state.uploaded_newsletters.append(newsletter_data)
                        save_newsletters_to_storage(st.session_state.uploaded_newsletters)
            
            # Show what we found
            st.write(f"📊 Found {len(newsletters)} newsletters to analyze:")
            for i, newsletter in enumerate(newsletters):
                st.write(f"{i+1}. {newsletter['title']} ({newsletter['source']}) - {len(newsletter['content'])} characters")
            
            if len(newsletters) < 5:
                st.error("Please upload at least 5 newsletters for accurate style analysis")
            else:
                with st.spinner("Analyzing your writing style..."):
                    try:
                        style_profile = style_analyzer.create_style_profile(newsletters)
                        
                        if 'error' in style_profile:
                            st.error(f"❌ Analysis Error: {style_profile['error']}")
                        else:
                            # Update user's style profile with fallback
                            try:
                                auth_manager.update_user_data(user['user_id'], {
                                    'style_profile': style_profile
                                })
                                st.success("✅ Style profile saved to database!")
                            except Exception as db_error:
                                st.warning(f"⚠️ Database save failed: {str(db_error)}")
                                st.info("💾 Saving to local storage as fallback...")
                                
                                # Fallback: Save to local JSON file
                                import json
                                import os
                                
                                # Create users directory if it doesn't exist
                                os.makedirs('users', exist_ok=True)
                                
                                # Load existing user data
                                user_file = f"users/{user['user_id']}.json"
                                if os.path.exists(user_file):
                                    with open(user_file, 'r') as f:
                                        user_data = json.load(f)
                                else:
                                    user_data = user.copy()
                                
                                # Update style profile
                                user_data['style_profile'] = style_profile
                                
                                # Save to file
                                with open(user_file, 'w') as f:
                                    json.dump(user_data, f, indent=2)
                                
                                st.success("✅ Style profile saved locally!")
                            
                            st.success("✅ Style profile created successfully!")
                            st.json(style_profile)
                            
                            # Clear session state
                            if 'retrain_style' in st.session_state:
                                del st.session_state.retrain_style
                            if 'uploaded_newsletters' in st.session_state:
                                st.session_state.uploaded_newsletters = []
                            
                            st.info("🔄 Refreshing page to show updated profile...")
                            st.rerun()
                    except Exception as e:
                        st.error(f"❌ Unexpected Error: {str(e)}")
                        st.write("Please check the console for more details.")

def show_source_management(user):
    """Display modern source management interface"""
    
    # Page Header
    st.markdown("""
    <div style="margin-bottom: 32px;">
        <h1 style="color: white; font-size: 2.5rem; font-weight: 700; margin-bottom: 8px;">
            <span class="gradient-text">🔗 Source Management</span>
        </h1>
        <p style="color: #94a3b8; font-size: 1.1rem;">
            Manage your content sources and categorize them by niche
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Add new source - styled card
    st.markdown("""
    <div style="background: linear-gradient(135deg, rgba(99, 102, 241, 0.15), rgba(139, 92, 246, 0.1)); border: 1px solid rgba(99, 102, 241, 0.3); border-radius: 16px; padding: 20px; margin-bottom: 24px;">
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 16px;">
            <span style="font-size: 1.5rem;">➕</span>
            <div style="color: #818cf8; font-weight: 600; font-size: 1.1rem;">Add New Source</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.expander("✨ Click to Add a New Source", expanded=False):
        with st.form("add_source_form"):
            col1, col2 = st.columns(2)
            with col1:
                source_url = st.text_input("🔗 Source URL", placeholder="https://example.com/rss")
                niche = st.selectbox("📂 Content Niche", [
                    "AI", "ML", "Technology", "Gaming", "Science", "Business", 
                    "Politics", "Entertainment", "Sports", "Health", "Other"
                ])
            with col2:
                source_name = st.text_input("📝 Source Name", placeholder="Tech News")
                source_type = st.selectbox("🏷️ Source Type", ["RSS Feed", "Website", "YouTube Video", "YouTube Channel", "Twitter Profile", "Twitter Hashtag", "Other"])
            
            # Show help for YouTube sources
            if source_type in ["YouTube Video", "YouTube Channel"]:
                if source_type == "YouTube Video":
                    st.info("💡 **YouTube Video**: Use individual video URLs like `https://www.youtube.com/watch?v=VIDEO_ID`")
                else:
                    st.info("💡 **YouTube Channel**: Use channel URLs like `https://www.youtube.com/@ChannelName`")
            
            # Show help for Twitter sources
            elif source_type in ["Twitter Profile", "Twitter Hashtag"]:
                if source_type == "Twitter Profile":
                    st.info("💡 **Twitter Profile**: Use Twitter profile URLs like `https://twitter.com/username` or just `@username`")
                else:
                    st.info("💡 **Twitter Hashtag**: Use hashtag like `#AI` or `#MachineLearning`")
            
            if st.form_submit_button("➕ Add Source", type="primary", use_container_width=True):
                if source_url and source_name:
                    try:
                        new_source = {
                            'url': source_url,
                            'name': source_name,
                            'niche': niche,
                            'type': source_type,
                            'added_at': datetime.now().isoformat()
                        }
                        
                        if new_source:
                            if 'sources' not in user:
                                user['sources'] = []
                            
                            user['sources'].append({
                                "url": source_url,
                                "name": source_name,
                                "niche": niche,
                                "type": source_type,
                                "added_at": datetime.now().isoformat()
                            })
                            auth_manager.update_user_data(user['user_id'], {'sources': user['sources']})
                            st.success("✅ Source added successfully!")
                            st.rerun()
                        else:
                            st.error("❌ Failed to add source to database")
                    except Exception as e:
                        st.error(f"❌ Error adding source: {str(e)}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Pre-configured sources header
    st.markdown("""
    <h2 style="color: white; margin-bottom: 8px;">📚 Pre-configured Sources</h2>
    <p style="color: #94a3b8; margin-bottom: 24px;">Click to add popular sources to your collection</p>
    """, unsafe_allow_html=True)
    
    # Define category colors for visual appeal
    category_colors = {
        "🤖 AI Sources": ("#6366f1", "#8b5cf6"),
        "🧠 ML Sources": ("#8b5cf6", "#a855f7"),
        "💻 Technology Sources": ("#0ea5e9", "#06b6d4"),
        "🐦 Twitter Sources": ("#1d9bf0", "#60a5fa"),
        "🎮 Gaming Sources": ("#10b981", "#34d399"),
        "🔬 Science Sources": ("#f59e0b", "#fbbf24"),
        "💼 Business Sources": ("#ef4444", "#f87171"),
        "🏛️ Politics Sources": ("#6b7280", "#9ca3af"),
        "🎬 Entertainment Sources": ("#ec4899", "#f472b6"),
        "⚽ Sports Sources": ("#22c55e", "#4ade80"),
        "🏥 Health Sources": ("#14b8a6", "#2dd4bf"),
        "📺 YouTube AI/ML Channels": ("#ff0000", "#ff4444"),
        "📺 YouTube Tech Channels": ("#ff0000", "#ff6666"),
    }
    
    # Define pre-configured sources
    predefined_sources = {
        "🤖 AI Sources": [
            {"name": "OpenAI Blog", "url": "https://openai.com/blog/", "niche": "AI", "type": "Website"},
            {"name": "Anthropic Blog", "url": "https://www.anthropic.com/news", "niche": "AI", "type": "Website"},
            {"name": "Google AI Blog", "url": "https://ai.googleblog.com/", "niche": "AI", "type": "Website"},
            {"name": "DeepMind Blog", "url": "https://deepmind.google/discover/blog/", "niche": "AI", "type": "Website"},
            {"name": "Hugging Face Blog", "url": "https://huggingface.co/blog", "niche": "AI", "type": "Website"}
        ],
        "🧠 ML Sources": [
            {"name": "Machine Learning Mastery", "url": "https://machinelearningmastery.com/", "niche": "ML", "type": "Website"},
            {"name": "Towards Data Science", "url": "https://towardsdatascience.com/", "niche": "ML", "type": "Website"},
            {"name": "Distill", "url": "https://distill.pub/", "niche": "ML", "type": "Website"},
            {"name": "Papers with Code", "url": "https://paperswithcode.com/", "niche": "ML", "type": "Website"},
            {"name": "Fast.ai Blog", "url": "https://www.fast.ai/", "niche": "ML", "type": "Website"}
        ],
        "💻 Technology Sources": [
            {"name": "TechCrunch", "url": "https://techcrunch.com/", "niche": "Technology", "type": "Website"},
            {"name": "The Verge", "url": "https://www.theverge.com/", "niche": "Technology", "type": "Website"},
            {"name": "Ars Technica", "url": "https://arstechnica.com/", "niche": "Technology", "type": "Website"},
            {"name": "Wired", "url": "https://www.wired.com/", "niche": "Technology", "type": "Website"},
            {"name": "Hacker News", "url": "https://news.ycombinator.com/", "niche": "Technology", "type": "Website"}
        ],
        "🐦 Twitter Sources": [
            {"name": "OpenAI", "url": "@OpenAI", "niche": "AI", "type": "Twitter Profile"},
            {"name": "Google AI", "url": "@GoogleAI", "niche": "AI", "type": "Twitter Profile"},
            {"name": "DeepMind", "url": "@DeepMind", "niche": "AI", "type": "Twitter Profile"},
            {"name": "AI Hashtag", "url": "#AI", "niche": "AI", "type": "Twitter Hashtag"},
            {"name": "Machine Learning Hashtag", "url": "#MachineLearning", "niche": "ML", "type": "Twitter Hashtag"}
        ],
        "🎮 Gaming Sources": [
            {"name": "IGN", "url": "https://www.ign.com/", "niche": "Gaming", "type": "Website"},
            {"name": "GameSpot", "url": "https://www.gamespot.com/", "niche": "Gaming", "type": "Website"},
            {"name": "Polygon", "url": "https://www.polygon.com/", "niche": "Gaming", "type": "Website"},
            {"name": "Kotaku", "url": "https://kotaku.com/", "niche": "Gaming", "type": "Website"},
            {"name": "PC Gamer", "url": "https://www.pcgamer.com/", "niche": "Gaming", "type": "Website"}
        ],
        "📺 YouTube Tech Channels": [
            {"name": "Marques Brownlee (MKBHD)", "url": "https://www.youtube.com/@mkbhd", "niche": "Technology", "type": "YouTube Channel"},
            {"name": "Linus Tech Tips", "url": "https://www.youtube.com/@LinusTechTips", "niche": "Technology", "type": "YouTube Channel"},
            {"name": "Fireship", "url": "https://www.youtube.com/@Fireship", "niche": "Technology", "type": "YouTube Channel"},
            {"name": "The Verge", "url": "https://www.youtube.com/@TheVerge", "niche": "Technology", "type": "YouTube Channel"}
        ]
    }
    
    # Display as colorful grid cards
    cols = st.columns(3)
    for idx, (category, sources) in enumerate(predefined_sources.items()):
        color1, color2 = category_colors.get(category, ("#6366f1", "#8b5cf6"))
        with cols[idx % 3]:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, {color1}22, {color2}11); border: 1px solid {color1}44; border-radius: 16px; padding: 20px; margin-bottom: 16px; min-height: 120px;">
                <div style="font-size: 1.2rem; font-weight: 600; color: white; margin-bottom: 8px;">{category}</div>
                <div style="color: #94a3b8; font-size: 0.9rem;">{len(sources)} sources available</div>
            </div>
            """, unsafe_allow_html=True)
            
            with st.expander(f"View & Add {category.split()[1]} Sources"):
                for i, source in enumerate(sources):
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"""
                        <div style="padding: 8px 0; border-bottom: 1px solid rgba(255,255,255,0.05);">
                            <div style="color: white; font-weight: 500;">{source['name']}</div>
                            <div style="color: #64748b; font-size: 0.85rem;">{source['niche']} • {source['type']}</div>
                        </div>
                        """, unsafe_allow_html=True)
                    with col2:
                        if st.button("➕ Add", key=f"add_{category}_{i}", use_container_width=True):
                            try:
                                existing_sources = user.get('sources', [])
                                existing_urls = [s['url'] for s in existing_sources]
                                
                                if source['url'] in existing_urls:
                                    st.warning("Already added!")
                                else:
                                    if 'sources' not in user:
                                        user['sources'] = []
                                    
                                    user['sources'].append({
                                        "url": source['url'],
                                        "name": source['name'],
                                        "niche": source['niche'],
                                        "type": source['type'],
                                        "added_at": datetime.now().isoformat()
                                    })
                                    auth_manager.update_user_data(user['user_id'], {'sources': user['sources']})
                                    st.success("✅ Added!")
                                    st.rerun()
                            except Exception as e:
                                st.error(f"Error: {str(e)}")
    
    # Display existing sources
    st.markdown("<br>", unsafe_allow_html=True)
    
    try:
        sources = user.get('sources', [])
        if sources:
            st.markdown(f"""
            <h2 style="color: white; margin-bottom: 8px;">✅ Your Sources ({len(sources)})</h2>
            <p style="color: #94a3b8; margin-bottom: 24px;">Your saved content sources for newsletter generation</p>
            """, unsafe_allow_html=True)
            
            for i, source in enumerate(sources):
                # Create a styled card for each source
                st.markdown(f"""
                <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 16px; margin-bottom: 12px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <div style="color: white; font-weight: 600; font-size: 1rem;">{source['name']}</div>
                            <div style="color: #64748b; font-size: 0.85rem; margin-top: 4px;">{source['url'][:60]}...</div>
                        </div>
                        <div style="display: flex; gap: 8px; align-items: center;">
                            <span style="background: rgba(99, 102, 241, 0.2); color: #818cf8; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;">{source['niche']}</span>
                            <span style="background: rgba(16, 185, 129, 0.2); color: #10b981; padding: 4px 12px; border-radius: 20px; font-size: 0.8rem;">{source['type']}</span>
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Delete button in a column
                col1, col2, col3 = st.columns([8, 1, 1])
                with col3:
                    if st.button("🗑️", key=f"delete_{i}", help="Delete source"):
                        try:
                            if 'sources' in user:
                                user['sources'] = [s for s in user['sources'] if s['url'] != source['url']]
                                auth_manager.update_user_data(user['user_id'], {'sources': user['sources']})
                            st.success("✅ Source deleted!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"Error: {str(e)}")
        else:
            # No sources found
            if 'sources' in user and user['sources']:
                st.subheader("Your Sources")
                for i, source in enumerate(user['sources']):
                    col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                    
                    with col1:
                        st.write(f"**{source['name']}**")
                        st.caption(source['url'])
                    
                    with col2:
                        st.write(f"**Niche:** {source['niche']}")
                    
                    with col3:
                        st.write(f"**Type:** {source['type']}")
                    
                    with col4:
                        if st.button("🗑️", key=f"delete_local_{i}"):
                            user['sources'].pop(i)
                            auth_manager.update_user_data(user['user_id'], {'sources': user['sources']})
                            st.rerun()
            else:
                st.info("No sources added yet. Add your first source above!")
    except Exception as e:
        st.error(f"Error loading sources: {str(e)}")
        # Fallback to local sources
        if 'sources' in user and user['sources']:
            st.subheader("Your Sources (Local)")
            for i, source in enumerate(user['sources']):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{source['name']}**")
                    st.caption(source['url'])
                
                with col2:
                    st.write(f"**Niche:** {source['niche']}")
                
                with col3:
                    st.write(f"**Type:** {source['type']}")
                
                with col4:
                    if st.button("🗑️", key=f"delete_local_{i}"):
                        user['sources'].pop(i)
                        auth_manager.update_user_data(user['user_id'], {'sources': user['sources']})
                        st.rerun()
        else:
            st.info("No sources added yet. Add your first source above!")

def show_draft_generation(user):
    """Display draft generation interface"""
    
    # Modern page header
    st.markdown("""
    <div style="margin-bottom: 32px;">
        <h1 style="color: white; font-size: 2.5rem; font-weight: 700; margin-bottom: 8px;">
            <span class="gradient-text">📰 Generate Newsletter</span>
        </h1>
        <p style="color: #94a3b8; font-size: 1.1rem;">
            Create stunning newsletters from your sources with AI-powered summarization
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check prerequisites - Make style training optional
    has_style_profile = ('style_profile' in user and 
                        user['style_profile'] is not None and 
                        isinstance(user['style_profile'], dict) and
                        (user['style_profile'].get('newsletter_count', 0) > 0 or 
                         user['style_profile'].get('style_type') == 'predefined'))
    
    # Show style training as optional, not required
    if not has_style_profile:
        st.info("💡 **Optional**: You can train a custom writing style in the Style Training tab, or use the default professional style.")
        # Don't return - allow draft generation to continue
    
    # Show current style information
    if has_style_profile:
        style_type = user['style_profile'].get('style_type', 'trained')
        style_name = user['style_profile'].get('style_name', 'Custom Style')
        
        if style_type == 'predefined':
            st.success(f"✅ Using {style_name} style")
        else:
            newsletter_count = user['style_profile'].get('newsletter_count', 0)
            st.success(f"✅ Using custom style trained with {newsletter_count} newsletters")
        
        # Show style characteristics
        with st.expander("View Style Characteristics", expanded=False):
            characteristics = user['style_profile'].get('characteristics', [])
            if characteristics:
                for char in characteristics:
                    st.write(f"• {char}")
            else:
                st.write("No characteristics available")
    
    # Check for sources in local storage
    try:
        sources = user.get('sources', [])
        if not sources:
            st.warning("⚠️ Please add some sources first!")
            return
    except Exception as e:
        st.error(f"Error loading sources: {str(e)}")
        # Fallback to local sources
        if 'sources' not in user or not user['sources']:
            st.warning("⚠️ Please add some sources first!")
            return
        sources = user['sources']
    
    # Generation options
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Content Focus")
        focus_niche = st.selectbox(
            "Select niche focus",
            ["All"] + list(set(source['niche'] for source in sources))
        )
    
    with col2:
        st.subheader("Delivery Options")
        delivery_method = st.radio(
            "How would you like to receive the draft?",
            ["Email", "Preview Only"]
        )
    
    # Generate draft
    if st.button("🚀 Generate Draft", type="primary"):
        with st.spinner("Generating your personalized draft..."):
            # Filter sources by niche if selected
            sources_to_use = sources
            if focus_niche != "All":
                sources_to_use = [s for s in sources if s['niche'] == focus_niche]
            
            # Extract URLs by type
            urls = [s['url'] for s in sources_to_use if s['type'] in ['Website', 'Other']]
            rss_urls = [s['url'] for s in sources_to_use if s['type'] == 'RSS Feed']
            youtube_urls = [s['url'] for s in sources_to_use if s['type'] in ['YouTube Video', 'YouTube Channel']]
            twitter_urls = [s['url'] for s in sources_to_use if s['type'] in ['Twitter Profile', 'Twitter Hashtag']]
            
            # Show what sources we found
            st.write(f"**Found sources:**")
            st.write(f"- Websites: {len(urls)}")
            st.write(f"- RSS Feeds: {len(rss_urls)}")
            st.write(f"- YouTube: {len(youtube_urls)}")
            st.write(f"- Twitter: {len(twitter_urls)}")
            
            # Check if we have any valid sources after YouTube processing
            valid_sources_count = len(urls) + len(rss_urls) + len(youtube_with_transcripts) if 'youtube_with_transcripts' in locals() else len(urls) + len(rss_urls) + len(youtube_urls) + len(twitter_urls)
            
            if valid_sources_count == 0:
                st.error("No valid sources found for the selected niche")
                return
            
            # Process YouTube URLs separately using transcript extraction
            if youtube_urls:
                st.info(f"📺 Processing {len(youtube_urls)} YouTube video(s) for transcript extraction")
                
                # Check if any YouTube videos have transcripts available
                from youtube_processor import YouTubeTranscriptProcessor
                youtube_processor = YouTubeTranscriptProcessor()
                
                youtube_with_transcripts = []
                youtube_without_transcripts = []
                
                for url in youtube_urls:
                    # Check if it's a channel URL or individual video URL
                    if youtube_processor.is_youtube_channel(url):
                        # For channel URLs, add them to transcripts list (they'll be processed later)
                        youtube_with_transcripts.append(url)
                    else:
                        # For individual video URLs, test transcript availability
                        video_id = youtube_processor.extract_video_id(url)
                        if video_id:
                            # Actually try to get transcript to test if it works
                            transcript = youtube_processor.get_transcript(video_id)
                            if transcript:
                                youtube_with_transcripts.append(url)
                            else:
                                youtube_without_transcripts.append(url)
                
                if youtube_without_transcripts:
                    st.warning(f"⚠️ {len(youtube_without_transcripts)} YouTube video(s) can't be processed for transcript extraction")
                    for url in youtube_without_transcripts:
                        st.write(f"  • {url}")
                    st.info("💡 **Note**: Transcript extraction failed due to YouTube's IP blocking restrictions. The system will use video metadata and descriptions instead to create content.")
                
                if youtube_with_transcripts:
                    channel_count = sum(1 for url in youtube_with_transcripts if youtube_processor.is_youtube_channel(url))
                    video_count = len(youtube_with_transcripts) - channel_count
                    
                    if channel_count > 0 and video_count > 0:
                        st.success(f"✅ {channel_count} YouTube channel(s) and {video_count} video(s) ready for processing")
                    elif channel_count > 0:
                        st.success(f"✅ {channel_count} YouTube channel(s) ready for processing")
                    else:
                        st.success(f"✅ {video_count} YouTube video(s) have transcripts available")
            
            # Only add default RSS feeds if user has NO sources at all
            # Don't add defaults if user has configured YouTube, Twitter, or other sources
            if not rss_urls and not urls and not youtube_urls and not twitter_urls and focus_niche in ['AI', 'ML', 'All']:
                if focus_niche == 'AI':
                    default_rss_feeds = [
                        "https://feeds.feedburner.com/oreilly/radar",
                        "https://openai.com/blog/rss.xml",
                        "https://www.artificialintelligence-news.com/feed/"
                    ]
                    st.info("🤖 Added default AI RSS feeds to ensure content generation")
                elif focus_niche == 'ML':
                    default_rss_feeds = [
                        "https://machinelearningmastery.com/feed/",
                        "https://towardsdatascience.com/feed",
                        "https://distill.pub/rss.xml"
                    ]
                    st.info("🧠 Added default ML RSS feeds to ensure content generation")
                else:  # All
                    default_rss_feeds = [
                        "https://feeds.feedburner.com/oreilly/radar",
                        "https://machinelearningmastery.com/feed/",
                        "https://towardsdatascience.com/feed"
                    ]
                    st.info("🤖 Added default AI/ML RSS feeds to ensure content generation")
                
                rss_urls.extend(default_rss_feeds)
            
            # Generate style prompt (use default if no style profile)
            if has_style_profile:
                style_prompt = generate_style_prompt(user['style_profile'])
            else:
                # Use default professional style
                style_prompt = "Write in a professional, clear, and engaging tone suitable for a newsletter."
            
            # Create pipeline with style integration
            try:
                # Ensure YouTube Data API key is set
                youtube_api_key = os.getenv('YOUTUBE_DATA_API_KEY')
                if youtube_api_key:
                    os.environ['YOUTUBE_DATA_API_KEY'] = youtube_api_key
                
                pipeline = ContentPipeline(
                    groq_api_key=os.getenv('GROQ_API_KEY'),
                    resend_api_key=os.getenv('RESEND_API_KEY'),
                    from_email=os.getenv('FROM_EMAIL', 'noreply@yourdomain.com')
                )
                
                # Generate draft
                start_time = datetime.now()
                
                # Use only YouTube videos with available transcripts
                youtube_urls_to_process = youtube_with_transcripts if 'youtube_with_transcripts' in locals() else youtube_urls
                
                # Extract writing style from user's style profile (default to professional)
                if has_style_profile:
                    style_profile = user['style_profile']
                    print(f"DEBUG: Style profile found: {style_profile}")
                    
                    # Handle both predefined and trained styles
                    if style_profile.get('style_type') == 'predefined':
                        # For predefined styles, map the tone to writing style
                        tone = style_profile.get('tone', 'professional')
                        print(f"DEBUG: Predefined style tone: {tone}")
                        if tone == 'formal':
                            writing_style = 'professional'
                        elif tone == 'casual':
                            writing_style = 'casual'
                        elif tone == 'technical':
                            writing_style = 'technical'
                        else:
                            writing_style = 'professional'  # Default fallback
                    else:
                        # For trained styles, use the dominant tone
                        writing_style = style_profile.get('dominant_tone', 'professional')
                        print(f"DEBUG: Trained style dominant tone: {writing_style}")
                        # Map trained style tones to writing styles
                        if writing_style in ['formal', 'professional', 'serious']:
                            writing_style = 'professional'
                        elif writing_style in ['casual', 'friendly']:
                            writing_style = 'casual'
                        elif writing_style in ['technical']:
                            writing_style = 'technical'
                        else:
                            writing_style = 'professional'  # Default fallback
                else:
                    writing_style = 'professional'  # Default style
                    print("DEBUG: No style profile found, using default professional style")
                
                print(f"DEBUG: Final writing style selected: {writing_style}")
                
                results = pipeline.process_mixed_sources(
                    urls=urls,
                    rss_urls=rss_urls,
                    youtube_urls=youtube_urls_to_process,
                    twitter_urls=twitter_urls,
                    max_rss_items=5,
                    email_recipients=[user['delivery_settings']['email']] if delivery_method == "Email" else [],
                    digest_title=f"Your {focus_niche} Newsletter",
                    writing_style=writing_style
                )
                generation_time = (datetime.now() - start_time).total_seconds()
                
                if results["success"]:
                    draft_id = f"draft_{int(datetime.now().timestamp())}"
                    
                    st.success("✅ Draft generated successfully!")
                    
                    # Display draft
                    st.subheader("📰 Your Newsletter Draft")
                    st.markdown(results["digest_content"])
                    
                    # Review interface
                    st.subheader("📝 Review & Edit")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("✅ Accept Draft", type="primary"):
                            st.success("Draft accepted!")
                    
                    with col2:
                        if st.button("✏️ Edit Draft"):
                            st.session_state.editing_draft = True
                            st.session_state.draft_content = results["digest_content"]
                            st.session_state.draft_id = draft_id
                    
                    if 'editing_draft' in st.session_state:
                        st.text_area("Edit your draft:", 
                                   value=st.session_state.draft_content, 
                                   height=400, key="draft_editor")
                        
                        if st.button("💾 Save Changes"):
                            
                            st.success("Changes saved!")
                            del st.session_state.editing_draft
                            # Use session state to trigger UI update without full rerun
                            st.session_state.draft_saved = True
                
                else:
                    error_msg = results['error']
                    
                    # Provide specific guidance for YouTube-related errors
                    if "YouTube" in error_msg or "transcript" in error_msg.lower():
                        st.error(f"❌ Draft generation failed: {error_msg}")
                        
                        # Show helpful information for YouTube issues
                        with st.expander("🔧 YouTube Processing Help", expanded=True):
                            st.markdown("""
                            **Common YouTube Issues & Solutions:**
                            
                            1. **Missing YouTube Data API Key**
                               - Go to [Google Cloud Console](https://console.cloud.google.com/)
                               - Enable YouTube Data API v3
                               - Create an API key
                               - Add it to your environment variables
                            
                            2. **Transcript Extraction Failed**
                               - Some videos don't have transcripts available
                               - YouTube may block transcript access from certain IPs
                               - Try using individual video URLs instead of channels
                            
                            3. **Channel Processing Issues**
                               - Channel URLs require YouTube Data API key
                               - Individual video URLs work without API key
                            
                            **Quick Fix:** Try adding individual YouTube video URLs instead of channel URLs.
                            """)
                    else:
                        st.error(f"❌ Draft generation failed: {error_msg}")
                    
            except Exception as e:
                st.error(f"❌ Error generating draft: {str(e)}")


def show_settings(user):
    """Display settings interface"""
    
    # Modern page header
    st.markdown("""
    <div style="margin-bottom: 32px;">
        <h1 style="color: white; font-size: 2.5rem; font-weight: 700; margin-bottom: 8px;">
            <span class="gradient-text">⚙️ Settings</span>
        </h1>
        <p style="color: #94a3b8; font-size: 1.1rem;">
            Configure your newsletter delivery and preferences
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Delivery settings
    st.markdown('<h3 style="color: white; margin-bottom: 16px;">📧 Delivery Settings</h3>', unsafe_allow_html=True)
    with st.form("delivery_settings"):
        delivery_time = st.time_input("Daily delivery time", 
                                    value=datetime.strptime(user.get('delivery_settings', {}).get('time', '08:00'), '%H:%M').time())
        delivery_email = st.text_input("Delivery email", 
                                     value=user.get('delivery_settings', {}).get('email', user.get('email', '')))
        timezone = st.selectbox("Timezone", ["UTC", "EST", "PST", "CST", "MST"])
        
        # Auto-delivery toggle
        auto_delivery = st.checkbox("Enable automatic daily delivery", 
                                  value=user.get('delivery_settings', {}).get('auto_delivery', False),
                                  help="Automatically generate and send newsletter at the specified time")
        
        if st.form_submit_button("Save Settings"):
            # Update user settings
            auth_manager.update_user_data(user['user_id'], {
                'delivery_settings': {
                    'time': delivery_time.strftime('%H:%M'),
                    'email': delivery_email,
                    'timezone': timezone,
                    'auto_delivery': auto_delivery
                }
            })
            
            # Handle scheduled job creation/removal
            if auto_delivery:
                # Check if user has sources and style profile
                sources = user.get('sources', [])
                has_sources = sources and len(sources) > 0
                
                has_style = ('style_profile' in user and 
                            user['style_profile'] is not None and 
                            isinstance(user['style_profile'], dict) and
                            (user['style_profile'].get('newsletter_count', 0) > 0 or 
                             user['style_profile'].get('style_type') == 'predefined'))
                
                if not has_sources:
                    st.error("❌ Please add some content sources first before enabling auto-delivery!")
                elif not has_style:
                    st.error("❌ Please complete style training first before enabling auto-delivery!")
                else:
                    # Create scheduled job
                    success = create_scheduled_job(
                        user['user_id'],
                        delivery_time,
                        delivery_email,
                        sources if 'sources' in locals() else user.get('sources', []),
                        user.get('style_profile')
                    )
                    
                    if success:
                        st.success("✅ Settings saved! Automatic delivery enabled.")
                        st.info(f"📧 Newsletter will be sent daily at {delivery_time.strftime('%H:%M')} to {delivery_email}")
                    else:
                        st.error("❌ Failed to create scheduled job. Please try again.")
            else:
                # Remove scheduled job if auto-delivery is disabled
                remove_scheduled_job(user['user_id'])
                st.success("✅ Settings saved! Automatic delivery disabled.")
            
            # Use session state to trigger UI update without full rerun
            st.session_state.settings_saved = True
    
    # Show current scheduled job status
    st.subheader("📅 Delivery Status")
    
    # Check if user has an active scheduled job
    user_job = next((job for job in st.session_state.scheduled_jobs if job['user_id'] == user['user_id']), None)
    
    if user_job:
        st.success(f"✅ **Automatic delivery is ACTIVE**")
        st.write(f"📧 **Email:** {user_job['email']}")
        st.write(f"⏰ **Time:** {user_job['delivery_time']}")
        st.write(f"📚 **Sources:** {user_job['sources_count']} configured")
        st.write(f"📅 **Created:** {datetime.fromisoformat(user_job['created_at']).strftime('%B %d, %Y at %I:%M %p')}")
        
        if st.button("🛑 Disable Auto-Delivery", type="secondary"):
            remove_scheduled_job(user['user_id'])
            # Update user settings
            auth_manager.update_user_data(user['user_id'], {
                'delivery_settings': {
                    **user.get('delivery_settings', {}),
                    'auto_delivery': False
                }
            })
            st.success("✅ Automatic delivery disabled!")
            # Use session state to trigger UI update without full rerun
            st.session_state.auto_delivery_disabled = True
    else:
        st.info("ℹ️ **Automatic delivery is INACTIVE**")
        st.write("Enable auto-delivery above to receive daily newsletters automatically.")
    
    # Show all active jobs (for debugging)
    if st.session_state.scheduled_jobs:
        with st.expander("🔧 Active Scheduled Jobs (Debug)", expanded=False):
            for job in st.session_state.scheduled_jobs:
                st.write(f"User: {job['user_id']} | Email: {job['email']} | Time: {job['delivery_time']}")
    

# --- MAIN APP LOGIC ---
if 'user' not in st.session_state:
    show_login_page()
else:
    show_main_app()
