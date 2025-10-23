import streamlit as st
import os
<<<<<<< HEAD
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
=======
from utils.content_pipeline import ContentPipeline
from dotenv import load_dotenv
from datetime import datetime # ADDED: For handling dates and times
from apscheduler.schedulers.background import BackgroundScheduler # ADDED: For scheduling jobs

# Load environment variables
load_dotenv()
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15
import streamlit_shadcn_ui as ui
from config.sources import NEWS_SOURCES

st.set_page_config(page_title="CreatorPulse", page_icon="📰", layout="wide")

<<<<<<< HEAD
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
    """Display login/signup page"""
    st.title("📰 CreatorPulse")
    st.caption("Your AI-powered content co-pilot for Independent Creators")
    
    tab1, tab2 = st.tabs(["Login", "Sign Up"])
    
    with tab1:
        st.subheader("Login to Your Account")
        with st.form("login_form"):
            email = st.text_input("Email", type="default")
            password = st.text_input("Password", type="password")
            login_btn = st.form_submit_button("Login", type="primary")
            
            if login_btn:
                if email and password:
                    result = auth_manager.login(email, password)
                    if result["success"]:
                        st.session_state.user = result["user"]
                        st.session_state.session_id = result["session_id"]
                        st.success("Login successful!")
                        st.rerun()
                    else:
                        st.error(result["error"])
                else:
                    st.error("Please fill in all fields")
    
    with tab2:
        st.subheader("Create New Account")
        with st.form("signup_form"):
            name = st.text_input("Full Name")
            email = st.text_input("Email", type="default")
            password = st.text_input("Password", type="password")
            confirm_password = st.text_input("Confirm Password", type="password")
            signup_btn = st.form_submit_button("Sign Up", type="primary")
            
            if signup_btn:
                if name and email and password and confirm_password:
                    if password != confirm_password:
                        st.error("Passwords do not match")
                    elif len(password) < 6:
                        st.error("Password must be at least 6 characters")
                    else:
                        result = auth_manager.signup(email, password, name)
                        if result["success"]:
                            st.success("Account created successfully! Please login.")
                        else:
                            st.error(result["error"])
                else:
                    st.error("Please fill in all fields")

def show_main_app():
    """Display main application interface"""
    user = get_current_user()
    
    
    # Sidebar navigation
    with st.sidebar:
        st.header(f"Welcome, {user['name']}!")
        
        # Navigation
        page = st.radio("Navigate", [
            "🏠 Dashboard",
            "📝 Style Training", 
            "🔗 Source Management",
            "📰 Generate Draft",
            "⚙️ Settings"
        ])
        
        # Logout button
        if st.button("Logout"):
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
    """Display user dashboard"""
    st.title("📊 Dashboard")
    
    
    # Check if user has auto-delivery enabled
    user_job = next((job for job in st.session_state.scheduled_jobs if job['user_id'] == user['user_id']), None)
    
    # Status Cards
    col1, col2 = st.columns(2)
    
    with col1:
        if user_job:
            st.metric(
                "Auto-Delivery",
                "✅ Active",
                f"Next: {user_job['delivery_time']}"
            )
        else:
            st.metric(
                "Auto-Delivery",
                "❌ Inactive",
                "Enable in Settings"
            )
    
    with col2:
        st.metric(
            "Status",
            "Ready",
            "Generate your first draft"
        )
    
    # Auto-delivery status
    if user_job:
        st.success(f"📧 **Automatic delivery is ACTIVE** - Next newsletter will be sent at {user_job['delivery_time']} to {user_job['email']}")
    else:
        st.info("ℹ️ **Automatic delivery is INACTIVE** - Go to Settings to enable daily newsletter delivery")
    
    # Getting Started
    st.subheader("Getting Started")
    st.info("📝 **Ready to create content?** Go to 'Generate Draft' to create your first newsletter draft!")

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
    st.title("📝 Style Training")
    st.caption("Upload your past newsletters to train the AI on your unique voice")
    
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
                # Use session state to trigger UI update without full rerun
                st.session_state.style_retrain_triggered = True
        with col2:
            if st.button("Train Custom Style", use_container_width=True, type="secondary"):
                st.session_state.train_custom_style = True
                # Use session state to trigger UI update without full rerun
                st.session_state.style_train_triggered = True
        with col3:
            if st.button("🗑️ Delete Style Profile", use_container_width=True, type="secondary"):
                try:
                    # Delete the style profile
                    auth_manager.update_user_data(user['user_id'], {
                        'style_profile': None
                    })
                    st.success("✅ Style profile deleted successfully!")
                    st.balloons()
                    # Use session state to trigger UI update without full rerun
                    st.session_state.style_deleted = True
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
                    # Clear any training session state
                    if 'train_custom_style' in st.session_state:
                        del st.session_state.train_custom_style
                    if 'retrain_style' in st.session_state:
                        del st.session_state.retrain_style
                    st.success("✅ Professional style selected!")
                    # Use session state to trigger UI update without full rerun
                    st.session_state.style_selected = True
        
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
                    # Clear any training session state
                    if 'train_custom_style' in st.session_state:
                        del st.session_state.train_custom_style
                    if 'retrain_style' in st.session_state:
                        del st.session_state.retrain_style
                    st.success("✅ Casual style selected!")
                    # Use session state to trigger UI update without full rerun
                    st.session_state.style_selected = True
        
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
                    # Clear any training session state
                    if 'train_custom_style' in st.session_state:
                        del st.session_state.train_custom_style
                    if 'retrain_style' in st.session_state:
                        del st.session_state.retrain_style
                    st.success("✅ Technical style selected!")
                    # Use session state to trigger UI update without full rerun
                    st.session_state.style_selected = True
        
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
    """Display source management interface"""
    st.title("🔗 Source Management")
    st.caption("Manage your content sources and categorize them by niche")
    
    # Add new source
    with st.expander("Add New Source"):
        with st.form("add_source_form"):
            source_url = st.text_input("Source URL", placeholder="https://example.com/rss")
            source_name = st.text_input("Source Name", placeholder="Tech News")
            niche = st.selectbox("Content Niche", [
                "AI", "ML", "Technology", "Gaming", "Science", "Business", 
                "Politics", "Entertainment", "Sports", "Health", "Other"
            ])
            source_type = st.selectbox("Source Type", ["RSS Feed", "Website", "YouTube Video", "YouTube Channel", "Twitter Profile", "Twitter Hashtag", "Other"])
            
            # Show help for YouTube sources
            if source_type in ["YouTube Video", "YouTube Channel"]:
                if source_type == "YouTube Video":
                    st.info("💡 **YouTube Video**: Use individual video URLs like `https://www.youtube.com/watch?v=VIDEO_ID`")
                else:
                    st.info("💡 **YouTube Channel**: Use channel URLs like `https://www.youtube.com/@ChannelName` (Note: Channel support requires YouTube Data API)")
            
            # Show help for Twitter sources
            elif source_type in ["Twitter Profile", "Twitter Hashtag"]:
                if source_type == "Twitter Profile":
                    st.info("💡 **Twitter Profile**: Use Twitter profile URLs like `https://twitter.com/username` or just `@username`")
                else:
                    st.info("💡 **Twitter Hashtag**: Use hashtag like `#AI` or `#MachineLearning` (Note: Twitter API key required)")
            
            if st.form_submit_button("Add Source", type="primary"):
                if source_url and source_name:
                    try:
                        # Add source to local storage
                        new_source = {
                            'url': source_url,
                            'name': source_name,
                            'niche': niche,
                            'type': source_type,
                            'added_at': datetime.now().isoformat()
                        }
                        
                        if new_source:
                            # Also add to local user data for backward compatibility
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
                            st.success("Source added successfully!")
                            st.rerun()
                        else:
                            st.error("Failed to add source to database")
                    except Exception as e:
                        st.error(f"Error adding source: {str(e)}")
    
    # Pre-configured sources
    st.subheader("📚 Pre-configured Sources")
    st.caption("Click to add popular sources to your collection")
    
    # Define pre-configured sources based on dropdown categories
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
        "🔬 Science Sources": [
            {"name": "Nature News", "url": "https://www.nature.com/news", "niche": "Science", "type": "Website"},
            {"name": "Science Daily", "url": "https://www.sciencedaily.com/", "niche": "Science", "type": "Website"},
            {"name": "MIT News", "url": "https://news.mit.edu/", "niche": "Science", "type": "Website"},
            {"name": "Stanford News", "url": "https://news.stanford.edu/", "niche": "Science", "type": "Website"},
            {"name": "Scientific American", "url": "https://www.scientificamerican.com/", "niche": "Science", "type": "Website"}
        ],
        "💼 Business Sources": [
            {"name": "Harvard Business Review", "url": "https://hbr.org/", "niche": "Business", "type": "Website"},
            {"name": "Forbes", "url": "https://www.forbes.com/", "niche": "Business", "type": "Website"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com/", "niche": "Business", "type": "Website"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com/", "niche": "Business", "type": "Website"},
            {"name": "Financial Times", "url": "https://www.ft.com/", "niche": "Business", "type": "Website"}
        ],
        "🏛️ Politics Sources": [
            {"name": "Politico", "url": "https://www.politico.com/", "niche": "Politics", "type": "Website"},
            {"name": "The Hill", "url": "https://thehill.com/", "niche": "Politics", "type": "Website"},
            {"name": "Axios", "url": "https://www.axios.com/", "niche": "Politics", "type": "Website"},
            {"name": "FiveThirtyEight", "url": "https://fivethirtyeight.com/", "niche": "Politics", "type": "Website"},
            {"name": "RealClearPolitics", "url": "https://www.realclearpolitics.com/", "niche": "Politics", "type": "Website"}
        ],
        "🎬 Entertainment Sources": [
            {"name": "Variety", "url": "https://variety.com/", "niche": "Entertainment", "type": "Website"},
            {"name": "The Hollywood Reporter", "url": "https://www.hollywoodreporter.com/", "niche": "Entertainment", "type": "Website"},
            {"name": "Entertainment Weekly", "url": "https://ew.com/", "niche": "Entertainment", "type": "Website"},
            {"name": "Deadline", "url": "https://deadline.com/", "niche": "Entertainment", "type": "Website"},
            {"name": "IndieWire", "url": "https://www.indiewire.com/", "niche": "Entertainment", "type": "Website"}
        ],
        "⚽ Sports Sources": [
            {"name": "ESPN", "url": "https://www.espn.com/", "niche": "Sports", "type": "Website"},
            {"name": "Sports Illustrated", "url": "https://www.si.com/", "niche": "Sports", "type": "Website"},
            {"name": "The Athletic", "url": "https://theathletic.com/", "niche": "Sports", "type": "Website"},
            {"name": "Bleacher Report", "url": "https://bleacherreport.com/", "niche": "Sports", "type": "Website"},
            {"name": "CBS Sports", "url": "https://www.cbssports.com/", "niche": "Sports", "type": "Website"}
        ],
        "🏥 Health Sources": [
            {"name": "WebMD", "url": "https://www.webmd.com/", "niche": "Health", "type": "Website"},
            {"name": "Mayo Clinic", "url": "https://www.mayoclinic.org/", "niche": "Health", "type": "Website"},
            {"name": "Healthline", "url": "https://www.healthline.com/", "niche": "Health", "type": "Website"},
            {"name": "Medical News Today", "url": "https://www.medicalnewstoday.com/", "niche": "Health", "type": "Website"},
            {"name": "Harvard Health", "url": "https://www.health.harvard.edu/", "niche": "Health", "type": "Website"}
        ],
        "📺 YouTube AI/ML Channels": [
            {"name": "Two Minute Papers", "url": "https://www.youtube.com/@TwoMinutePapers", "niche": "AI", "type": "YouTube Channel"},
            {"name": "3Blue1Brown", "url": "https://www.youtube.com/@3blue1brown", "niche": "ML", "type": "YouTube Channel"},
            {"name": "Lex Fridman", "url": "https://www.youtube.com/@lexfridman", "niche": "AI", "type": "YouTube Channel"},
            {"name": "Yannic Kilcher", "url": "https://www.youtube.com/@YannicKilcher", "niche": "AI", "type": "YouTube Channel"},
            {"name": "sentdex", "url": "https://www.youtube.com/@sentdex", "niche": "ML", "type": "YouTube Channel"},
            {"name": "CodeEmporium", "url": "https://www.youtube.com/@CodeEmporium", "niche": "ML", "type": "YouTube Channel"},
            {"name": "AI Explained", "url": "https://www.youtube.com/@AIExplained", "niche": "AI", "type": "YouTube Channel"},
            {"name": "Machine Learning Street Talk", "url": "https://www.youtube.com/@MachineLearningStreetTalk", "niche": "ML", "type": "YouTube Channel"}
        ],
        "📺 YouTube Tech Channels": [
            {"name": "Marques Brownlee (MKBHD)", "url": "https://www.youtube.com/@mkbhd", "niche": "Technology", "type": "YouTube Channel"},
            {"name": "Linus Tech Tips", "url": "https://www.youtube.com/@LinusTechTips", "niche": "Technology", "type": "YouTube Channel"},
            {"name": "TechWorld with Nana", "url": "https://www.youtube.com/@TechWorldwithNana", "niche": "Technology", "type": "YouTube Channel"},
            {"name": "Fireship", "url": "https://www.youtube.com/@Fireship", "niche": "Technology", "type": "YouTube Channel"},
            {"name": "The Verge", "url": "https://www.youtube.com/@TheVerge", "niche": "Technology", "type": "YouTube Channel"},
            {"name": "CNET", "url": "https://www.youtube.com/@CNET", "niche": "Technology", "type": "YouTube Channel"},
            {"name": "TechCrunch", "url": "https://www.youtube.com/@TechCrunch", "niche": "Technology", "type": "YouTube Channel"},
            {"name": "Ars Technica", "url": "https://www.youtube.com/@ArsTechnica", "niche": "Technology", "type": "YouTube Channel"}
        ]
    }
    
    # Display predefined sources by category
    for category, sources in predefined_sources.items():
        with st.expander(f"{category} ({len(sources)} sources)"):
            cols = st.columns(2)
            for i, source in enumerate(sources):
                with cols[i % 2]:
                    col1, col2 = st.columns([3, 1])
                    with col1:
                        st.write(f"**{source['name']}**")
                        st.caption(f"{source['url']}")
                        st.write(f"*{source['niche']} • {source['type']}*")
                    with col2:
                        if st.button("➕", key=f"add_{category}_{i}", help="Add this source"):
                            try:
                                # Check if source already exists in local storage
                                existing_sources = user.get('sources', [])
                                existing_urls = [s['url'] for s in existing_sources]
                                
                                if source['url'] in existing_urls:
                                    st.warning("Source already added!")
                                else:
                                    # Add source to local storage
                                    new_source = {
                                        'url': source['url'],
                                        'name': source['name'],
                                        'niche': source['niche'],
                                        'type': source['type'],
                                        'added_at': datetime.now().isoformat()
                                    }
                                    
                                    if new_source:
                                        # Also add to local user data for backward compatibility
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
                                        st.success("Added!")
                                        st.rerun()
                                    else:
                                        st.error("Failed to add source to database")
                            except Exception as e:
                                st.error(f"Error adding source: {str(e)}")
    
    # Display existing sources
    try:
        # Get sources from local storage
        sources = user.get('sources', [])
        if sources:
            st.subheader("Your Sources")
            for i, source in enumerate(sources):
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])
                
                with col1:
                    st.write(f"**{source['name']}**")
                    st.caption(source['url'])
                
                with col2:
                    st.write(f"**Niche:** {source['niche']}")
                
                with col3:
                    st.write(f"**Type:** {source['type']}")
                
                with col4:
                    if st.button("🗑️", key=f"delete_{i}"):
                        try:
                            # Delete from local storage
                            if True:  # Always succeed for local storage
                                # Also update local data
                                if 'sources' in user:
                                    user['sources'] = [s for s in user['sources'] if s['url'] != source['url']]
                                    auth_manager.update_user_data(user['user_id'], {'sources': user['sources']})
                                st.success("Source deleted!")
                                # Use session state to trigger UI update without full rerun
                                st.session_state.source_deleted = True
                            else:
                                st.error("Failed to delete source")
                        except Exception as e:
                            st.error(f"Error deleting source: {str(e)}")
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
    st.title("📰 Generate Draft")
    st.caption("Generate a personalized newsletter draft using your style and sources")
    
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
    st.title("⚙️ Settings")
    
    # Delivery settings
    st.subheader("Delivery Settings")
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
=======
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
>>>>>>> 32eab2a55c2a460898d3aeacbd94ee64ab0f0d15
