import streamlit as st
import stripe
import base64
from fpdf import FPDF
import os
import random
import time
from datetime import datetime
import requests
import streamlit.components.v1 as components

# ───────── Configuration & Secrets ─────────
stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]

PRICE_IDS = {
    "1 Day Access": "price_1RT9VaGRCFNpMv7GYYUcWP1q",
    "1 Week Access": "price_1RT9ZEGRCFNpMv7GWGWSgk64",
    "1 Month Access": "price_1RTCyOGRCFNpMv7GBwfTCTdT"
}

APP_NAME = "AI Career Builder Ultimate"
OWNER = "Akhil Mann"
EMAIL = "werttreat@gmail.com"
DOMAIN = "https://ai-career-builder-tlkzz8xxeamz7svg78ek88.streamlit.app"
ANALYTICS_ID = "UA-XXXXXXXXX-X"  # Replace with your Google Analytics ID

st.set_page_config(
    page_title=APP_NAME,
    page_icon="🚀",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ───────── Session State Defaults ─────────
if "free_resume_used" not in st.session_state:
    st.session_state.free_resume_used = False
if "premium_unlocked" not in st.session_state:
    st.session_state.premium_unlocked = False
if "payment_link" not in st.session_state:
    st.session_state.payment_link = None
if "newsletter_emails" not in st.session_state:
    st.session_state.newsletter_emails = []
if "theme" not in st.session_state:
    st.session_state.theme = "Light"
if "page" not in st.session_state:
    st.session_state.page = "Build Resume"

# ───────── Utility Functions ─────────
def load_lottie_animation(url):
    """Fetch a Lottie animation JSON from a URL."""
    r = requests.get(url)
    return r.json() if r.status_code == 200 else None

def enrich_content(text, context):
    """Return AI-style enriched content for short inputs."""
    ai_examples = {
        "data scientist": [
            "Led development of predictive models using Python and TensorFlow, improving forecast accuracy by 35%.",
            "Engineered real-time data pipelines, reducing data latency by 60%, enabling faster decision-making.",
            "Collaborated with cross-functional teams to deploy scalable ML models in production."
        ],
        "developer": [
            "Developed RESTful APIs with Node.js and Express, serving over 100k monthly users.",
            "Optimized front-end performance with React and Redux, cutting load times by 50%.",
            "Integrated CI/CD pipelines using GitHub Actions, boosting release efficiency."
        ],
        "designer": [
            "Crafted UI/UX for mobile apps with over 1M downloads using Figma and Adobe XD.",
            "Redesigned landing pages, increasing conversion rate by 22% via A/B testing.",
            "Created brand identity systems, establishing consistent visual language."
        ],
        "default": [
            "Championed strategic initiatives, enhancing team performance and operational efficiency.",
            "Recognized for leadership in project execution and stakeholder engagement.",
            "Spearheaded training programs, elevating skillsets across departments."
        ]
    }
    if not text or len(text.strip()) < 10:
        key = next((k for k in ai_examples if k in context.lower()), "default")
        return random.choice(ai_examples[key])
    return text

def make_resume_txt(**kwargs):
    """Generate a plain-text resume."""
    return f"""
{name.upper()}
{title}
Contact: {email} | {phone}
LinkedIn: {linkedin if linkedin else "N/A"}

SUMMARY
{enrich_content(summary, title)}

SKILLS
{enrich_content(skills, title)}

EXPERIENCE
{enrich_content(experience, title)}

EDUCATION
{enrich_content(education, title)}

PROJECTS / ACHIEVEMENTS
{enrich_content(projects, title)}
"""

def make_resume_pdf(**kwargs):
    """Generate a PDF resume."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 15, name, ln=1, align='C')
    if photo:
        import tempfile
        import PIL.Image
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        image = PIL.Image.open(photo).resize((80, 80))
        image.save(temp_file.name)
        pdf.image(temp_file.name, x=165, y=20, w=30, h=30)
    pdf.set_font("Helvetica", "I", 14)
    pdf.cell(0, 10, title, ln=1, align='C')
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, f"\nContact: {email} | {phone}\nLinkedIn: {linkedin if linkedin else 'N/A'}\n", align='C')
    sections = [
        ("SUMMARY", enrich_content(summary, title)),
        ("SKILLS", enrich_content(skills, title)),
        ("EXPERIENCE", enrich_content(experience, title)),
        ("EDUCATION", enrich_content(education, title)),
        ("PROJECTS / ACHIEVEMENTS", enrich_content(projects, title))
    ]
    for section, content in sections:
        pdf.ln(2)
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, section, ln=1)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, content)
    if int(page_count) == 2:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "ADDITIONAL ENRICHMENT", ln=1)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, "Leadership, Certifications, Volunteering, Soft Skills, and Professional Growth.")
    return pdf

# ───────── Google Analytics Snippet ─────────
analytics_code = f"""
<script async src="https://www.googletagmanager.com/gtag/js?id={ANALYTICS_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{ANALYTICS_ID}');
</script>
"""
components.html(analytics_code, height=0, width=0)

# ───────── Sidebar Home Button & Navigation ─────────
st.sidebar.image("https://raw.githubusercontent.com/akulapena/logos/main/logo.png", width=120)  # placeholder logo URL
if st.sidebar.button("🏠 Home"):
    st.session_state.page = "Build Resume"
page = st.sidebar.radio("Navigate", ["Build Resume", "Contact Us", "Chatbot", "Weather", "Subscribe"], key="page")

# ───────── STYLE CUSTOMIZATION ─────────
st.sidebar.markdown("---")
st.sidebar.subheader("🎨 Theme & UI Settings")
theme_choice = st.sidebar.selectbox("Color Theme", ["Light", "Dark", "Midnight Blue", "Emerald Green"])
st.session_state.theme = theme_choice

accent_color = st.sidebar.color_picker("Accent Color", "#43ffd8")
font_choice = st.sidebar.selectbox("Font", ["Helvetica", "Arial", "Monospace", "Georgia"])

# Inject CSS for theme and font
custom_css = f"""
<style>
body {{ font-family: '{font_choice}', sans-serif; }}
[data-testid="stAppViewContainer"] {{
    background-color: {'#111827' if theme_choice in ['Dark','Midnight Blue'] else '#ffffff'} !important;
}}
h1, h2, h3, h4, h5, h6 {{ color: {accent_color}; }}
a {{ color: {accent_color}; }}
button {{ background-color: {accent_color} !important; }}
</style>
"""
st.markdown(custom_css, unsafe_allow_html=True)

# ───────── PAGE: BUILD RESUME ─────────
if page == "Build Resume":
    st.markdown(f"<h1 style='text-align:center;font-size:3em;font-weight:900'>{APP_NAME}</h1>", unsafe_allow_html=True)
    try:
        from streamlit_lottie import st_lottie
        st_lottie(load_lottie_animation("https://assets9.lottiefiles.com/packages/lf20_kyu7xb1v.json"), height=220)
    except Exception:
        pass
    st.markdown("### 🚀 Build Your Dream Resume With AI")
    st.markdown(
        """
        <div style="text-align:center; margin-top:-10px; margin-bottom:20px;">
            <span style="background:linear-gradient(to right, #ff416c, #ff4b2b); color:white; padding:10px 24px; border-radius:20px; font-weight:bold; font-size:1.1em;">
                🤖 AI Integration Coming Soon – Stay Tuned!
            </span>
        </div>
        """, unsafe_allow_html=True
    )

    # ─── PRO FEATURE BUY BUTTONS ───
    if not st.session_state.premium_unlocked:
        st.subheader("💎 Unlock Pro Features")
        st.info("Generate 1 resume free. Unlock unlimited resumes + Pro features below.")
        for plan, price_id in PRICE_IDS.items():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f"**{plan}**")
            with col2:
                if st.button(f"Buy {plan}", key=plan):
                    try:
                        session = stripe.checkout.Session.create(
                            payment_method_types=['card'],
                            line_items=[{'price': price_id, 'quantity': 1}],
                            mode="subscription",
                            success_url=DOMAIN + '?success=1',
                            cancel_url=DOMAIN + '?canceled=1',
                        )
                        st.session_state.payment_link = session.url
                        st.markdown(
                            f'<a href="{session.url}" target="_blank" style="color:#fff;background:#2b8cff;padding:10px 20px;border-radius:8px;text-decoration:none;font-weight:700;">Pay</a>',
                            unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Stripe error: {e}")
        st.markdown("---")

    # If payment link is generated
    if st.session_state.payment_link:
        st.markdown(
            f'<div style="text-align:center">'
            f'<a href="{st.session_state.payment_link}" target="_blank">'
            '<button style="font-size:20px;padding:12px 24px;border-radius:8px;background:linear-gradient(90deg,#2463EB,#5EEAD4);color:#fff;border:none;">Pay Now</button>'
            '</a></div>', unsafe_allow_html=True
        )
        st.info("Once paid, return to this page. Your purchase will unlock unlimited resume generation.")

    with st.form("resume_form"):
        col1, col2 = st.columns([2, 1])
        with col1:
            name = st.text_input("Full Name", placeholder="e.g. Akhil Mann")
            title = st.text_input("Professional Title", placeholder="e.g. Data Scientist")
            summary = st.text_area("Professional Summary", placeholder="A results-driven data scientist...")
            skills = st.text_input("Skills (comma-separated)", placeholder="Python, SQL, Machine Learning")
            experience = st.text_area("Work Experience", placeholder="Company, Position, Dates, Responsibilities...")
            education = st.text_area("Education", placeholder="College, Degree, Dates...")
            projects = st.text_area("Projects or Achievements", placeholder="Project name, Description...")
        with col2:
            email = st.text_input("Email", placeholder="your@email.com")
            phone = st.text_input("Phone Number", placeholder="+1-xxx-xxx-xxxx")
            linkedin = st.text_input("LinkedIn (optional)", placeholder="linkedin.com/in/akhilmann")
            photo = st.file_uploader("Profile Photo (optional)", type=["jpg", "jpeg", "png"])
            page_count = st.selectbox("Number of Pages", [1, 2])
            pdf_or_txt = st.selectbox("Download Format", ["PDF", "TXT"])
        submitted = st.form_submit_button("Generate Resume 🚀")

    if submitted:
        with st.spinner("Generating your resume with AI magic..."):
            progress = st.progress(0)
            for i in range(5):
                time.sleep(0.2)
                progress.progress((i + 1) * 20)
            if pdf_or_txt == "PDF":
                pdf = make_resume_pdf()
                tmpfile = f"/tmp/{name.replace(' ', '_')}_resume.pdf"
                pdf.output(tmpfile)
                with open(tmpfile, "rb") as f:
                    b64 = base64.b64encode(f.read()).decode()
                    st.success("✅ Resume ready! Download your PDF below.")
                    href = f'<a href="data:application/pdf;base64,{b64}" download="{name}_resume.pdf">Download Resume PDF</a>'
                    st.markdown(href, unsafe_allow_html=True)
            else:
                txt = make_resume_txt()
                st.download_button("Download Resume (TXT)", txt, file_name=f"{name}_resume.txt")
            if not st.session_state.premium_unlocked:
                st.session_state.free_resume_used = True

    st.markdown("---")
    st.info(f"Contact: {EMAIL} | All rights reserved © {OWNER} {datetime.now().year}")

# ───────── PAGE: CONTACT US ─────────
elif page == "Contact Us":
    st.title("📨 Contact Us")
    st.write("We'd love to hear from you. Fill out the form below and we'll respond ASAP!")
    with st.form("contact_form"):
        contact_name = st.text_input("Your Name")
        contact_email = st.text_input("Your Email")
        contact_msg = st.text_area("Message")
        submitted_c = st.form_submit_button("Send")
    if submitted_c:
        st.success("Thanks for reaching out! We'll get back to you shortly.")
    st.markdown("---")
    st.info(f"Contact: {EMAIL} | All rights reserved © {OWNER} {datetime.now().year}")

# ───────── PAGE: CHATBOT ─────────
elif page == "Chatbot":
    st.title("🤖 AI Chatbot")
    st.markdown("Chat with our AI assistant for quick resume advice, tips, or general questions.")
    chatbot_html = """
    <iframe
        width="100%"
        height="600"
        src="https://example-chatbot.com/embed"
        frameborder="0"
        allowfullscreen>
    </iframe>
    """
    st.markdown(chatbot_html, unsafe_allow_html=True)
    st.markdown("---")
    st.info(f"Contact: {EMAIL} | All rights reserved © {OWNER} {datetime.now().year}")

# ───────── PAGE: WEATHER ─────────
elif page == "Weather":
    st.title("🌤️ Check Local Weather")
    st.write("Enter your city to get the current weather conditions.")
    city = st.text_input("City Name", value="Vancouver")
    if st.button("Get Weather"):
        api_key = st.secrets.get("OPENWEATHER_API_KEY", "")
        if api_key:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
            resp = requests.get(url).json()
            if resp.get("cod") == 200:
                weather = resp["weather"][0]["description"].title()
                temp = resp["main"]["temp"]
                st.subheader(f"{city.title()}: {weather}, {temp}°C")
            else:
                st.error("City not found. Please try again.")
        else:
            st.warning("No OpenWeather API key found. Set OPENWEATHER_API_KEY in secrets.")
    st.markdown("---")
    st.info(f"Contact: {EMAIL} | All rights reserved © {OWNER} {datetime.now().year}")

# ───────── PAGE: SUBSCRIBE ─────────
elif page == "Subscribe":
    st.title("📧 Subscribe to Our Newsletter")
    st.write("Stay updated with the latest AI tools, resume tips, and exclusive offers!")
    newsletter_email = st.text_input("Enter your email to subscribe")
    if st.button("Subscribe"):
        if newsletter_email and "@" in newsletter_email:
            st.session_state.newsletter_emails.append(newsletter_email)
            st.success("🎉 Thank you for subscribing! Check your inbox for updates.")
        else:
            st.error("Please enter a valid email address.")
    st.markdown("**Current Subscribers:**")
    st.write(", ".join(st.session_state.newsletter_emails) or "No subscribers yet.")
    st.markdown("---")
    st.info(f"Contact: {EMAIL} | All rights reserved © {OWNER} {datetime.now().year}")
