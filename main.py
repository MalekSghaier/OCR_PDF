from fastapi import FastAPI, UploadFile, File
from pdf2image import convert_from_path
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi import Request
import pytesseract
from PIL import Image
import os
import re

app = FastAPI()
templates = Jinja2Templates(directory="templates")

UPLOAD_FOLDER = "uploads"

# Spécifique Windows
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload-pdf/")
async def upload_pdf(file: UploadFile = File(...)):

    file_path = os.path.join(UPLOAD_FOLDER, file.filename)

    # Sauvegarde du PDF
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Conversion PDF -> images
    images = convert_from_path(
        file_path,
        dpi=300, 
        poppler_path=r"C:\poppler\Library\bin"
    )

    full_text = ""

    for image in images:

      # Convertir en niveaux de gris
      image = image.convert("L")

      # OCR avec configuration améliorée
      text = pytesseract.image_to_string(
          image,
          lang="eng+fra+ara",
          config="--oem 3 --psm 6"
      )

      full_text += text + "\n"

    # Exemple extraction Email
    emails = re.findall(
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
        full_text
    )

    # Exemple extraction date
    dates = re.findall(
        r"\d{2}/\d{2}/\d{4}",
        full_text
    )

    return {
        "text": full_text,
        "emails_found": emails,
        "dates_found": dates
    }