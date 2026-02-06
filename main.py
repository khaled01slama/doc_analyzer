"""Document Analysis API - FastAPI application."""

import time
from fastapi import FastAPI, UploadFile, File, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from config import get_settings
from models import DocumentMetadata, AnalysisResult, DocumentAnalysisResponse
from parser import parse_document
from chunker import chunk_document
from workflow import run_analysis
import uvicorn


app = FastAPI(
    title="Document Analysis API",
    description="Analyze PDF and Word documents using AI",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
async def health():
    """Health check endpoint."""
    settings = get_settings()
    return {"status": "healthy", "model": settings.groq_model}


@app.post("/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document_endpoint(
    file: UploadFile = File(..., description="PDF or Word document"),
    chunk_size: int = Query(2000, ge=500, le=5000, description="Chunk size"),
):
    """
    Analyze a document and return a comprehensive summary.
    Supports PDF (.pdf) and Word (.docx) documents.
    """
    start_time = time.time()
    settings = get_settings()

    filename = file.filename or "document"
    extension = filename.split(".")[-1].lower()

    if extension not in ["pdf", "docx", "doc"]:
        raise HTTPException(400, f"Unsupported file type: {extension}")

    content = await file.read()
    file_size_mb = len(content) / (1024 * 1024)

    if file_size_mb > settings.max_file_size_mb:
        raise HTTPException(400, f"File too large: {file_size_mb:.1f}MB (max: {settings.max_file_size_mb}MB)")

    try:
        text, page_count = await parse_document(content, filename)
    except Exception as e:
        raise HTTPException(500, f"Error parsing document: {str(e)}")

    if not text.strip():
        raise HTTPException(400, "No text content found in document")

    words = text.split()
    metadata = {
        "filename": filename,
        "file_type": extension,
        "total_pages": page_count,
        "total_characters": len(text),
        "total_words": len(words),
    }

    chunks = chunk_document(text, chunk_size, settings.chunk_overlap)
    metadata["total_chunks"] = len(chunks)

    try:
        analysis = await run_analysis(chunks, metadata)
    except Exception as e:
        raise HTTPException(500, f"Error during analysis: {str(e)}")

    processing_time = time.time() - start_time

    return DocumentAnalysisResponse(
        success=True,
        message="Document analyzed successfully",
        metadata=DocumentMetadata(**metadata),
        analysis=AnalysisResult(**analysis),
        processing_time_seconds=round(processing_time, 2),
    )


@app.get("/")
async def root():
    return {"message": "Document Analysis API", "docs": "/docs"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
