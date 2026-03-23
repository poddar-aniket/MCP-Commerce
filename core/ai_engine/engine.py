import difflib
from core.ai_engine.llm_adapter import LLMAdapter
from core.mcp_server.registry.tool_registry import TOOLS
from core.rag.store import InMemoryStore
from core.rag.memory import ContextMemory
from core.rag.retrieve import Retriever
from core.ai_engine.query_parser import parse_query

from services.ranking.filters import (
    filter_by_max_price,
    filter_cheaper_than,
)
from services.ranking.deduplicate import deduplicate_products
from core.rag.reference_resolver import resolve_reference_price


# --------------------------------------------------
# FIXED TOOL PLANS (NO LLM)
# --------------------------------------------------

FIXED_TOOL_PLANS = {
    "search": [
        "generate_query",
        "search_amazon",
        "search_ebay",
        "search_walmart",
        "rank_results",
    ],
    "similar": [
        "find_similar_products",
    ],
    "cheaper": [
        "find_similar_products",
    ],
    "alternatives": [
        "find_similar_products",
    ],
}

# --------------------------------------------------
# COMMON SENSE FILTER — junk keyword blacklist
# --------------------------------------------------
JUNK_KEYWORDS = [
    "case", "cover", "screen protector", "tempered glass", "skin",
    "t-mobile", "verizon", "at&t", "boost mobile", "cricket", "metro",
    "monthly", "installment", "plan", "/mo", "per month",
    "empty box", "box only", "dummy", "replica", "display model",
    "charger only", "cable only", "adapter only",
]

REFURBISHED_WORDS = ["refurbished", "renewed", "pre-owned", "used", "open box", "reconditioned"]


class AIEngine:
    """
    MCP-compliant AI engine.

    Guarantees:
    - Deterministic execution by default
    - LLM is optional and non-authoritative
    - Similarity NEVER triggers fresh search
    """

    def __init__(self):
        self.llm = LLMAdapter()  # rare fallback only
        self.memory = ContextMemory(InMemoryStore())
        self.retriever = Retriever()

    # ==================================================
    # ENTRYPOINT
    # ==================================================

    def handle_input(self, user_input: str, history: list[dict] = None, result_mode: str = "top_5_overall", item_condition: str = "any"):
        history = history or []
        
        parsed_intent = self.llm.analyze_user_intent(user_input, history)
        print(f"\n🧠 AI Reasoning: {parsed_intent.reasoning}")
        print(f"🎯 Search Query: {parsed_intent.search_query}\n")

        query = parse_query(user_input)

        if parsed_intent:
            query["search_query"] = parsed_intent.search_query
            query["product_name"] = parsed_intent.search_query
            query["raw_query"] = parsed_intent.search_query
            if parsed_intent.min_price is not None:
                query["min_price"] = parsed_intent.min_price
            if parsed_intent.max_price is not None:
                query["max_price"] = parsed_intent.max_price
            item_condition = parsed_intent.condition

        # Defensive guard
        if not query or not query.get("intent"):
            return [], parsed_intent.suggestion

        intent = query["intent"]

        # Deterministic intents NEVER touch LLM
        if intent in FIXED_TOOL_PLANS:
            if intent == "search":
                return self._run_search(query, result_mode=result_mode, item_condition=item_condition), parsed_intent.suggestion
            else:
                return self._run_similarity(query), parsed_intent.suggestion

        # Rare fallback only
        return self._run_llm_fallback(query, history), parsed_intent.suggestion

    # ==================================================
    # SEARCH FLOW (LIVE DATA)
    # ==================================================

    def _run_search(self, query: dict, result_mode: str = "top_5_overall", item_condition: str = "any"):
        context = query
        results = []

        for tool_name in FIXED_TOOL_PLANS["search"]:
            tool = TOOLS.get(tool_name)
            if not tool:
                continue

            if tool_name == "generate_query":
                context = tool(context)
                self.memory.save_product(context)

            elif tool_name.startswith("search_"):
                try:
                    results.extend(tool(context))
                except Exception:
                    continue

            elif tool_name == "rank_results":
                # 🛡️ COMMON SENSE FILTER: drop junk before ranking
                filtered = self._common_sense_filter(results, query, item_condition)
                ranked = tool(filtered)

                if not ranked:
                    return []

                # 🔒 RAG INDEXING GATE (Phase 3.5)
                clean = deduplicate_products(ranked)
                top_k = clean[:5]

                if top_k:
                    self.retriever.index_products(top_k)

                # 🔍 FUZZY DEDUP PASS (runs for ALL modes)
                deduped = self._fuzzy_deduplicate(ranked)

                # 🎛️ RESULT MODE FILTER
                if result_mode == "top_1_each":
                    return self._best_one_per_platform(deduped)
                else:
                    # Default: top_5_overall (cheapest 5 across all platforms)
                    return deduped[:5]

        return []

    # ==================================================
    # COMMON SENSE FILTER
    # ==================================================

    def _common_sense_filter(self, results: list, query: dict, item_condition: str = "any") -> list:
        """
        Two-pass pre-filter applied BEFORE ranking:

        Pass 1 — Junk keyword blacklist:
            Drop any item whose title contains a JUNK_KEYWORD
            (accessories, carrier plans, empty boxes, etc.)

        Pass 2 — Dynamic outlier filter:
            If the user did NOT specify a min_price, drop items whose
            price is less than 10% of the highest price in the batch.
            (Skipped entirely if the batch max is under $50.)
        """
        min_price_specified = query.get("min_price") is not None

        # ------- Pass 1: Context-aware junk keyword blacklist -------
        # Extract the cleaned search query to compare against junk list
        search_query = str(
            query.get("product_name")
            or query.get("raw_query")
            or ""
        ).lower()

        # Dynamically exclude junk keywords the user explicitly searched for.
        # e.g. if the user searches "iphone case", "case" is removed from junk list.
        active_junk = [kw for kw in JUNK_KEYWORDS if kw not in search_query]

        pass1 = []
        for item in results:
            title = str(
                item.get("title", "") if isinstance(item, dict)
                else getattr(item, "title", "")
            ).lower()

            if active_junk and any(kw in title for kw in active_junk):
                continue

            if item_condition == "new":
                if any(kw in title for kw in REFURBISHED_WORDS):
                    continue
            elif item_condition == "refurbished":
                if not any(kw in title for kw in REFURBISHED_WORDS):
                    continue

            pass1.append(item)

        if not pass1:
            return results  # Don't over-filter; give back originals as safety net

        # ------- Pass 2: Dynamic outlier price filter -------
        if min_price_specified:
            return pass1  # User explicitly set a floor — respect it, skip outlier check

        def _price(item):
            try:
                return float(
                    item.get("price", 0) if isinstance(item, dict)
                    else getattr(item, "price", 0) or 0
                )
            except (TypeError, ValueError):
                return 0.0

        prices = [_price(i) for i in pass1 if _price(i) > 0]
        if not prices:
            return pass1

        max_price = max(prices)

        # Skip outlier filter for genuinely cheap searches (batch max < $50)
        if max_price < 50:
            return pass1

        threshold = max_price * 0.10  # Drop anything below 10% of the top price
        pass2 = [i for i in pass1 if _price(i) >= threshold]

        # Safety net: never return empty; fall back to pass1
        return pass2 if pass2 else pass1

    # ==================================================
    # FUZZY DEDUPLICATION
    # ==================================================

    def _fuzzy_deduplicate(self, results: list, threshold: float = 0.85) -> list:
        """
        Removes near-duplicate products by title similarity.
        When two titles are >85% similar, keeps the cheaper one.
        """
        unique_results = []

        for candidate in results:
            new_title = str(candidate.get("title", "") if isinstance(candidate, dict)
                            else getattr(candidate, "title", "")).lower()
            new_price = float(candidate.get("price", float("inf")) if isinstance(candidate, dict)
                              else getattr(candidate, "price", float("inf")) or float("inf"))

            duplicate_found = False
            for idx, existing in enumerate(unique_results):
                existing_title = str(existing.get("title", "") if isinstance(existing, dict)
                                     else getattr(existing, "title", "")).lower()
                existing_price = float(existing.get("price", float("inf")) if isinstance(existing, dict)
                                       else getattr(existing, "price", float("inf")) or float("inf"))

                ratio = difflib.SequenceMatcher(None, new_title, existing_title).ratio()

                if ratio > threshold:
                    # Keep the cheaper one
                    if new_price < existing_price:
                        unique_results[idx] = candidate
                    duplicate_found = True
                    break

            if not duplicate_found:
                unique_results.append(candidate)

        return unique_results

    def _best_one_per_platform(self, results: list) -> list:
        """
        From a deduped result list, returns the single cheapest item
        from each marketplace platform (Amazon, eBay, Walmart).
        """
        best = {}  # { platform_name_lower: item }

        for item in results:
            platform = str(
                item.get("platform", "") if isinstance(item, dict)
                else getattr(item, "platform", "")
            ).lower()

            price = float(
                item.get("price", float("inf")) if isinstance(item, dict)
                else getattr(item, "price", float("inf")) or float("inf")
            )

            if platform not in best or price < float(
                best[platform].get("price", float("inf")) if isinstance(best[platform], dict)
                else getattr(best[platform], "price", float("inf")) or float("inf")
            ):
                best[platform] = item

        # Return in a stable order: amazon → ebay → walmart → others
        priority = ["amazon", "ebay", "walmart"]
        ordered = []
        for p in priority:
            if p in best:
                ordered.append(best[p])
        # Append any unexpected platforms too
        for p, item in best.items():
            if p not in priority:
                ordered.append(item)

        return ordered

    # ==================================================
    # SIMILAR / CHEAPER / ALTERNATIVES (RAG ONLY)
    # ==================================================

    def _run_similarity(self, query: dict):
        reference = query.get("reference_product")
        if not reference:
            return []

        # 🔒 Similarity NEVER triggers search
        results = self.retriever.find_similar(reference)

        # Exclude the reference product itself
        results = [
            r for r in results
            if reference.lower() not in r.get("title", "").lower()
        ]

        # Absolute price constraint
        if query.get("max_price") is not None:
            results = filter_by_max_price(results, query["max_price"])

        # Relative price constraint
        if query["intent"] == "cheaper":
            ref_price = resolve_reference_price(
                self.retriever, reference
            )
            if ref_price is not None:
                results = filter_cheaper_than(results, ref_price)

        return deduplicate_products(results)

    # ==================================================
    # RARE LLM FALLBACK
    # ==================================================

    def _run_llm_fallback(self, query: dict, history: list[dict] = None):
        """
        Only reached for unsupported / ambiguous intents.
        """
        history = history or []

        plan = self.llm.decide_tool_sequence(query, TOOLS, history=history)
        context = query
        results = []

        for tool_name in plan:
            tool = TOOLS.get(tool_name)
            if not tool:
                continue

            if tool_name == "generate_query":
                context = tool(context)

            elif tool_name.startswith("search_"):
                try:
                    results.extend(tool(context))
                except NotImplementedError:
                    continue

            elif tool_name == "rank_results":
                return tool(results)

        return []
