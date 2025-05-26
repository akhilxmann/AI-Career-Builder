 import os
import streamlit as st
import stripe
from fpdf import FPDF
import base64

stripe.api_key = os.getenv('STRIPE_SECRET_KEY')  

PRICE_IDS = {
    "Daily": "price_daily_$10,        
    "Weekly": "price_weekly_$”20,
    "Monthly": "price_monthly_$”50,
    "Lifetime": "price_lifetime_450”
}

APP_NAME = "AI Career Builder Ultimate"
OWNER = "Akhil Mann"
EMAIL = "werttreat@gmail.com"
DOMAIN = "https://ai-career-builder-tlkzz8xxeamz7svg78ek88.streamlit.app"

st.set_page_config(page_title=APP_NAME, page_icon="🚀", layout="wide")

# === ANIMATION ===
def load_lottie_animation(url):
    import requests
    r = requests.get(url)
    if r.status_code == 200:
        return r.json()
    else:
        return None

lottie_resume = load_lottie_animation("https://assets9.lottiefiles.com/packages/lf20_kyu7xb1v.json")
lottie_premium = load_lottie_animation("https://assets10.lottiefiles.com/packages/lf20_qhrndegw.json")

# === SESSION STATE ===
if "free_resume_used" not in st.session_state:
    st.session_state.free_resume_used = False
if "premium_unlocked" not in st.session_state:
    st.session_state.premium_unlocked = False

# === SIDEBAR ===
with st.sidebar:
    st.title("⚙️ Settings & Customization")
    resume_style = st.selectbox("Resume Style", ["Formal", "Modern", "Creative"])
    tone = st.selectbox("Tone", ["Professional", "Friendly", "Confident"])
    length = st.selectbox("Resume Length", ["Short", "Medium", "Detailed"])
    language = st.selectbox("Language", ["English", "Spanish", "French", "Hindi"])
    dark_mode = st.toggle("🌙 Dark Mode", value=False)

    st.markdown("---")
    st.subheader("💎 Unlock Pro Features")

    if not st.session_state.premium_unlocked:
        st.info("Generate 1 resume free. Unlock unlimited resumes + Pro features below.")

        for plan, price_id in PRICE_IDS.items():
            if st.button(f"Buy {plan} Plan"):
                try:
                    session = stripe.checkout.Session.create(
                        payment_method_types=['card'],
                        line_items=[{
                            'price': price_id,
                            'quantity': 1,
                        }],
                        mode='payment',
                        success_url=DOMAIN + '/success',
                        cancel_url=DOMAIN + '/cancel',
                    )
                    st.markdown(
                        f'<a href="{session.url}" target="_blank" style="color:#fff;background:#2b8cff;padding:10px 30px;border-radius:12px;text-decoration:none;font-weight:700;display:inline-block;margin-top:16px;">Pay for {plan} Plan</a>',
                        unsafe_allow_html=True)
                except Exception as e:
                    st.error(f"Stripe error: {e}")

    st.markdown("---")
    st.write(f"© 2025 {APP_NAME} | {OWNER} | {EMAIL}")

# === HEADER + LOTTIE ===
st.markdown(f"<h1 style='text-align:center;font-size:3em;font-weight:900'>{APP_NAME}</h1>", unsafe_allow_html=True)
if not st.session_state.premium_unlocked:
    st_lottie_url = "https://assets9.lottiefiles.com/packages/lf20_kyu7xb1v.json"
else:
    st_lottie_url = "https://assets10.lottiefiles.com/packages/lf20_qhrndegw.json"

try:
    from streamlit_lottie import st_lottie
    st_lottie(load_lottie_animation(st_lottie_url), height=220)
except Exception:
    pass  # If Lottie fails, continue silently

st.markdown("### 🚀 Build Your Dream Resume With AI")

# === FORM ===
with st.form("resume_form"):
    col1, col2 = st.columns([2,1])
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
        page_count = st.selectbox("Number of Pages", [1,2])
        pdf_or_txt = st.selectbox("Download Format", ["PDF", "TXT"])

    submitted = st.form_submit_button("Generate Resume 🚀")

# === RESUME GENERATION LOGIC ===
def enrich_content(text, context):
    # Minimal offline enrichment
    if not text or len(text.strip()) < 10:
        if "data scientist" in context.lower():
            return "Developed advanced ML models, led data-driven initiatives, published research in top journals."
        elif "developer" in context.lower():
            return "Built scalable web applications, managed databases, optimized algorithms for performance."
        elif "designer" in context.lower():
            return "Designed engaging UIs, improved user experience, led creative campaigns for major brands."
        else:
            return "Contributed to organizational growth, exceeded targets, developed leadership and teamwork skills."
    return text

def make_resume_txt(**kwargs):
    # Professional format (expand as needed)
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
        txt += "\n\nADDITIONAL ENRICHMENT\nLeadership, Certifications, Volunteering, Soft Skills, and Professional Growth."
    return txt

def make_resume_pdf(**kwargs):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 18)
    pdf.cell(0, 15, name, ln=1, align='C')
    if photo:
        import tempfile
        import PIL.Image
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
        image = PIL.Image.open(photo)
        image = image.resize((80, 80))
        image.save(temp_file.name)
        pdf.image(temp_file.name, x=165, y=20, w=30, h=30)
    pdf.set_font("Helvetica", "I", 14)
    pdf.cell(0, 10, title, ln=1, align='C')
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 7, f"\nContact: {email} | {phone}\nLinkedIn: {linkedin if linkedin else 'N/A'}\n", align='C')
    pdf.ln(3)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "SUMMARY", ln=1)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, enrich_content(summary, title))
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "SKILLS", ln=1)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, enrich_content(skills, title))
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "EXPERIENCE", ln=1)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, enrich_content(experience, title))
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "EDUCATION", ln=1)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, enrich_content(education, title))
    pdf.ln(1)
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 8, "PROJECTS / ACHIEVEMENTS", ln=1)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(0, 6, enrich_content(projects, title))
    if int(page_count) == 2:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 13)
        pdf.cell(0, 8, "ADDITIONAL ENRICHMENT", ln=1)
        pdf.set_font("Helvetica", "", 11)
        pdf.multi_cell(0, 6, "Leadership, Certifications, Volunteering, Soft Skills, and Professional Growth.")
    return pdf

if submitted:
    # === FREE VS PAID LOGIC ===
    if not st.session_state.free_resume_used or st.session_state.premium_unlocked:
        # Show loading animation
        with st.spinner("Generating your beautiful resume..."):
            import time
            time.sleep(2)
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

            # Set session state to show resume used
            if not st.session_state.premium_unlocked:
                st.session_state.free_resume_used = True
    else:
        st.warning("🔒 You have used your free resume. Please unlock unlimited resumes in the sidebar to continue.")

# === SUCCESS/CANCEL (manual) ===
st.markdown("---")
st.info(f"Contact: {EMAIL} | All rights reserved © {OWNER} 2025")
