"""LangGraph workflow for document analysis."""

import re
import asyncio
from typing import Optional, TypedDict

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

from config import get_settings
from prompts import CHUNK_SUMMARY_PROMPT, SYNTHESIS_PROMPT, SYNTHESIS_USER_TEMPLATE


class AnalysisState(TypedDict):
    """State for the analysis workflow."""
    chunks: list[str]
    chunk_summaries: list[str]
    final_analysis: dict
    metadata: dict
    error: Optional[str]


def create_llm():
    """Create Groq LLM instance."""
    settings = get_settings()
    return ChatGroq(
        api_key=settings.groq_api_key,
        model_name=settings.groq_model,
        temperature=0.1,
        max_tokens=1024,
    )


async def summarize_chunks_node(state: AnalysisState) -> AnalysisState:
    """Summarize all chunks into brief summaries for synthesis."""
    llm = create_llm()
    chunks = state["chunks"]

    prompt = ChatPromptTemplate.from_messages([
        ("system", CHUNK_SUMMARY_PROMPT),
        ("human", "{text}")
    ])
    chain = prompt | llm

    batch_size = 5
    summaries = []

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        tasks = [chain.ainvoke({"text": chunk}) for chunk in batch]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            if isinstance(r, Exception):
                summaries.append("")
            else:
                summaries.append(r.content)

    return {**state, "chunk_summaries": summaries}


async def synthesize_analysis_node(state: AnalysisState) -> AnalysisState:
    """Synthesize all summaries into final document analysis."""
    llm = create_llm()
    summaries = state["chunk_summaries"]
    metadata = state["metadata"]

    combined_summaries = "\n\n".join(f"- {s}" for s in summaries if s)

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYNTHESIS_PROMPT),
        ("human", SYNTHESIS_USER_TEMPLATE)
    ])

    chain = prompt | llm

    try:
        response = await chain.ainvoke({
            "filename": metadata.get("filename", "Unknown"),
            "pages": metadata.get("total_pages", 0),
            "summaries": combined_summaries,
        })

        analysis = parse_analysis_response(response.content)
        return {**state, "final_analysis": analysis}
    except Exception as e:
        return {**state, "error": str(e), "final_analysis": {
            "summary": "Error generating analysis",
            "key_themes": [],
            "main_points": []
        }}


def parse_analysis_response(content: str) -> dict:
    """Parse the structured analysis response."""
    result = {
        "summary": "",
        "key_themes": [],
        "main_points": []
    }

    # Extract summary
    summary_match = re.search(r"SUMMARY:\s*\n(.*?)(?=\n\s*KEY THEMES:|$)", content, re.DOTALL | re.IGNORECASE)
    if summary_match:
        result["summary"] = summary_match.group(1).strip()

    # Extract key themes
    themes_match = re.search(r"KEY THEMES:\s*\n(.*?)(?=\n\s*MAIN POINTS:|$)", content, re.DOTALL | re.IGNORECASE)
    if themes_match:
        result["key_themes"] = [line.strip().lstrip("- •") for line in themes_match.group(1).strip().split("\n") if line.strip().lstrip("- •")]

    # Extract main points
    points_match = re.search(r"MAIN POINTS:\s*\n(.*?)(?=$)", content, re.DOTALL | re.IGNORECASE)
    if points_match:
        result["main_points"] = [line.strip().lstrip("- •") for line in points_match.group(1).strip().split("\n") if line.strip().lstrip("- •")]

    return result


def create_workflow() -> StateGraph:
    workflow = StateGraph(AnalysisState)

    workflow.add_node("summarize_chunks", summarize_chunks_node)
    workflow.add_node("synthesize", synthesize_analysis_node)

    workflow.set_entry_point("summarize_chunks")
    workflow.add_edge("summarize_chunks", "synthesize")
    workflow.add_edge("synthesize", END)

    return workflow.compile()


async def run_analysis(chunks: list[str], metadata: dict) -> dict:
    """Run the complete analysis workflow."""
    workflow = create_workflow()

    initial_state: AnalysisState = {
        "chunks": chunks,
        "chunk_summaries": [],
        "final_analysis": {},
        "metadata": metadata,
        "error": None,
    }

    result = await workflow.ainvoke(initial_state)
    return result["final_analysis"]
