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
from transformers import pipeline  # using local AI model

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

@st.cache_resource(show_spinner=False)
def load_local_generator():
    """
    Load the local AI model (distilgpt2) in memory.
    Runs on CPU only.
    """
    return pipeline(
        "text-generation",
        model="distilgpt2",
        tokenizer="distilgpt2",
        device=-1  # CPU device
    )

def enrich_content(text, context):
    """
    If the user-supplied text is very short (<10 chars) or blank:
      - If the user has NOT unlocked premium, return a generic, professionally worded sentence.
      - If the user HAS unlocked premium, generate AI-powered content with distilgpt2.
    Otherwise, return the user's own text.
    """
    ctx = context.strip().lower()
    if not text or len(text.strip()) < 10:
        if not st.session_state.premium_unlocked:
            # Free version: generic professional sentence
            return "Dedicated professional with a proven track record of delivering excellence and driving continuous improvement."
        else:
            # Premium: use AI model for richer content
            prompt = f"{context.title()} Specialist: "
            generator = load_local_generator()
            output = generator(
                prompt,
                max_length=len(prompt.split()) + 40,
                num_return_sequences=1,
                do_sample=True,
                top_p=0.95,
                temperature=0.8
            )
            generated = output[0]["generated_text"]
            return generated.replace(prompt, "").strip()
    return text

def make_resume_txt(**kwargs):
    """Generate a plain-text resume."""
    title_lower = title.strip().lower()

    # If user is a doctor/surgeon, build a one-page, custom resume:
    if "doctor" in title_lower or "surgeon" in title_lower:
        summary_text = (
            f"Results-driven {title.title()} with over 10 years of experience "
            "specializing in facial reconstructive and cosmetic surgery. "
            "Adept at leading surgery teams, developing patient care protocols, "
            "and mentoring junior surgeons to achieve optimal outcomes."
        )
        skills_text = (
            "- Facial Reconstruction Surgery\n"
            "- Cosmetic and Reconstructive Techniques\n"
            "- Patient Consultation and Management\n"
            "- Surgical Planning and Execution\n"
            "- Post-Operative Care and Follow-Up\n"
            "- Clinical Research and Publications"
        )
        experience_text = (
            "- 2013-Present: Senior Face Surgeon, ABC Medical Center, Metropolis, USA\n"
            "  * Performed over 650 successful facial reconstructive surgeries, "
            "improving patient satisfaction by 40%.\n"
            "  * Led a team of 5 junior surgeons and 10 nursing staff, developing "
            "standardized surgical protocols reducing complications by 25%.\n"
            "  * Published 10+ research papers on advanced surgical techniques in "
            "peer-reviewed journals.\n\n"
            "- 2010-2013: Face Surgery Resident, XYZ University Hospital, Metropolis, USA\n"
            "  * Completed rigorous residency focused on maxillofacial reconstruction, "
            "trauma management, and microsurgery.\n"
            "  * Assisted in 300+ complex surgeries and managed patient follow-up care."
        )
        education_text = (
            "Doctor of Medicine (M.D.), EBBS University, College of Medicine, Metropolis, USA, 2010\n"
            "- Graduated with honors (Top 5% of class)\n"
            "- Completed elective in Advanced Facial Surgery Techniques, 2009"
        )
        projects_text = (
            "- Developed a minimally invasive facial reconstruction protocol "
            "reducing operative time by 30% and improving recovery rates.\n"
            "- Co-creator of the \"Facial Aesthetics Clinic\" initiative, serving over 2000 patients.\n"
            "- Authored research on 3D-printed surgical guides for precise bone reconstruction."
        )

        txt = f"""
{name.upper()}
{title.title()}
Contact: {email} | {phone}
LinkedIn: {linkedin if linkedin else "N/A"}

SUMMARY
{summary_text}

SKILLS
{skills_text}

EXPERIENCE
{experience_text}

EDUCATION
{education_text}

PROJECTS / ACHIEVEMENTS
{projects_text}
"""
        return txt.strip()

    # Otherwise, default to the free/premium content generator:
    txt = f"""
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
    if int(page_count) == 2:
        txt += "\n\nADDITIONAL ENRICHMENT\nLeadership, Certifications, Volunteering, Soft Skills, and Professional Growth.\n"
    return txt.strip()

def make_resume_pdf(**kwargs):
    """Generate a PDF resume with structured sections."""
    title_lower = title.strip().lower()
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
    pdf.cell(0, 10, title.title(), ln=1, align='C')
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, f"Contact: {email} | {phone}\nLinkedIn: {linkedin if linkedin else 'N/A'}\n", align='C')
    pdf.ln(5)

    if "doctor" in title_lower or "surgeon" in title_lower:
        sections = {
            "SUMMARY": (
                f"Results-driven {title.title()} with over 10 years of experience "
                "specializing in facial reconstructive and cosmetic surgery. "
                "Adept at leading surgery teams, developing patient care protocols, "
                "and mentoring junior surgeons to achieve optimal outcomes."
            ),
            "SKILLS": (
                "- Facial Reconstruction Surgery\n"
                "- Cosmetic and Reconstructive Techniques\n"
                "- Patient Consultation and Management\n"
                "- Surgical Planning and Execution\n"
                "- Post-Operative Care and Follow-Up\n"
                "- Clinical Research and Publications"
            ),
            "EXPERIENCE": (
                "- 2013-Present: Senior Face Surgeon, ABC Medical Center, Metropolis, USA\n"
                "  * Performed over 650 successful facial reconstructive surgeries, "
                "improving patient satisfaction by 40%.\n"
                "  * Led a team of 5 junior surgeons and 10 nursing staff, developing "
                "standardized surgical protocols reducing complications by 25%.\n"
                "  * Published 10+ research papers on advanced surgical techniques in "
                "peer-reviewed journals.\n\n"
                "- 2010-2013: Face Surgery Resident, XYZ University Hospital, Metropolis, USA\n"
                "  * Completed rigorous residency focused on maxillofacial reconstruction, "
                "trauma management, and microsurgery.\n"
                "  * Assisted in 300+ complex surgeries and managed patient follow-up care."
            ),
            "EDUCATION": (
                "Doctor of Medicine (M.D.), EBBS University, College of Medicine, Metropolis, USA, 2010\n"
                "- Graduated with honors (Top 5% of class)\n"
                "- Completed elective in Advanced Facial Surgery Techniques, 2009"
            ),
            "PROJECTS / ACHIEVEMENTS": (
                "- Developed a minimally invasive facial reconstruction protocol "
                "reducing operative time by 30% and improving recovery rates.\n"
                "- Co-creator of the \"Facial Aesthetics Clinic\" initiative, serving over 2000 patients.\n"
                "- Authored research on 3D-printed surgical guides for precise bone reconstruction."
            )
        }
    else:
        sections = {
            "SUMMARY": enrich_content(summary, title),
            "SKILLS": enrich_content(skills, title),
            "EXPERIENCE": enrich_content(experience, title),
            "EDUCATION": enrich_content(education, title),
            "PROJECTS / ACHIEVEMENTS": enrich_content(projects, title)
        }

    for section, content in sections.items():
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, section, ln=1)
        pdf.set_font("Helvetica", "", 11)
        for line in content.split("\n"):
            pdf.multi_cell(0, 6, line)
        pdf.ln(3)

    if int(page_count) == 2 and not ("doctor" in title_lower or "surgeon" in title_lower):
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
