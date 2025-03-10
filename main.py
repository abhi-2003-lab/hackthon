import streamlit as st
import httpx
import requests
from langchain_community.document_loaders import WebBaseLoader
from bs4 import BeautifulSoup
from chains import Chain
from portfolio import Portfolio
from utils import clean_text

# 🔹 Custom CSS for Blue Background & UI Enhancements
def add_custom_css():
    st.markdown("""
        <style>
        body {
            background: linear-gradient(to right, #004e92, #000428);
            color: white;
        }
        .stApp {
            background: linear-gradient(to right, #004e92, #000428);
        }
        .stTextInput > div > div > input {
            background-color: #FFFFFF;
            color: black;
            border-radius: 8px;
            padding: 10px;
        }
        .stButton > button {
            background-color: #007bff;
            color: white;
            border-radius: 8px;
            padding: 10px 15px;
            border: none;
            font-weight: bold;
            transition: background 0.3s ease-in-out;
        }
        .stButton > button:hover {
            background-color: #0056b3;
        }
        .stMarkdown {
            color: white;
        }
        </style>
    """, unsafe_allow_html=True)

# 🔹 Function to Fetch URL Content with Timeout Handling
def fetch_url_content(url, timeout=30, max_retries=5):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }

    for attempt in range(max_retries):
        try:
            with httpx.Client(timeout=timeout, follow_redirects=True) as client:
                response = client.get(url, headers=headers)
                response.raise_for_status()

                final_url = response.url
                if final_url != url:
                    st.info(f"🔄 Redirected to: {final_url}")

                return response.text

        except (httpx.TimeoutException, requests.exceptions.Timeout):
            st.warning(f"⚠️ Attempt {attempt + 1}/{max_retries}: Request timed out. Retrying...")

        except httpx.RequestError as e:
            if "getaddrinfo failed" in str(e):  
                st.error("❌ DNS resolution failed. Try changing your DNS to 8.8.8.8.")
            else:
                st.error(f"⚠️ Error: {e}")
            return None

    # 🔄 Fallback to `requests` if `httpx` fails
    try:
        st.info("🔄 Switching to fallback method (requests)...")
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        return response.text
    except requests.RequestException as e:
        st.error(f"❌ Error: {e}")
        return None

    st.error("❌ Maximum retries reached. The website is not responding.")
    return None

# 🔹 Function to Generate AI Email
def write_mail(job, links):
    email_body = f"""
**Subject:** {job.get('title', 'Exciting Job Opportunity')} - Interest in {job.get('company', 'Your Company')}

**Dear Hiring Manager,**

I came across the **{job.get('title', 'role')}** at **{job.get('company', 'your company')}** and was impressed by your commitment to **{job.get('mission', 'industry excellence')}**.

With extensive experience in **{", ".join(job.get("skills", []))}**, our team has successfully delivered projects that drive **{job.get("goals", "business growth and efficiency")}**.

### **Portfolio Highlights**  
{", ".join(links) if links else "Portfolio links available upon request."}

I'd love to discuss how our expertise can contribute to your team's success. Please let me know if we can schedule a call.

**Best Regards,**  
Your Name  
Your Position  
Your Company  
"""
    return email_body

# 🔹 Main Streamlit App
def create_streamlit_app(llm, portfolio, clean_text):
    add_custom_css()

    st.title("📧 AI Mail Generator")
    url_input = st.text_input("Enter a Job Listing URL:", value="https://jobs.nike.com/job/R-37121?from=job%20search%20funnel")
    submit_button = st.button("Submit")

    if submit_button:
        with st.spinner("Fetching job details... Please wait."):
            try:
                html_content = fetch_url_content(url_input, timeout=30, max_retries=5)

                if html_content:
                    try:
                        loader = WebBaseLoader([url_input])  
                        data = clean_text(loader.load().pop().page_content)
                    except Exception as loader_error:
                        st.warning(f"⚠️ WebBaseLoader failed: {loader_error}. Trying manual parsing...")
                        soup = BeautifulSoup(html_content, "html.parser")
                        data = clean_text(soup.get_text())

                    # Debugging - Show Raw Extracted Data
                    st.write("### Extracted Job Data Preview:")
                    st.text(data[:500])

                    portfolio.load_portfolio()
                    jobs = llm.extract_jobs(data)

                    # Debugging - Show Extracted Job Details
                    st.write("### Extracted Job Details:")
                    st.json(jobs)

                    if not jobs:
                        st.error("❌ No jobs extracted. The webpage format may have changed.")

                    for job in jobs:
                        skills = job.get("skills", [])
                        links = portfolio.query_links(skills)
                        email = write_mail(job, links)

                        # Display the generated email with markdown formatting
                        st.markdown(f"```\n{email}\n```")

            except Exception as e:
                st.error(f"❌ An Error Occurred: {e}")

# 🔹 Run Streamlit App
if __name__ == "__main__":
    chain = Chain()
    portfolio = Portfolio()
    st.set_page_config(layout="wide", page_title="AI Mail Generator", page_icon="📧")
    create_streamlit_app(chain, portfolio, clean_text)
