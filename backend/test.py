from backend.utils.pdf_loader_tool import load_pdf_text

resume_text = load_pdf_text("data/sample.pdf")
print(resume_text)
