"""LangGraph research agent implemented with OpenAI-compatible chat APIs."""

import json
import os
import re
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from langchain_core.messages import AIMessage
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.runnables import RunnableConfig
from langchain_openai import ChatOpenAI
from langgraph.graph import END, START, StateGraph
from langgraph.types import Send

from agent.configuration import Configuration
from agent.prompts import (
    answer_instructions,
    get_current_date,
    query_writer_instructions,
    reflection_instructions,
    web_searcher_instructions,
)
from agent.state import (
    OverallState,
    QueryGenerationState,
    ReflectionState,
    WebSearchState,
)
from agent.tools_and_schemas import Reflection, SearchQueryList
from agent.utils import (
    get_research_topic,
)

load_dotenv(Path(__file__).resolve().parents[2] / ".env")

_openai_api_key = os.getenv("ZZZ_API_KEY") or os.getenv("OPENAI_API_KEY")
_openai_base_url = os.getenv("ZZZ_BASE_URL") or os.getenv("OPENAI_BASE_URL")
_tavily_api_key = os.getenv("TAVILY_API_KEY")
_tavily_search_url = "https://api.tavily.com/search"


def _requires_responses_api(model: str | None) -> bool:
    """Return whether a model is only available through the Responses API."""
    return bool(model and "deep-research" in model)


def _openai_llm(**kwargs):
    """Build an OpenAI-compatible chat model client."""
    if not _openai_api_key:
        raise ValueError(
            "ZZZ_API_KEY or OPENAI_API_KEY is not set. "
            "Copy backend/.env.example to backend/.env and add your own key."
        )
    if _requires_responses_api(kwargs.get("model")):
        kwargs["use_responses_api"] = True
        kwargs["disable_streaming"] = True
        kwargs.pop("temperature", None)
        model_kwargs = dict(kwargs.pop("model_kwargs", {}) or {})
        model_kwargs.setdefault("tools", [{"type": "web_search_preview"}])
        kwargs["model_kwargs"] = model_kwargs

    return ChatOpenAI(
        api_key=_openai_api_key,
        base_url=_openai_base_url,
        **kwargs,
    )


def _tavily_search(query: str, *, max_results: int = 8) -> dict:
    """Search the web with Tavily and return the parsed response."""
    if not _tavily_api_key:
        raise ValueError("TAVILY_API_KEY is not set")

    payload = {
        "api_key": _tavily_api_key,
        "query": query,
        "search_depth": "advanced",
        "include_answer": True,
        "include_raw_content": False,
        "max_results": max_results,
    }
    request = Request(
        _tavily_search_url,
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urlopen(request, timeout=60) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Tavily search failed: {exc.code} {body}") from exc
    except URLError as exc:
        raise RuntimeError(f"Tavily search failed: {exc.reason}") from exc


def _format_tavily_results(search_response: dict) -> str:
    """Format Tavily results as grounded context for the synthesis model."""
    parts = []
    answer = search_response.get("answer")
    if answer:
        parts.append(f"Tavily answer summary:\n{answer}")

    results = search_response.get("results") or []
    for idx, result in enumerate(results, start=1):
        title = result.get("title") or "Untitled source"
        url = result.get("url") or ""
        content = result.get("content") or ""
        score = result.get("score")
        score_text = f"\nRelevance score: {score}" if score is not None else ""
        parts.append(
            f"Source {idx}: [{title}]({url}){score_text}\nSnippet:\n{content}"
        )

    return "\n\n---\n\n".join(parts)


def _tavily_sources(search_response: dict) -> list[dict[str, str]]:
    """Convert Tavily results into the source shape expected by the UI."""
    sources = {}
    for result in search_response.get("results") or []:
        url = result.get("url")
        if not url:
            continue
        sources.setdefault(
            url,
            {
                "label": result.get("title") or url,
                "short_url": url,
                "value": url,
            },
        )
    return list(sources.values())


def _message_text(message) -> str:
    """Extract plain text from chat-completions or Responses API messages."""
    text = getattr(message, "text", None)
    if isinstance(text, str):
        return text
    content = getattr(message, "content", message)
    return content if isinstance(content, str) else str(content)


def _invoke_json(llm, prompt: str, schema):
    parser = JsonOutputParser(pydantic_object=schema)
    return schema.model_validate(parser.invoke(_message_text(llm.invoke(prompt))))


def _extract_markdown_sources(text: str) -> list[dict[str, str]]:
    """Extract markdown links so the UI can still display gathered sources."""
    sources = {}
    for label, url in re.findall(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", text):
        sources.setdefault(
            url,
            {
                "label": label,
                "short_url": url,
                "value": url,
            },
        )
    return list(sources.values())


# Nodes
def generate_query(state: OverallState, config: RunnableConfig) -> QueryGenerationState:
    """LangGraph node that generates search queries based on the User's question.

    Uses an OpenAI-compatible chat model to create optimized search queries based on
    the User's question.

    Args:
        state: Current graph state containing the User's question
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated queries
    """
    configurable = Configuration.from_runnable_config(config)

    # check for custom initial search query count
    if state.get("initial_search_query_count") is None:
        state["initial_search_query_count"] = configurable.number_of_initial_queries

    llm = _openai_llm(
        model=configurable.query_generator_model,
        temperature=1.0,
        max_retries=2,
    )

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = query_writer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        number_queries=state["initial_search_query_count"],
    )
    # Generate the search queries
    result = _invoke_json(llm, formatted_prompt, SearchQueryList)
    return {"search_query": result.query}


def continue_to_web_research(state: QueryGenerationState):
    """LangGraph node that sends the search queries to the web research node.

    This is used to spawn n number of web research nodes, one for each search query.
    """
    return [
        Send("web_research", {"search_query": search_query, "id": int(idx)})
        for idx, search_query in enumerate(state["search_query"])
    ]


def web_research(state: WebSearchState, config: RunnableConfig) -> OverallState:
    """LangGraph node that performs web research with Tavily.

    Tavily retrieves sources, then the configured model synthesizes those sources
    into the summary format used by the rest of the graph.

    Args:
        state: Current graph state containing the search query and research loop count
        config: Configuration for the runnable, including search API settings

    Returns:
        Dictionary with state update, including sources_gathered, research_loop_count, and web_research_results
    """
    # Configure
    configurable = Configuration.from_runnable_config(config)
    formatted_prompt = web_searcher_instructions.format(
        current_date=get_current_date(),
        research_topic=state["search_query"],
    )
    tavily_response = _tavily_search(state["search_query"])
    tavily_context = _format_tavily_results(tavily_response)
    formatted_prompt = f"""{formatted_prompt}

Use the Tavily search results below as the source material for this research step.
Base the summary only on these results. Cite sources using the provided markdown links.

Tavily search results:
{tavily_context}
"""

    llm = _openai_llm(
        model=configurable.query_generator_model,
        temperature=0,
        max_retries=2,
    )
    response = llm.invoke(formatted_prompt)
    modified_text = _message_text(response)
    sources_gathered = _tavily_sources(tavily_response)

    return {
        "sources_gathered": sources_gathered,
        "search_query": [state["search_query"]],
        "web_research_result": [modified_text],
    }


def reflection(state: OverallState, config: RunnableConfig) -> ReflectionState:
    """LangGraph node that identifies knowledge gaps and generates potential follow-up queries.

    Analyzes the current summary to identify areas for further research and generates
    potential follow-up queries. Uses structured output to extract
    the follow-up query in JSON format.

    Args:
        state: Current graph state containing the running summary and research topic
        config: Configuration for the runnable, including LLM provider settings

    Returns:
        Dictionary with state update, including search_query key containing the generated follow-up query
    """
    configurable = Configuration.from_runnable_config(config)
    # Increment the research loop count and get the reasoning model
    state["research_loop_count"] = state.get("research_loop_count", 0) + 1
    reasoning_model = state.get("reasoning_model", configurable.reflection_model)

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = reflection_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n\n---\n\n".join(state["web_research_result"]),
    )
    # init Reasoning Model
    llm = _openai_llm(
        model=reasoning_model,
        temperature=1.0,
        max_retries=2,
    )
    result = _invoke_json(llm, formatted_prompt, Reflection)

    return {
        "is_sufficient": result.is_sufficient,
        "knowledge_gap": result.knowledge_gap,
        "follow_up_queries": result.follow_up_queries,
        "research_loop_count": state["research_loop_count"],
        "number_of_ran_queries": len(state["search_query"]),
    }


def evaluate_research(
    state: ReflectionState,
    config: RunnableConfig,
) -> OverallState:
    """LangGraph routing function that determines the next step in the research flow.

    Controls the research loop by deciding whether to continue gathering information
    or to finalize the summary based on the configured maximum number of research loops.

    Args:
        state: Current graph state containing the research loop count
        config: Configuration for the runnable, including max_research_loops setting

    Returns:
        String literal indicating the next node to visit ("web_research" or "finalize_summary")
    """
    configurable = Configuration.from_runnable_config(config)
    max_research_loops = (
        state.get("max_research_loops")
        if state.get("max_research_loops") is not None
        else configurable.max_research_loops
    )
    if state["is_sufficient"] or state["research_loop_count"] >= max_research_loops:
        return "finalize_answer"
    else:
        return [
            Send(
                "web_research",
                {
                    "search_query": follow_up_query,
                    "id": state["number_of_ran_queries"] + int(idx),
                },
            )
            for idx, follow_up_query in enumerate(state["follow_up_queries"])
        ]


def finalize_answer(state: OverallState, config: RunnableConfig):
    """LangGraph node that finalizes the research summary.

    Prepares the final output by deduplicating and formatting sources, then
    combining them with the running summary to create a well-structured
    research report with proper citations.

    Args:
        state: Current graph state containing the running summary and sources gathered

    Returns:
        Dictionary with state update, including running_summary key containing the formatted final summary with sources
    """
    configurable = Configuration.from_runnable_config(config)
    reasoning_model = state.get("reasoning_model") or configurable.answer_model

    # Format the prompt
    current_date = get_current_date()
    formatted_prompt = answer_instructions.format(
        current_date=current_date,
        research_topic=get_research_topic(state["messages"]),
        summaries="\n---\n\n".join(state["web_research_result"]),
    )

    # init Reasoning Model
    llm = _openai_llm(
        model=reasoning_model,
        temperature=0,
        max_retries=2,
    )
    result = llm.invoke(formatted_prompt)
    result_content = _message_text(result)

    # Replace the short urls with the original urls and add all used urls to the sources_gathered
    unique_sources = []
    for source in state["sources_gathered"]:
        if source["short_url"] in result_content:
            result_content = result_content.replace(
                source["short_url"], source["value"]
            )
            unique_sources.append(source)

    return {
        "messages": [AIMessage(content=result_content)],
        "sources_gathered": unique_sources,
    }


# Create our Agent Graph
builder = StateGraph(OverallState, config_schema=Configuration)

# Define the nodes we will cycle between
builder.add_node("generate_query", generate_query)
builder.add_node("web_research", web_research)
builder.add_node("reflection", reflection)
builder.add_node("finalize_answer", finalize_answer)

# Set the entrypoint as `generate_query`
# This means that this node is the first one called
builder.add_edge(START, "generate_query")
# Add conditional edge to continue with search queries in a parallel branch
builder.add_conditional_edges(
    "generate_query", continue_to_web_research, ["web_research"]
)
# Reflect on the web research
builder.add_edge("web_research", "reflection")
# Evaluate the research
builder.add_conditional_edges(
    "reflection", evaluate_research, ["web_research", "finalize_answer"]
)
# Finalize the answer
builder.add_edge("finalize_answer", END)

graph = builder.compile(name="pro-search-agent")
