# Evaluation Results

## Summary

Total Tests: 10

Passed: 10

Accuracy: 100%

---

## Categories Tested

### Retrieval
- Product search
- Vehicle-specific part lookup

### Tool Usage
- Stock lookup

### Conversation Memory
- Follow-up stock queries
- Multi-turn conversations

### Ambiguous Queries
- "I need tyres"
- "Need brake pads"
- "Looking for engine oil"

### Out-of-Domain Queries
- Weather
- IPL
- Jokes

---

## Results

| Category | Status |
|-----------|---------|
| Retrieval | PASS |
| Tool Usage | PASS |
| Memory | PASS |
| Clarification | PASS |
| Guardrails | PASS |

---

## Observed Failure Modes

Potential failure modes identified:

- Retrieval may return semantically similar products.
- Multi-turn conversations depend on correct state management.
- Clarification behavior relies on LLM reasoning.
- Out-of-domain detection is prompt-driven.

---

## Conclusion

The assistant passed all 10 evaluation cases and achieved 100% accuracy on the evaluation suite.