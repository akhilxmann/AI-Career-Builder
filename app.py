import streamlit as st
import stripe
import os

# Stripe secret key (replace with your real key)
stripe.api_key = 'sk_live_your_secret_key_here'

# Track free resume generation
if 'free_used' not in st.session_state:
    st.session_state.free_used = False

st.set_page_config(page_title="AI Career Builder Ultimate", page_icon="💼", layout="wide")
st.title("💼 AI Career Builder Ultimate")

# Sidebar: Plans & Payment
st.sidebar.title("💳 Payment & Access")

plans = {
    "Daily Access ($10/day)": 'price_daily_xxxxxx',
    "Weekly Pass ($50/week)": 'price_weekly_xxxxxx',
    "Monthly Pro ($150/month)": 'price_monthly_xxxxxx',
    "Lifetime Access ($500 one-time)": 'price_lifetime_xxxxxx'
}

if not st.session_state.free_used:
    st.sidebar.success("🎉 You can generate 1 free resume!")
else:
    st.sidebar.warning("🔒 Premium access required for more resumes.")

for plan, price_id in plans.items():
    if st.sidebar.button(f"Buy {plan}"):
        try:
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price': price_id,
                    'quantity': 1,
                }],
                mode='payment',
                success_url='https://ai-career-builder-tlkzz8xxeamz7svg78ek88.streamlit.app/success',
                cancel_url='https://ai-career-builder-tlkzz8xxeamz7svg78ek88.streamlit.app/cancel',
            )
            st.sidebar.markdown(f"[👉 Click here to pay]({session.url})", unsafe_allow_html=True)
        except Exception as e:
            st.sidebar.error(f"Payment error: {str(e)}")

# Resume Builder Form
st.subheader("🚀 Build Your Professional Resume")
name = st.text_input("Your Name")
title = st.text_input("Professional Title")
email = st.text_input("Email")
phone = st.text_input("Phone Number")
summary = st.text_area("Professional Summary")
skills = st.text_input("Skills (comma-separated)")
experience = st.text_area("Work Experience")
education = st.text_area("Education")
projects = st.text_area("Projects or Achievements")

if st.button("Generate Resume"):
    if not st.session_state.free_used:
        st.session_state.free_used = True
        unlocked = True
    else:
        unlocked = False

    if unlocked:
        resume_text = f"""
        {name.upper()}
        {title}

        Contact: {email} | {phone}

        SUMMARY
        {summary}

        SKILLS
        {skills}

        EXPERIENCE
        {experience}

        EDUCATION
        {education}

        PROJECTS / ACHIEVEMENTS
        {projects}

        BONUS ENRICHMENT
        Leadership roles, certifications, teamwork experience, adaptability, problem-solving, cross-functional collaboration.
        """

        st.success("✅ Resume generated! Download below.")
        st.download_button("Download Resume (TXT)", resume_text, file_name="resume.txt")
    else:
        st.error("❗ You’ve used your free resume. Please choose a plan on the left to unlock unlimited access.")

st.sidebar.markdown("---")
st.sidebar.markdown("© 2025 AI Career Builder Ultimate | Akhil Mann | werttreat@gmail.com")
