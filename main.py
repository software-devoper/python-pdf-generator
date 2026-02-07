from fastapi import FastAPI
from pydantic import BaseModel
from weasyprint import HTML
from supabase import create_client
import uuid
import os

app = FastAPI()

# ENV VARIABLES (will be set during deploy)
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

class PDFRequest(BaseModel):
    html: str
    filename: str | None = "document.pdf"

@app.post("/generate-pdf")
def generate_pdf(data: PDFRequest):
    file_id = str(uuid.uuid4())
    pdf_path = f"/tmp/{file_id}.pdf"

    # Generate PDF from HTML
    HTML(string=data.html).write_pdf(pdf_path)

    # Upload to Supabase Storage
    with open(pdf_path, "rb") as f:
        supabase.storage.from_("pdfs").upload(
            path=f"{file_id}.pdf",
            file=f,
            file_options={"content-type": "application/pdf"}
        )

    # Public download link
    public_url = supabase.storage.from_("pdfs").get_public_url(f"{file_id}.pdf")

    return {
        "success": True,
        "download_url": public_url
    }
