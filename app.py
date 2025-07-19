import streamlit as st
import PyPDF2
from ollama_chat import ask_ollama
from language_utils import detect_language, translate_to_english

# Function to extract text from uploaded PDF file
def extract_text_from_pdf(uploaded_file):
    pdf_reader = PyPDF2.PdfReader(uploaded_file)
    pdf_text = ""
    for page in pdf_reader.pages:
        text = page.extract_text()
        if text:
            pdf_text += text
    return pdf_text.strip()

# Streamlit app UI setup
st.set_page_config(page_title="Chat with PDF", layout="wide")
st.title("PDF Mind AI")

uploaded_file = st.file_uploader("Upload a PDF", type="pdf")
mode = st.selectbox("Choose Mode", ["Summarize", "Chat"])

# State for resetting messages if a new PDF is uploaded
if uploaded_file:
    if "last_uploaded_file_name" not in st.session_state:
        st.session_state.last_uploaded_file_name = None

    # Reset chat context when new file is uploaded
    if uploaded_file.name != st.session_state.last_uploaded_file_name:
        st.session_state.last_uploaded_file_name = uploaded_file.name
        st.session_state.messages = []  # Reset messages

    pdf_text = extract_text_from_pdf(uploaded_file)

    # Warn if PDF content is too short
    if len(pdf_text) < 200:
        st.warning("⚠️ The PDF text seems short or unclear. The model may not respond accurately.")

    st.subheader("📄 Extracted Text Preview")
    st.text_area("Raw PDF Text (preview)", value=pdf_text[:1500] + ("..." if len(pdf_text) > 1500 else ""), height=200, disabled=True)

    lang = detect_language(pdf_text)
    st.info(f"Detected Language: `{lang}`")

    translated_pdf_text = pdf_text
    if lang != "en":
        with st.spinner("Translating to English..."):
            translated_pdf_text = translate_to_english(pdf_text, src_lang=lang)
            st.success("Translation Complete")
            st.text_area("Translated PDF text", value=translated_pdf_text[:1500] + "...", height=200, disabled=True)

    # Inject PDF context into messages if not already present
    if not any("PDF Content:" in msg["content"] for msg in st.session_state.get("messages", [])):
        st.session_state.messages = [
            {"role": "system", "content": "You are a helpful assistant that answers questions based only on the following PDF content."},
            {"role": "user", "content": f"PDF Content:\n{pdf_text}"}
        ]

    # Summarize Mode
    if mode == "Summarize":
        if st.button("🔍 Summarize this PDF"):
            with st.spinner("Summarizing..."):
                prompt = f"""
You are a smart summarizer.

The user has uploaded a PDF. Based on its content, write a professional and clear summary. Avoid line-by-line repetition or raw data. Understand the intent and present it in a short paragraph.

PDF Content:
\"\"\"
{pdf_text}
\"\"\"
"""
                response = ask_ollama([{"role": "user", "content": prompt}])
                st.success("✅ Summary:")
                st.markdown(response)

    # Chat Mode
    elif mode == "Chat":
        st.subheader("💬 Ask questions about your PDF")

        with st.form(key="chat_form", clear_on_submit=True):
            user_input = st.text_input("Type your question here")
            submit_button = st.form_submit_button("Ask")

            if submit_button and user_input.strip():
                st.session_state.messages.append({"role": "user", "content": user_input.strip()})
                with st.spinner("Thinking..."):
                    response = ask_ollama(st.session_state.messages)
                    st.session_state.messages.append({"role": "assistant", "content": response})
                    st.markdown(f"**🤖:** {response}")

        if st.checkbox("📜 Show full chat history"):
            for msg in st.session_state.messages:
                role = "🧠 System" if msg["role"] == "system" else "👤 You" if msg["role"] == "user" else "🤖 Assistant"
                st.markdown(f"**{role}:** {msg['content']}")

