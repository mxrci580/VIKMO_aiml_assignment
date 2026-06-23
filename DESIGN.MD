# VIKMO Dealer Assistant - Design Document

## 1. System Architecture

User Query
↓
FAISS Retriever
↓
Top-K Catalogue Documents
↓
Gemini 2.5 Flash
↓
Function Calling (if required)
↓
Tools
    - check_stock
    - find_parts_by_vehicle
    - create_order
↓
Grounded Response

## 2. Retrieval Approach

- Product catalogue converted into documents
- Each document contains:
  - SKU
  - Name
  - Category
  - Brand
  - Vehicle Fitment
  - Price
  - Stock
  - Description

- Embedded using HuggingFace embeddings

### Chunking Strategy

Each catalogue product was stored as a single document.

Since product records are relatively small and self-contained, additional text chunking was not required. Treating each SKU as one document preserves product context and simplifies retrieval.

### Embedding Choice

HuggingFace embeddings were selected because they are free, easy to run locally, and integrate well with LangChain and FAISS. They provide semantic search capability without requiring paid API calls.

- Stored in FAISS vector database
- Top-k similarity search retrieves relevant products

Retrieved documents are injected into the Gemini prompt as grounding context before response generation. This enables retrieval-augmented generation (RAG) and reduces hallucinations.

Why FAISS?
- Fast
- Lightweight
- Works locally
- Suitable for 600 product catalogue

## 3. Tool Design

The assistant uses Gemini 2.5 Flash function calling to dynamically select tools based on user intent.

Implemented tools:

### check_stock()

Returns current inventory for a SKU.

### find_parts_by_vehicle()

Returns compatible parts for a specified vehicle.

### create_order()

Creates structured order output containing:
- dealer name
- line items
- order id
- status

Gemini generates function arguments, Python executes the tool, and the result is returned to Gemini before generating the final response.

This approach ensures grounded responses and prevents the model from inventing stock levels or order confirmations.

## 4. Conversation Memory

### Chat History

Conversation history is maintained throughout the session and appended to the prompt for each user interaction.

This allows the assistant to retain context across multiple turns and answer follow-up questions more naturally.

Future improvements could include entity-level memory (e.g., current SKU and vehicle tracking) and persistent storage.

## 5. Prompt Design

The assistant uses a system prompt that restricts responses to vehicle parts, stock lookup, and order-related tasks.

The prompt instructs the model to:

- Use catalogue information as the source of truth.
- Ask clarifying questions when information is missing.
- Refuse unrelated requests politely.
- Avoid inventing product, stock, or pricing information.

This improves grounding and reduces hallucination.

## 6. Guardrails

Assistant restricted to:

- Vehicle parts
- Inventory lookup
- Ordering

Out-of-domain requests are politely refused.

Examples:
- Weather
- IPL
- Jokes

## 7. Evaluation Methodology

### Evaluation Metric

Assistant performance was measured using task success rate.

A test was considered successful if the assistant:
- retrieved the correct product information,
- invoked the appropriate tool when required,
- maintained conversation context correctly,
- asked clarifying questions for ambiguous requests,
- refused out-of-domain queries appropriately.

Created evaluation suite covering:

- Retrieval
- Tool usage
- Memory
- Ambiguous queries
- Out-of-domain requests

Total Tests: 10

Passed: 10

Accuracy: 100%

## 8. Failure Analysis

Potential failure modes include:

- Retrieval errors when multiple products have similar descriptions.
- Incorrect tool selection for unusually phrased user requests.
- Dependence on conversation state for follow-up questions.
- Ambiguous vehicle descriptions without make/model information.
- Prompt-based guardrails may occasionally over-refuse valid edge cases.

Future improvements would include hybrid retrieval, more robust evaluation coverage, and persistent memory storage.

## 9. Future Improvements

- Support multiple tool calls in a single turn
- Hybrid search (BM25 + Vector Search)
- Better order validation and inventory checks
- WhatsApp interface
- Multimodal part identification from images
- Persistent conversation memory using a database
- A lightweight Streamlit chat interface was added to provide a WhatsApp-style conversational experience on top of the assistant.

## 10. Demand Forecasting

### Validation Scheme

A holdout validation strategy was used.

The final 4 weeks of data for each SKU were reserved as the test window.
All earlier observations were used for training.

This prevents information leakage because no future observations are used when fitting the model.

### Baseline

A moving-average baseline using the previous 4 weeks of sales was implemented.

### Proposed Model

A Random Forest Regressor was trained using:

- lag_1 sales
- lag_2 sales
- lag_3 sales
- lag_4 sales
- 4-week rolling mean
- promo_flag

These features capture recent sales momentum and promotional effects.

### Metric

Mean Absolute Error (MAE) was used because it is easy to interpret in units sold.


## Forecasting Results

A 4-week holdout window was used for evaluation. The final four observations for each SKU were reserved for testing, while all earlier observations were used for training.

A moving-average baseline achieved an MAE of 7.85.

The Random Forest model achieved an MAE of approximately 5.62, representing a 28.35% improvement over the baseline.

Feature importance analysis showed that the 4-week rolling average was the strongest predictor (68.7% importance), followed by promotional activity (16.4%). This suggests that recent demand trends and promotions are the primary drivers of future demand.

After evaluation, the model was retrained on all available historical data and used to generate forecasts for the next four weeks for each SKU.

## Leakage Prevention

All lag and rolling features were created using historical observations only.

The rolling mean feature was computed as:

groupby("sku")["units_sold"].shift(1).rolling(4).mean()

The shift(1) ensures that the current week's sales are not included in the feature calculation.

The most recent four weeks for each SKU were held out as the test window and were never used during training.


## Chat UI

A lightweight chat interface was implemented using Streamlit to provide a WhatsApp-style conversational experience.

### Architecture

User
↓
Streamlit Chat UI
↓
process_query()
↓
FAISS Retrieval
↓
Catalogue Context
↓
Gemini 2.5 Flash
↓
Tool Calling (optional)
↓
Grounded Response

### Features

- Real-time conversational interface
- Conversation history within a session
- Example query shortcuts for quick testing
- Support for retrieval, stock lookup, and order workflows
- Integration with the existing assistant backend without modifying core business logic

### Design Choice

Streamlit was selected because it allows rapid development of interactive AI applications while keeping the focus on retrieval, tool calling, and forecasting functionality.

The UI layer is intentionally thin and delegates all reasoning, retrieval, memory management, and tool execution to the backend assistant.

### Benefits

- Improves usability compared to a command-line interface
- Demonstrates how the assistant can be deployed as a customer-facing application
- Makes evaluation and testing easier for reviewers
- Provides a foundation for future deployment as a web or WhatsApp-based assistant