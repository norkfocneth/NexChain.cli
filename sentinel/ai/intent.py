"""
ChainSentinel Intent Router & Entity Extractor
Extracts addresses and maps natural language user queries (Hinglish/English) to deterministic Python tools.
Features conversation context tracking so follow-ups like 'Why?' or 'Graph bhi bana' retain previous address.
"""

import re
import json
from typing import Dict, Any, Optional, Tuple
from sentinel.blockchain import detect_network
from sentinel.ai.llm import query_local_llm, get_available_model


# Regular expressions for crypto addresses
TRON_REGEX = r'\b(T[1-9A-HJ-NP-za-km-z]{33})\b'
ETH_REGEX = r'\b(0x[0-9a-fA-F]{40})\b'
BTC_SEGWIT_REGEX = r'\b(bc1[a-zA-HJ-NP-Z0-9]{25,65})\b'
BTC_LEGACY_REGEX = r'\b([13][a-km-zA-HJ-NP-Z1-9]{25,34})\b'
GENERIC_ADDR_REGEX = r'\b(bc1q[a-zA-Z0-9_]+|TX[a-zA-Z0-9_]+|0x[a-fA-F0-9]+)\b'


def extract_address(text: str) -> Optional[str]:
    """Extracts first valid cryptocurrency address from text."""
    for pattern in [TRON_REGEX, ETH_REGEX, BTC_SEGWIT_REGEX, BTC_LEGACY_REGEX, GENERIC_ADDR_REGEX]:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


class IntentRouter:
    def __init__(self):
        self.last_address: Optional[str] = None
        self.last_intent: Optional[str] = None

    def route(self, user_input: str) -> Dict[str, Any]:
        text = user_input.strip()
        lower_text = text.lower()

        # Step 1: Address Extraction
        extracted_addr = extract_address(text)
        target_address = extracted_addr or self.last_address

        # Update state if new address found
        if extracted_addr:
            self.last_address = extracted_addr

        # Step 2: Deterministic Fast Rule Matching (Zero latency & 100% reliable)
        # Bulk Scan Request
        if any(w in lower_text for w in ["bulk", "csv", "audit", "batch", "dump", "file scan"]):
            return {
                "intent": "scan_bulk",
                "address": None,
                "confidence": 0.95,
                "needs_address": False
            }
        # A. Graph Request
        if any(w in lower_text for w in ["graph", "flow", "chart", "map", "topology", "link"]):
            self.last_intent = "generate_graph"
            return {
                "intent": "generate_graph",
                "address": target_address,
                "confidence": 0.95,
                "needs_address": target_address is None
            }

        # B. Reports / Why / Reason Request
        if any(w in lower_text for w in ["why", "report", "complaint", "shikayat", "saboot", "evidence", "kyun", "details", "reports dikhao"]):
            self.last_intent = "show_reports"
            return {
                "intent": "show_reports",
                "address": target_address,
                "confidence": 0.95,
                "needs_address": target_address is None
            }

        # C. Scan / Safety Check Request
        if extracted_addr or any(w in lower_text for w in [
            "scan", "check", "scammer", "safe", "fraud", "p2p", "investigate",
            "bhai ye wallet", "surakshit", "fake", "kaisa hai", "verify", "is this"
        ]):
            self.last_intent = "wallet_scan"
            return {
                "intent": "wallet_scan",
                "address": target_address,
                "confidence": 0.95,
                "needs_address": target_address is None
            }

        # D. List Flagged / Threats
        if any(w in lower_text for w in ["flagged", "threats", "all scammers", "list", "sabse dangerous", "database"]):
            self.last_intent = "list_flagged"
            return {
                "intent": "list_flagged",
                "address": None,
                "confidence": 0.90,
                "needs_address": False
            }

        # E. Cases
        if any(w in lower_text for w in ["case", "cases", "investigation"]):
            self.last_intent = "show_cases"
            return {
                "intent": "show_cases",
                "address": None,
                "confidence": 0.90,
                "needs_address": False
            }

        # F. Sync
        if any(w in lower_text for w in ["sync", "update", "threat feed"]):
            self.last_intent = "sync_intel"
            return {
                "intent": "sync_intel",
                "address": None,
                "confidence": 0.90,
                "needs_address": False
            }

        # G. Greetings
        if any(lower_text.startswith(w) for w in ["hi", "hello", "hey", "namaste", "suno", "yo", "help"]):
            return {
                "intent": "greeting",
                "address": target_address,
                "confidence": 0.99,
                "needs_address": False
            }

        # Step 3: Optional Local LLM router fallback for complex colloquial phrasing
        if get_available_model():
            llm_result = self._route_with_llm(text, target_address)
            if llm_result:
                return llm_result

        # Default fallback
        return {
            "intent": "general_chat",
            "address": target_address,
            "confidence": 0.50,
            "needs_address": False
        }

    def _route_with_llm(self, text: str, current_address: Optional[str]) -> Optional[Dict[str, Any]]:
        prompt = f"""You are ChainSentinel Intent Router. Classify the user query into a JSON tool call.
Possible intents: "wallet_scan", "show_reports", "generate_graph", "list_flagged", "general_chat".
User text: "{text}"
Current active wallet in context: "{current_address or ''}"

Return ONLY a JSON object:
{{"intent": "<one of the intents>", "address": "<extracted wallet or empty string>"}}"""
        response = query_local_llm(prompt, temperature=0.1)
        if response:
            try:
                # Extract json from response
                start = response.find("{")
                end = response.rfind("}")
                if start != -1 and end != -1:
                    data = json.loads(response[start:end+1])
                    intent = data.get("intent", "general_chat")
                    addr = data.get("address") or current_address
                    return {
                        "intent": intent,
                        "address": addr,
                        "confidence": 0.85,
                        "needs_address": (intent in ["wallet_scan", "show_reports", "generate_graph"]) and (not addr)
                    }
            except Exception:
                pass
        return None
