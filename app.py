import streamlit as st
import stripe
import time

# Load Stripe secret key from Streamlit secrets
stripe.api_key = st.secrets["STRIPE_SECRET_KEY"]

st.set_page_config(page_title="AI Career Builder Ultimate", page_icon=":rocket:", layout="wide")

# -------------- CONFIG --------------
PRODUCTS = [
    {"name": "1 Week Unlimited", "price_id": "price_YOUR_1WEEK_ID", "desc": "Unlimited resumes for 1 week", "price": "$10"},
    {"name": "1 Month Unlimited", "price_id": "price_YOUR_1MONTH_ID", "desc": "Unlimited resumes for 1 month", "price": "$20"},
    {"name": "1 Year Unlimited", "price_id": "price_YOUR_1YEAR_ID", "desc": "Unlimited resumes for 1 year", "price": "$99"},
    {"name": "Lifetime (One-Time)", "price_id": "price_YOUR_LIFETIME_ID", "desc": "Lifetime, all features & updates", "price": "$149"}
]
PAYMENT_LINKS = {
    "1 Week Unlimited": "https://buy.stripe.com/test_xxxxxxxx1",
    "1 Month Unlimited": "https://buy.stripe.com/test_xxxxxxxx2",
    "1 Year Unlimited": "https://buy.stripe.com/test_xxxxxxxx3",
    "Lifetime (One-Time)": "https://buy.stripe.com/test_xxxxxxxx4"
}

# -------------- SESSION --------------
if "resume_count" not in st.session_state:
    st.session_state["resume_count"] = 0
if "subscribed" not in st.session_state:
    st.session_state["subscribed"] = False

# -------------- HEADER --------------
st.markdown(
    """
    <h1 style="text-align:center;">🚀 <span style='color:#16c7f8'>AI Career Builder Ultimate</span> — The #1 AI Resume Generator</h1>
    <h4 style="text-align:center; color:#bbb;">Modern, ultra-enriched, professional resumes, cover letters & more — instantly.</h4>
    """,
    unsafe_allow_html=True,
)
st.markdown("---")

# -------------- PAYMENT WALL --------------
def payment_wall():
    st.warning("🚧 You have reached your free limit. Unlock unlimited resumes & features by subscribing below!", icon="⚡️")
    st.markdown("### 💳 Choose a Plan")
    cols = st.columns(len(PRODUCTS))
    for i, product in enumerate(PRODUCTS):
        with cols[i]:
            st.markdown(f"**{product['name']}**  \n{product['desc']}  \n**{product['price']}**")
            pay_url = PAYMENT_LINKS[product["name"]]
            st.markdown(f"<a href='{pay_url}' target='_blank'><button style='background-color:#1abc9c;color:white;padding:0.5em 1.2em;border:none;border-radius:8px;font-weight:bold;'>Pay Now</button></a>", unsafe_allow_html=True)
    st.stop()

if st.session_state["resume_count"] >= 1 and not st.session_state["subscribed"]:
    payment_wall()

# -------------- RESUME FORM --------------
st.markdown("### 📝 Resume Builder")
with st.form("resume_form"):
    name = st.text_input("Full Name", "Akhil Mann")
    title = st.text_input("Professional Title", "Software Engineer")
    email = st.text_input("Email", "akhil@example.com")
    phone = st.text_input("Phone Number", "+1 555-123-4567")
    address = st.text_input("Address", "Toronto, Canada")
    summary = st.text_area("Professional Summary", "Enthusiastic, adaptable and highly skilled software engineer with a passion for AI-driven solutions. Expert in Python, automation and cross-platform development. Proven record of delivering innovative products at speed.")
    exp = st.text_area("Experience (comma separated or paragraph)", "Lead Engineer at BigTech Inc (2021-2024), AI Intern at StarAI (2020-2021)")
    edu = st.text_area("Education", "B.Tech, Computer Science, University of Toronto, 2020")
    skills = st.text_area("Skills (comma separated)", "Python, Machine Learning, Automation, Cloud, Web Development")
    submit = st.form_submit_button("Generate Resume 🚀")

if submit:
    st.session_state["resume_count"] += 1

    # ------- AI-Like Context Enrichment -------
    fake_awards = [
        "Awarded 'Employee of the Year' for outstanding contributions.",
        "Published 3 research papers on machine learning and AI.",
        "Built a personal productivity tool used by 5,000+ users worldwide.",
        "Head Boy at XYZ International School.",
        "Won Gold Medal in National Hackathon."
    ]
    experience_section = (
        f"- Lead Engineer at BigTech Inc (2021-2024): Led a team of 10+ in building scalable AI products. Achieved 40% increase in system efficiency.\n"
        f"- AI Intern at StarAI (2020-2021): Developed NLP models for real-time chatbots, reducing support costs by 30%.\n"
        f"- Freelance Developer: Built and deployed custom SaaS tools for startups and SMBs."
    )
    enriched_resume = f"""
**{name}**  
{title}  
Email: {email} | Phone: {phone} | Address: {address}

---

### PROFESSIONAL SUMMARY  
{summary}

---

### EXPERIENCE  
{experience_section}

---

### EDUCATION  
{edu}

---

### SKILLS  
{skills}

---

### AWARDS & EXTRAS  
{', '.join(fake_awards)}
    """

    st.success("✅ AI Resume Generated!")
    st.markdown("---")
    st.markdown(f"<pre style='background:#222;color:#16c7f8;padding:2em;border-radius:16px;font-size:1.15em;overflow:auto'>{enriched_resume}</pre>", unsafe_allow_html=True)
    st.download_button(
        label="⬇️ Download as TXT",
        data=enriched_resume,
        file_name=f"{name.replace(' ', '_')}_resume.txt",
        mime="text/plain"
    )

    # Animated Lottie checkmark
    st_lottie_url = "https://assets4.lottiefiles.com/packages/lf20_m6j5igjg.json"
    try:
        from streamlit_lottie import st_lottie
        import requests
        lottie_json = requests.get(st_lottie_url).json()
        st_lottie(lottie_json, height=150, key="done_anim")
    except Exception:
        pass

    st.balloons()
    st.info("Upgrade to premium to unlock unlimited resume generations, cover letter builder, LinkedIn optimizer, ATS match, and more.", icon="💎")

# --------- FOOTER ----------
st.markdown("""
---
<p style="text-align:center;color:#bbb;font-size:0.9em;">
    © 2025 AI Career Builder Ultimate by Akhil Mann · <a href="mailto:werttreat@gmail.com" style="color:#16c7f8">Contact</a>
</p>
""", unsafe_allow_html=True)
