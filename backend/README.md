# OpenSAGE backend

LangGraph/FastAPI reference implementation for the OpenSAGE research workflow.

## Configuration

Copy `.env.example` to `.env` and add credentials you control. `.env` is ignored by Git.

- `ZZZ_API_KEY` or `OPENAI_API_KEY`: key for an OpenAI-compatible chat endpoint.
- `ZZZ_BASE_URL` or `OPENAI_BASE_URL`: optional compatible endpoint base URL.
- `TAVILY_API_KEY`: Tavily search key.
- `QUERY_GENERATOR_MODEL`, `REFLECTION_MODEL`, `ANSWER_MODEL`: model labels.
- `NUMBER_OF_INITIAL_QUERIES`, `MAX_RESEARCH_LOOPS`: workflow budgets.

The module can be imported without credentials; missing keys are reported only when the corresponding model/search call is attempted. The historical labels and web index are not guaranteed to remain available, so current execution is a reference implementation rather than bit-for-bit replay of April 2026 retrievals.

The retained template-derived backend component is licensed under `backend/LICENSE` (MIT). Project-level notices are in `../THIRD_PARTY_NOTICES.md`.
