# VIKMO Dealer Assistant

## Overview

This project implements a conversational AI assistant for auto-parts dealers.

The assistant can:

- Retrieve relevant products from the catalogue.
- Check stock availability.
- Find parts by vehicle.
- Create structured orders.
- Maintain conversation context across multiple turns.

The system uses Retrieval-Augmented Generation (RAG) with FAISS vector search and Gemini for conversational interaction.

---

## Tech Stack

- Python
- Google Gemini 2.5 Flash
- LangChain
- FAISS
- HuggingFace Embeddings
- Pandas

---

## Project Structure

```text
assistant/
evaluation/
data/
README.md
DESIGN.md
requirements.txt
```

---

## Setup

Install dependencies:

```bash
pip install -r requirements.txt
```

Create a `.env` file:

```env
GOOGLE_API_KEY=your_api_key
```

---

## Running the Assistant

```bash
python assistant/agent.py
```

---

## Running Evaluation

```bash
python evaluation/run_eval.py
```

---

## Example Queries

```text
Do you have brake pads for Bajaj Pulsar 150?

Check stock for BRK-1002

I need tyres

What's the weather today?
```

---

## Example Interaction

User:
```text
Do you have brake pads for Bajaj Pulsar 150?
```

Assistant:
```text
Yes, BRK-1002 Brake Pad Set for Bajaj Pulsar 150 is available.
```

User:
```text
What is the stock?
```

Assistant:
```text
Brake Pad Set — Bajaj Pulsar 150 currently has 136 units in stock.
```

---

## Assumptions

- Product information is sourced from the provided catalogue.
- Stock information is retrieved from catalogue data.
- The assistant is restricted to auto-parts related queries.
- Conversation state is maintained for follow-up questions.
- Evaluation results are based on the included evaluation suite.

---

## Evaluation Results

Total Tests: 10

Passed: 10

Accuracy: 100%

See:

- DESIGN.md
- evaluation/results.md

for additional details.


## Demand Forecasting Results

Baseline MAE: 7.85

Random Forest MAE: 5.62

Improvement over baseline: 28.35%

The forecasting model was trained using:

- lag_1
- lag_2
- lag_3
- lag_4
- rolling_mean_4
- promo_flag

Future forecasts are available in:

forecast_next_4_weeks.csv

## Tool Calling

The assistant uses Gemini 2.5 Flash function calling.

Gemini can invoke:

- check_stock
- find_parts_by_vehicle
- create_order

Tool outputs are executed in Python and returned to Gemini for grounded responses.