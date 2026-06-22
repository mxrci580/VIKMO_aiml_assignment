import sys
import os

sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            ".."
        )
    )
)

import json
sys.path.append(
    os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            "..",
            "assistant"
        )
    )
)

from agent import process_query

with open("evaluation/eval_set.json", "r") as f:
    test_cases = json.load(f)

passed = 0
total = len(test_cases)

for i, test in enumerate(test_cases, start=1):

    query = test["query"]

    if isinstance(query, list):

        response = None

        for turn in query:
            response = process_query(turn)

    else:
        response = process_query(query)

    is_pass = False

    if test["expected"] == "returns relevant brake pad SKU":

        if "BRK-1002" in response:
            is_pass = True

    elif test["expected"] == "returns stock information":

        if "stock" in response.lower() or "units" in response.lower():
            is_pass = True

    elif test["expected"] == "asks for vehicle information":

        if "vehicle" in response.lower():
            is_pass = True

    elif test["expected"] == "uses previous context":

        if "136" in response or "stock" in response.lower():
            is_pass = True

    elif test["expected"] == "politely refuses and stays on domain":

        response_lower = response.lower()

        if (
            "cannot" in response_lower
            or "only provide" in response_lower
            or "catalogue" in response_lower
            or "only help" in response_lower
            or "vehicle parts" in response_lower
            or "stock" in response_lower
            or "orders" in response_lower
        ):
            is_pass = True

    if is_pass:
        passed += 1

    status = "PASS" if is_pass else "FAIL"

    print(f"\nTest {i}")
    print("Query:", query)
    print("Response:", response)
    print("Expected:", test["expected"])
    print("Status:", status)
    print("-" * 50)

accuracy = (passed / total) * 100

print("\n" + "=" * 50)
print(f"Passed: {passed}/{total}")
print(f"Accuracy: {accuracy:.2f}%")
print("=" * 50)

#python evaluation/run_eval.py
