from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    filename: str
    file_type: str
    total_pages: int
    total_characters: int
    total_words: int
    total_chunks: int


class AnalysisResult(BaseModel):
    summary: str
    key_themes: list[str] = Field(default_factory=list)
    main_points: list[str] = Field(default_factory=list)


class DocumentAnalysisResponse(BaseModel):
    success: bool
    message: str
    metadata: DocumentMetadata
    analysis: AnalysisResult
    processing_time_seconds: float
