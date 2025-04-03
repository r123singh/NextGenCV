import streamlit as st
from templates import template
import pdfplumber
import openai
import os
from dotenv import load_dotenv
import uuid
from storage import StorageHandler
from config import RESUME_VIEWER_URL, IS_PRODUCTION
import docx

load_dotenv()

resume_text = None
st.set_page_config(layout="wide")
storage_handler = StorageHandler()

def tmp_store(updated_resume_md):
    unique_filename = f'{str(uuid.uuid4())}.md'
    return storage_handler.store_file(updated_resume_md, unique_filename)

def chat_screen():
    global resume_text
    openai.api_key = os.getenv("OPENAI_API_KEY")
    st.title("ResuMaxAI 🤖")
    
    # Initialize session state for messages and filenames if not exists
    if "messages" not in st.session_state:
        st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

    st.sidebar.markdown("""
    <style>
    .sidebar-expanded {
        display: block;
        background-color: #f0f0f0;
        font-size: 1.5rem;
        font-weight: bold;
        color: #000000;
        padding: 10px;
        border-radius: 10px;
        border: 1px solid #000000;
    }
    </style>
    """, unsafe_allow_html=True)
    
    uploaded_resume = st.sidebar.file_uploader("Resume file", type=["pdf", "docx", "doc", "txt"])
    linkedin = st.sidebar.text_input("LinkedIn URL", placeholder="https://www.linkedin.com/in/john-doe", value="https://www.linkedin.com/in/john-doe")
    github = st.sidebar.text_input("GitHub URL", placeholder="https://github.com/john-doe", value="https://github.com/john-doe")
    selected_model = st.sidebar.selectbox("Select Model", ["gpt-4o-mini", "gpt-4o", "gpt-3.5-turbo", "claude 3.5 sonnet","claude 3 haiku", "gemini 1.5 flash", "gemini 1.5 pro"])

    def enhance_resume(resume_txt, job_requirements):
        prompt = f"""
        Role:
        You are a highly skilled resume expert specializing in enhancing and tailoring resumes to align with specific job requirements. Your expertise lies in refining resumes to highlight the most relevant skills, achievements, and experiences, ensuring they align with the target role's expectations. Only return the required resume markdown content, nothing else. Don't add any explanation or comments.

        Task:
        You will be provided with:
        - An existing resume.
        - A set of job requirements for a specific role.
        - Your goal is to generate a refined resume in Markdown format as per output format.

        Enhancements to Apply:
            - Alignment with Job Requirements: Modify and emphasize skills, experiences, and accomplishments that best match the job description.
            - Bullet Points for Impact: Ensure each work experience entry contains exactly five compelling bullet points, highlighting key contributions and quantifiable achievements.
            - Invented/Expanded Content: If necessary, infer or creatively enhance project descriptions, job tasks, or impact statements to better fit the target role.
            - Consistency & Readability: Maintain professional formatting, clarity, and readability. Ensure the resume is concise yet detailed.
            - Additional Sections: Include LinkedIn URL: {linkedin} and GitHub URL: {github} if applicable or available, ensuring a comprehensive and well-rounded professional profile.
            - Output Format: The final output must be structured in Markdown format as per {template}.
        """
        try: 
            response = openai.chat.completions.create(
                model="gpt-4o-mini",
                temperature=0,
                messages=[
                    {
                        "role": "system",
                        "content": prompt
                    },
                    {
                        "role": "user",
                        "content": f"Create a new resume using the provided resume data: {resume_txt}. Here is the job description to tailor the resume to: {job_requirements}."
                    }
                ]
            )
        except Exception as e:
            st.error(f"INVALID MODEL SELECTED" + str(e))
            st.chat_message("assistant").code("Please select a valid model.")
            return
        
        updated_resume = response.choices[0].message.content
        
        # Store the resume and create download link
        filename = tmp_store(updated_resume)
        
        if filename:
            file_url = storage_handler.get_file_url(filename)
            with st.chat_message("assistant"):
                st.code(updated_resume)
                st.markdown(f"""
                    <div style='text-align: right; margin-top: 10px;'>
                        <a href='{RESUME_VIEWER_URL}?url={file_url}' target='_blank' 
                           style='text-decoration: none; color: #0066cc; display: inline-flex; align-items: center; gap: 5px;'>
                            Download Resume 
                            <i class='fas fa-download' style='font-size: 16px;'></i>
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
        
        # Add messages and filename to session state
        st.session_state.messages.append(
            {
                "role": "user",
                "content": job_requirements
            }
        )
        st.session_state.messages.append(
            {
                "role": "assistant",
                "content": updated_resume,
                "filename": filename if filename else None
            }
        )

    # Add Font Awesome CDN for the download icon
    st.markdown("""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
    """, unsafe_allow_html=True)

    if uploaded_resume:
        if resume_text is None:
            if uploaded_resume.type == "application/pdf":
                with pdfplumber.open(uploaded_resume) as pdf:
                    resume_text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
            elif uploaded_resume.type == "application/vnd.openxmlformats-officedocument.wordprocessingml.document":
                doc = docx.Document(uploaded_resume)
                resume_text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
            elif uploaded_resume.type == "text/plain":
                resume_text = uploaded_resume.read().decode("utf-8")
    else:
        st.warning("Hello! :wave: Please upload a resume to get started.")

    # Display existing messages with their download links
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            if msg["role"] == "assistant" and "filename" in msg and msg["filename"]:
                st.code(msg["content"])
                file_url = storage_handler.get_file_url(msg["filename"])
                st.markdown(f"""
                    <div style='text-align: right; margin-top: 10px;'>
                        <a href='{RESUME_VIEWER_URL}?url={file_url}' target='_blank' 
                           style='text-decoration: none; color: #0066cc; display: inline-flex; align-items: center; gap: 5px;'>
                            Download Resume 
                            <i class='fas fa-download' style='font-size: 16px;'></i>
                        </a>
                    </div>
                    """, unsafe_allow_html=True)
            elif msg["role"] == "assistant":
                if msg["content"].startswith("How can I help you?"):
                    st.markdown(msg["content"])
                else:
                    st.code(msg["content"])
            else:
                st.markdown(msg["content"])
                
    user_input = st.chat_input("Message Resume-GPT your job description")

    if user_input and resume_text:
        st.chat_message("user").markdown(user_input)
        enhance_resume(resume_text, user_input)

if __name__ == "__main__":
    chat_screen()