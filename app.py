import streamlit as st
from dotenv import load_dotenv
from rag_system.pdf_processor import load_policy_texts
from rag_system.embeddings import create_and_save_vectorstore, load_vectorstore
from rag_system.llm import get_answer
import os
import time

load_dotenv()

# Constants
COMPANY_POLICY_DIR = "policies/company"
TEAM_POLICY_BASE_DIR = "policies/teams"
VECTOR_INDEX_DIR = "vector_index/combined"

st.set_page_config(page_title="🎮 DATEV AI Dev Buddy", layout="wide", page_icon="🧑‍💻")

def process_and_index_policies(team_name=None):
    team_dir = os.path.join(TEAM_POLICY_BASE_DIR, team_name) if team_name else None
    policy_texts = load_policy_texts(company_dir=COMPANY_POLICY_DIR, team_dir=team_dir)
    if not policy_texts:
        st.warning("⚠️ No policy documents found to index.")
        return False
    create_and_save_vectorstore(policy_texts, index_dir=VECTOR_INDEX_DIR)
    return True

def show_dev_buddy(score: int):
    if score >= 90:
        message = "🎉 Amazing! Your code is 100% compliant. Keep up the stellar work! 🚀"
        img_url = "https://i.imgur.com/OYVpe2W.png"  # happy dev avatar
        banner_color = "#28a745"
        badge = "🏅 Compliance Champion"
    elif score >= 75:
        message = "👍 Good job! Just a few tweaks needed to hit perfection."
        img_url = "https://i.imgur.com/9bIebZI.png"  # encouraging dev avatar
        banner_color = "#ffc107"
        badge = "🌟 Compliance Rising Star"
    else:
        message = "⚠️ Heads up! Some compliance issues found. Let's fix them together! 💪"
        img_url = "https://i.imgur.com/8n0f4yD.png"  # concerned dev avatar
        banner_color = "#dc3545"
        badge = "⚡ Compliance Rookie"

    # Banner with avatar and message
    st.markdown(f"""
    <div style="background:{banner_color}; padding: 20px; border-radius: 15px; display: flex; align-items: center; gap: 20px;">
      <img src="{img_url}" width="100" style="border-radius: 50%; border: 3px solid white;" />
      <div style="color: white;">
        <h2 style="margin: 0;">{message}</h2>
        <h3 style="margin: 5px 0;">{badge}</h3>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Progress bar with score
    progress_color = banner_color
    progress_html = f"""
    <div style="background:#eee; border-radius:8px; padding:4px; width: 100%; max-width: 500px; margin-top: 15px;">
      <div style="background:{progress_color}; width:{score}%; height:28px; border-radius:5px; text-align:center; color:white; font-weight:bold; line-height:28px; font-size:18px;">
        Compliance Score: {score}%
      </div>
    </div>
    """
    st.markdown(progress_html, unsafe_allow_html=True)

def main():
    st.title("🧑‍💻 DATEV AI Developer Buddy Console")

    with st.expander("📄 Upload Company or Team Policy PDFs", expanded=True):
        upload_team = st.text_input("Enter team name (leave blank for company-wide upload):", "")
        uploaded_files = st.file_uploader("Upload PDF files", accept_multiple_files=True, type=["pdf"])

        if uploaded_files:
            folder = os.path.join(TEAM_POLICY_BASE_DIR, upload_team) if upload_team else COMPANY_POLICY_DIR
            os.makedirs(folder, exist_ok=True)

            progress = st.progress(0)
            for i, pdf in enumerate(uploaded_files):
                with open(os.path.join(folder, pdf.name), "wb") as f:
                    f.write(pdf.getbuffer())
                progress.progress((i + 1) / len(uploaded_files))
                time.sleep(0.1)

            st.success(f"✅ Uploaded {len(uploaded_files)} PDFs to {'team ' + upload_team if upload_team else 'company'} policies! 🎉")
            st.info("🔎 Indexing policy documents...")
            if process_and_index_policies(team_name=upload_team if upload_team else None):
                st.balloons()
                st.success("🎯 Policy documents indexed successfully!")

    with st.expander("💡 Compliance & Sustainability Checker", expanded=True):
        team_for_query = st.text_input("Enter team name for querying team-specific policies (optional):", "")
        code_snippet = st.text_area("Paste your code snippet here:", height=250)

        if st.button("🚀 Check Compliance & Sustainability"):
            if not code_snippet.strip():
                st.warning("⚠️ Please enter a code snippet to check.")
            else:
                with st.spinner("🤖 Your Dev Buddy is analyzing your code..."):
                    try:
                        vectorstore = load_vectorstore(index_dir=VECTOR_INDEX_DIR)
                        docs = vectorstore.similarity_search(code_snippet)
                        response = get_answer(docs, code_snippet)

                        # Simple heuristic for compliance scoring
                        low_keywords = ["issue", "error", "violate", "not compliant", "fix", "warning"]
                        score = 100
                        response_lower = response.lower()
                        if any(k in response_lower for k in low_keywords):
                            score = 70

                        st.subheader("✅ Compliance Suggestions")
                        st.markdown(response)

                        show_dev_buddy(score)

                        st.subheader("🌿 Sustainability Tips")
                        st.markdown("""
                        - Optimize loops and reduce nested iterations.  
                        - Avoid redundant computations.  
                        - Prefer lightweight libraries over heavy dependencies.  
                        - Cache results when possible to improve performance.
                        """)

                    except Exception as e:
                        st.error(f"⚠️ Something went wrong: {e}")

    with st.expander("📚 Automated Documentation Generator", expanded=False):
        if st.button("📄 Generate Documentation"):
            st.info("🧙‍♂️ Automagic docs coming soon! Stay tuned for Sphinx integration.")

if __name__ == "__main__":
    main()
