import os
import json
from langchain_groq import ChatGroq
from langchain_core.prompts import PromptTemplate
from langchain_core.exceptions import OutputParserException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Chain:
    def __init__(self):
        """Initialize ChatGroq with API key & model selection"""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("❌ GROQ_API_KEY is missing. Please set it in the .env file.")

        self.llm = ChatGroq(temperature=0, groq_api_key=api_key, model_name="google-2.0-flash")

    def extract_jobs(self, cleaned_text):
        """Extract job postings from the given text and return them as a JSON list."""
        prompt_extract = PromptTemplate.from_template(
            """
            ### SCRAPED TEXT FROM WEBSITE:
            {page_data}
            ### INSTRUCTION:
            The scraped text is from the career's page of a website.
            Your job is to extract the job postings and return them in JSON format containing the following keys: `role`, `experience`, `skills`, and `description`.
            Only return the valid JSON. No extra text.
            ### VALID JSON:
            """
        )
        chain_extract = prompt_extract | self.llm

        try:
            # Get raw response from LLM
            res = chain_extract.invoke({"page_data": cleaned_text}).content.strip()

            # Fix potential JSON formatting issues
            if res.startswith("```json"):
                res = res[7:-3].strip()  # Remove code block markdown

            jobs = json.loads(res)  # Convert to Python dict
            return jobs if isinstance(jobs, list) else [jobs]  # Ensure it's always a list

        except (json.JSONDecodeError, OutputParserException) as e:
            raise OutputParserException(f"❌ Failed to parse JSON output: {e}")

    def write_mail(self, job, links):
        """Generate a cold email for the given job description & portfolio links."""
        prompt_email = PromptTemplate.from_template(
            """
            JOB DESCRIPTION:
            {job_description}

            INSTRUCTION:
            You are Mohan, a Business Development Executive at XYZ Company.
            XYZ Company specializes in AI & Software Consulting, helping enterprises optimize processes through automation.
            Your task is to write a cold email to the client about the job opportunity, emphasizing how XYZ Company can meet their needs.
            Also, include relevant portfolio links to showcase past projects: {link_list}.
            Do not add a preamble. Only return the email content.
            EMAIL (NO PREAMBLE):
            """
        )
        chain_email = prompt_email | self.llm
        res = chain_email.invoke({"job_description": str(job), "link_list": ", ".join(links)})
        return res.content.strip()

# Debugging - Test API key presence
if __name__ == "__main__":
    api_key = os.getenv("GROQ_API_KEY")
    if api_key:
        print("✅ GROQ_API_KEY is set.")
    else:
        print("❌ GROQ_API_KEY is missing.")
