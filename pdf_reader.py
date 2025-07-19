import PyPDF2

def extract_text_from_pdf(file):
    doc = PyPDF2.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    return text