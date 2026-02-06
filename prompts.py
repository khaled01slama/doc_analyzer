"""Prompts for document analysis."""

CHUNK_SUMMARY_PROMPT = "Summarize this text in 2-3 sentences, capturing the main points:"

SYNTHESIS_PROMPT = """You are an expert document analyst. Based on the section summaries below, provide a comprehensive analysis of the entire document.

Return your analysis in this exact format (use these exact headers):

SUMMARY:
[A comprehensive 4-6 sentence summary of the entire document]

KEY THEMES:
- [Theme 1]
- [Theme 2]
- [Theme 3]
- [Add more as needed]

MAIN POINTS:
- [Main point 1]
- [Main point 2]
- [Main point 3]
- [Add more as needed]"""

SYNTHESIS_USER_TEMPLATE = """Document: {filename}
Pages: {pages}

Section Summaries:
{summaries}

Provide your comprehensive analysis:"""
