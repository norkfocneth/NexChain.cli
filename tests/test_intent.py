import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sentinel.ai.intent import IntentRouter

router = IntentRouter()

# Step 1: User asks in natural Hinglish with address
q1 = "Mujhe ek wallet mila hai P2P transaction ke liye, check karke batao scammer wallet toh nahi hai: TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x"
r1 = router.route(q1)
print("Query 1:", q1)
print("Route 1:", r1)
assert r1["intent"] == "wallet_scan"
assert r1["address"] == "TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x"
print("✓ Step 1 passed: Address extracted, intent = wallet_scan\n")

# Step 2: User asks follow-up "Why?" without repeating address
q2 = "Why? Kya reports aayi hain?"
r2 = router.route(q2)
print("Query 2:", q2)
print("Route 2:", r2)
assert r2["intent"] == "show_reports"
assert r2["address"] == "TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x"
print("✓ Step 2 passed: Context memory preserved address, intent = show_reports\n")

# Step 3: User asks follow-up "Graph bhi bana"
q3 = "Iska graph bhi bana ke dikhao"
r3 = router.route(q3)
print("Query 3:", q3)
print("Route 3:", r3)
assert r3["intent"] == "generate_graph"
assert r3["address"] == "TX9a8vR2bQ8YwM4kF1nP7dL3tS5eH6jZ0x"
print("✓ Step 3 passed: Context memory preserved address, intent = generate_graph\n")

# Step 4: User asks to list all flagged wallets
q4 = "show all flagged threat wallets"
r4 = router.route(q4)
print("Query 4:", q4)
print("Route 4:", r4)
assert r4["intent"] == "list_flagged"
print("✓ Step 4 passed: Intent = list_flagged\n")

print("ALL CONVERSATIONAL INTENT ROUTER TESTS PASSED SUCCESSFULLY! 🚀")
