import os
import uuid

from fastapi import FastAPI, UploadFile, File, Form
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from inference import TinyChartInference
from fastapi.staticfiles import StaticFiles


app = FastAPI(title="TinyChart IndoChartQA API")
app.mount("/static", StaticFiles(directory="static"), name="static")

# ============================================================
# Configuration
# ============================================================

UPLOAD_FOLDER = "static/uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

USE_MODEL = True

# ============================================================
# Load model
# ============================================================

if USE_MODEL:
    model = TinyChartInference()


# ============================================================
# CORS
# ============================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ============================================================
# Frontend
# ============================================================

@app.get("/")
async def home():
    return FileResponse("templates/index.html")


# ============================================================
# Prediction API
# ============================================================
@app.post("/predict")
async def predict(
    image: UploadFile = File(...),
    question: str = Form(...)
):
    filename = f"{uuid.uuid4().hex}.png"
    image_path = os.path.join(UPLOAD_FOLDER, filename)

    with open(image_path, "wb") as buffer:
        buffer.write(await image.read())

    result = model.predict(
        image_path,
        question
    )

    return result
