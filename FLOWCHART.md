# MarketingFlow AI — LangGraph Flow

```mermaid
flowchart TD
    A([START]) --> S[Supervisor Agent]
    S -->|knowledge_answer| K[Client Knowledge RAG]
    S -->|content_only| K
    S -->|strategy_only| K
    S -->|full_campaign| K

    K -->|Knowledge question| QA[Knowledge Answer Agent]
    QA --> Z([END])

    K -->|Content only| C[Content Creator Agent]
    K -->|Needs strategy/research| R[Research Agent - Google Search]

    R --> ST[Marketing Strategist Agent]
    ST -->|Strategy only| F[Finalizer]
    ST -->|Full campaign| C

    C --> V[Reviewer Agent]
    V --> F
    F --> Z

    D[(Client Form + TXT/MD Knowledge)] -.-> K
    G[(Gemini Embeddings)] -.-> K
    W[(Gemini Google Search)] -.-> R
    L[(Gemini 2.5 Flash-Lite)] -.-> S
    L -.-> ST
    L -.-> C
    L -.-> V
```

## Full campaign path

```text
Client Form / Documents
        ↓
Supervisor
        ↓
Client Knowledge Agent (Semantic RAG)
        ↓
Research Agent (Live Google Search)
        ↓
Marketing Strategist
        ↓
Content Creator
        ↓
Reviewer
        ↓
Final Deliverable
```
