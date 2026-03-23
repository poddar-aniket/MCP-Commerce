import os
import json
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import ServerError, ClientError
from core.models import ParsedQuery

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class LLMAdapter:
    """
    Gemini-based LLM adapter (production-hardened).
    Plans tool execution for MCP.
    """

    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise RuntimeError("GOOGLE_API_KEY not found in environment")

        self.client = genai.Client(api_key=api_key)

        # Primary + fallback models
        self.models = [
            "gemini-2.5-flash",
            "gemini-1.5-flash",
        ]

    def analyze_user_intent(self, user_input: str, history: list = None) -> ParsedQuery:
        history = history or []
        history_context = ""
        if history:
            formatted_history = "\n".join([f"{msg.get('role', 'user').capitalize()}: {msg.get('content', '')}" for msg in history[-5:]])
            history_context = f"\nHere is the recent conversation history: {formatted_history}.\nCRITICAL RULE: You must perform Coreference Resolution. If the user's current message uses pronouns (it, them) or adjectives (cheaper ones, better ones), you MUST look at the history to determine what product they mean. Your `search_query` must ALWAYS be the actual product name (e.g., 'iphone 17'), NEVER the adjective ('cheaper'). Update the `max_price` based on their request for cheaper items, but keep the core product name intact.\n"

        prompt = f"""You are an expert E-Commerce Query Analyzer. Your job is to read the user's conversational message and extract the core shopping intent. 
Rule 1: Provide a brief 1-sentence reasoning of what the user wants.
Rule 2: Extract a BROAD, generic `search_query` of 1 to 3 words max. Strip all conversational filler and price constraints.
Rule 3: Extract min and max prices as floats if mentioned.
Rule 4: Determine the condition. If they ask for used/second-hand, set to 'refurbished'. If 'any', set to 'any'. Otherwise, default to 'new'.
Rule 5: Provide a brief, proactive shopping suggestion (1-2 sentences) based on their budget and requested item.
{history_context}
User input:
"{user_input}"
"""

        try:
            response = self.client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=ParsedQuery,
                ),
            )
            raw_text = (response.text or "").strip()
            parsed_dict = json.loads(raw_text)
            return ParsedQuery.model_validate(parsed_dict)
        except Exception as e:
            logger.error("Failed to analyze user intent: %s", str(e))
            # Fallback
            return ParsedQuery(
                reasoning="Fallback due to LLM error.",
                search_query=str(user_input)[:50],
                condition="new",
            )

    def _extract_text(self, user_input):
        """
        Normalize input into plain text.
        Accepts raw string or structured_query dict.
        """
        if isinstance(user_input, dict):
            return (
                user_input.get("reference_product")
                or user_input.get("raw_query")
                or ""
            )
        return user_input or ""

    def decide_tool_sequence(self, user_input, tools: dict, history: list[dict] = None) -> list:
        history = history or []
        tool_names = list(tools.keys())

        # 🔒 Normalize input ONCE
        text = self._extract_text(user_input)
        lowered = text.lower()

        formatted_history = "\n".join([f"{msg.get('role', 'user')}: {msg.get('content', '')}" for msg in history[-5:]])

        prompt = f"""
You are an AI planner in a Model Context Protocol (MCP) system.

Your job is to decide WHICH TOOLS to call and in WHAT ORDER.

Here is the recent conversation history for context:
{formatted_history}

User input:
"{text}"

Available tools:
{tool_names}

IMPORTANT RULES:

1. If the user is asking to SEARCH for a product
   (examples: "buy", "price", "find", "compare", product names),
   you MUST include these tools in order:
   - generate_query
   - search_amazon
   - search_flipkart
   - rank_results

2. If the user is asking for SIMILAR / ALTERNATIVE / CHEAPER products
   (keywords include: "similar", "like this", "alternatives", "cheaper"),
   you MUST include:
   - find_similar_products

3. You MAY include BOTH search and similarity tools if needed.

4. Use ONLY tools from the available tools list.
5. Respond ONLY in valid JSON.
6. Do NOT include explanations or markdown.

OUTPUT FORMAT (exact):
{{
  "tool_sequence": ["tool_name_1", "tool_name_2"]
}}
"""

        for model_name in self.models:
            try:
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                )

                raw_text = (response.text or "").strip()
                if not raw_text:
                    raise ValueError("Empty response from Gemini")

                parsed = json.loads(raw_text)
                sequence = parsed.get("tool_sequence")

                if not isinstance(sequence, list):
                    raise ValueError("tool_sequence is not a list")

                for tool in sequence:
                    if tool not in tool_names:
                        raise ValueError(f"Invalid tool: {tool}")

                return sequence

            except (ServerError, ClientError, json.JSONDecodeError, ValueError) as e:
                logger.warning(
                    "Gemini model %s failed, reason: %s",
                    model_name,
                    str(e),
                )
                continue

        # 🔐 FINAL SAFE FALLBACK (NO LLM)
        logger.error("All Gemini models failed. Using deterministic fallback.")

        if any(word in lowered for word in [
            "similar",
            "like this",
            "alternative",
            "alternatives",
            "cheaper",
        ]):
            return ["find_similar_products"]

        return [
            "generate_query",
            "search_amazon",
            "search_flipkart",
            "rank_results",
        ]
