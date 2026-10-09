"""Run the Phase 7 shopping workflow using the LLM settings from .env.

Expected recommendation shape:
{
  "recommended_product": {"id": "...", "model_name": "...", "...": "..."},
  "reason": "...",
  "alternatives": [{"id": "...", "model_name": "...", "...": "..."}]
}
"""

import json

from app.graph.shopping_graph import run_shopping_workflow

EXAMPLE_QUERY = (
    "I need a laptop under 60000 for Python programming and machine learning basics "
    "with 16GB RAM"
)


def main() -> None:
    state = run_shopping_workflow(EXAMPLE_QUERY)
    print(json.dumps(state["recommendation"], indent=2, ensure_ascii=True))


if __name__ == "__main__":
    main()
