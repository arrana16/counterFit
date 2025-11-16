import asyncio
import logging
import os
from typing import Any, Dict

logger = logging.getLogger(__name__)


LISTINGS: Dict[str, Dict[str, Any]] = {
    "demo-item-1": {
        "official_description": (
            "Official archive tote bag made from certified organic cotton "
            "with hand-stitched leather trim and serialized hologram tag."
        ),
        "seller": {
            "description": (
                "Vintage tote picked up in SoHo years ago. Some fraying but totally "
                "authentic. Comes with dust bag, but I misplaced the hologram tag."
            )
        },
    }
}


async def call_llm(prompt: str) -> str:
    """Call an LLM provider (mocked for now)."""

    api_key = os.getenv("OPENAI_API_KEY")
    provider = "OpenAI"
    if not api_key:
        api_key = os.getenv("OPENROUTER_API_KEY")
        provider = "OpenRouter"

    if not api_key:
        await asyncio.sleep(0)
        return (
            "Mock Analyst Review: seller mentions missing hologram tag, which is a red "
            "flag for this model. Request proof of purchase and inspect stitching."
        )

    try:
        await asyncio.sleep(0)
        logger.info(
            "Mocking %s LLM call (prompt length=%s)", provider, len(prompt)
        )
        return (
            f"[Mocked {provider} response] The seller's narrative conflicts with the "
            "official materials list. Verify hologram tag authenticity and leather "
            "stitching before proceeding."
        )
    except Exception as exc:  # pragma: no cover - fallback safeguard
        logger.exception("LLM call failed: %s", exc)
        return (
            "Analyst unavailable due to upstream error. Please re-run the evaluation."
        )


async def analyst_agent(listing: Dict[str, Any]) -> str:
    official_description = listing.get("official_description", "").strip()
    seller_description = listing.get("seller", {}).get("description", "").strip()
    prompt = (
        "You are The Analyst, the first evaluator agent in a fashion resale "
        "negotiation simulator. Highlight authenticity red flags, inconsistencies, "
        "and risk signals in a concise paragraph.\n\n"
        f"Official description:\n{official_description or 'N/A'}\n\n"
        f"Seller description:\n{seller_description or 'N/A'}\n\n"
        "Produce a short summary focused on issues the negotiation team should "
        "investigate next."
    )
    return await call_llm(prompt)
