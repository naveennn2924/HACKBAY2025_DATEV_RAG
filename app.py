import streamlit as st
from dotenv import load_dotenv
from rag_system.pdf_processor import load_policy_texts
from rag_system.embeddings import create_and_save_vectorstore, load_vectorstore
from rag_system.llm import get_answer
import os
import time

load_dotenv()

# Folder constants
COMPANY_POLICY_DIR = "policies/company"
TEAM_POLICY_BASE_DIR = "policies/teams"
VECTOR_INDEX_BASE_DIR = "vector_index"

st.set_page_config(page_title="🎮 DATEV AI Dev Buddy", layout="wide", page_icon="🧑‍💻")

# Save uploaded PDF to folder
def save_uploaded_pdfs(uploaded_files, folder_path):
    os.makedirs(folder_path, exist_ok=True)
    for pdf in uploaded_files:
        file_path = os.path.join(folder_path, pdf.name)
        with open(file_path, "wb") as f:
            f.write(pdf.getbuffer())

# Process and index policies
def process_and_index_policies(team_name=None):
    team_name = team_name.strip() if isinstance(team_name, str) else None

    if team_name:
        pdf_folder = os.path.join(TEAM_POLICY_BASE_DIR, team_name)
        vector_index_dir = os.path.join(VECTOR_INDEX_BASE_DIR, team_name)
        company_dir = None
        team_dir = pdf_folder
    else:
        pdf_folder = COMPANY_POLICY_DIR
        vector_index_dir = os.path.join(VECTOR_INDEX_BASE_DIR, "company")
        company_dir = COMPANY_POLICY_DIR
        team_dir = None

    policy_texts = load_policy_texts(company_dir=company_dir, team_dir=team_dir)

    if not policy_texts:
        st.warning("⚠️ No policy documents found to index.")
        return False

    # Ensure team-specific vectorstore folder is created
    create_and_save_vectorstore(policy_texts, index_dir=vector_index_dir)
    return True

# Load vectorstore for team
def load_vectorstore_for_team(team_name=None):
    team_name = team_name.strip() if isinstance(team_name, str) else None

    if team_name:
        vector_index_dir = os.path.join(VECTOR_INDEX_BASE_DIR, team_name)
    else:
        vector_index_dir = os.path.join(VECTOR_INDEX_BASE_DIR, "company")

    if not os.path.exists(vector_index_dir):
        st.error(f"❌ Vectorstore index not found for {'team ' + team_name if team_name else 'company'}. Please upload and index policies first.")
        return None

    return load_vectorstore(index_dir=vector_index_dir)

# Display dynamic UI for Dev Buddy
def show_dev_buddy(score: int):
    if score >= 70:
        message = "🎉 Amazing! Your code is 100% compliant. Keep up the stellar work! 🚀"
        img_url = "https://i.imgur.com/OYVpe2W.png"
        banner_color = "#28a745"
        badge = "🏅 Compliance Champion"
    elif score >= 55:
        message = "👍 Good job! Just a few tweaks needed to hit perfection."
        img_url = "https://i.imgur.com/9bIebZI.png"
        banner_color = "#ffc107"
        badge = "🌟 Compliance Rising Star"
    else:
        message = "⚠️ Heads up! Some compliance issues found. Let's fix them together! 💪"
        img_url = "https://i.imgur.com/8n0f4yD.png"
        banner_color = "#dc3545"
        badge = "⚡ Compliance Rookie"

    # Dynamic banner with transition
    st.markdown(f"""
    <div style="background:{banner_color}; padding: 20px; border-radius: 15px; display: flex; align-items: center; gap: 20px; transition: all 0.3s ease;">
      <img src="{img_url}" width="100" style="border-radius: 50%; border: 3px solid white;" />
      <div style="color: white;">
        <h2 style="margin: 0;">{message}</h2>
        <h3 style="margin: 5px 0;">{badge}</h3>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Progress bar
    progress_html = f"""
    <div style="background:#eee; border-radius:8px; padding:4px; width: 100%; max-width: 500px; margin-top: 15px;">
      <div style="background:{banner_color}; width:{score}%; height:28px; border-radius:5px; text-align:center; color:white; font-weight:bold; line-height:28px; font-size:18px;">
        Compliance Score: {score}%
      </div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

# Main interface
def main():
    st.title("🧑‍💻 DATEV Developer Buddy Console")

    # Upload section with dynamic progress
    with st.expander("📄 Upload Company or Team Policy PDFs", expanded=True):
        upload_team = st.text_input("Enter team name ")
        uploaded_files = st.file_uploader("Upload PDF files", accept_multiple_files=True, type=["pdf"])

        if uploaded_files:
            folder = (
                os.path.join(TEAM_POLICY_BASE_DIR, upload_team.strip())
                if upload_team.strip()
                else COMPANY_POLICY_DIR
            )
            save_uploaded_pdfs(uploaded_files, folder)

            st.success(f"✅ Uploaded {len(uploaded_files)} PDFs to {'team ' + upload_team if upload_team else 'company'} policies! 🎉")
            st.info("🔎 Indexing policy documents...")

            # Display progress while indexing
            with st.spinner("Indexing... please wait"):
                if process_and_index_policies(team_name=upload_team):
                    st.balloons()
                    st.success(f"🎯 Policy documents indexed successfully for {'team ' + upload_team if upload_team else 'company'}!")

    # Compliance checker with real-time feedback
    with st.expander("💡 Compliance Checker", expanded=True):
        query_team = st.text_input("Enter team name for querying team-specific policies (optional):", "")
        code_snippet = st.text_area("Paste your code snippet here:", height=250)

        if st.button("🚀 Check"):
            if not code_snippet.strip():
                st.warning("⚠️ Please enter a code snippet to check.")
            else:
                with st.spinner("🤖 Your Dev Buddy is analyzing your code..."):
                    vectorstore = load_vectorstore_for_team(query_team)
                    if vectorstore is None:
                        return

                    docs = vectorstore.similarity_search(code_snippet)
                    response = get_answer(docs, code_snippet)

                    low_keywords = ["issue", "error", "violate", "not compliant", "fix", "warning"]
                    score = 100
                    if any(k in response.lower() for k in low_keywords):
                        score = 70

                    st.subheader("✅ Compliance Suggestions")
                    st.markdown(response)

                  


if __name__ == "__main__":
    main()
