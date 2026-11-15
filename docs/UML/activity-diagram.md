# Activity Diagram Documentation
## AI Chatbot for University Help Desk (KIET)

---

## 1. Description

The Activity Diagram models the step-by-step workflow of handling a user chat message: from client-side input validation and API dispatch, through server-side preprocessing, similarity computation, threshold branch logic, database logging, and final UI rendering.

---

## 2. Mermaid Activity Flowchart

```mermaid
flowchart TD
    Start([User Types Question]) --> InputCheck{Input Valid?}

    InputCheck -- No (Empty / < 2 chars) --> ShowToast[Display Client Warning Toast] --> EndFail([Await Correction])

    InputCheck -- Yes (>= 2 chars) --> SendMsg[Send POST /api/chat with session_id]
    SendMsg --> ShowTyping[Display UI Typing Indicator & User Bubble]

    ShowTyping --> ServerReceive[Server Receives Request]
    ServerReceive --> ServerValidate{Valid JSON & Length?}

    ServerValidate -- No --> Return400[Return HTTP 400 Bad Request]
    Return400 --> ClientError[Client Renders Error Notice] --> EndFail

    ServerValidate -- Yes --> CheckSession{Session Exists in DB?}
    CheckSession -- No --> CreateConv[Insert New Conversation Record] --> Preprocess
    CheckSession -- Yes --> FetchConv[Retrieve Existing Conversation] --> Preprocess

    Preprocess[Preprocess Query: Lowercase, Remove Punctuation, Filter Stopwords, Stem Tokens] --> Vectorize[Vectorize Query using Fitted IDF]

    Vectorize --> CalcSim[Calculate Cosine Similarity against FAQ Corpus]
    CalcSim --> RankCandidate[Rank Candidates & Retrieve Top Match]

    RankCandidate --> ThresholdCheck{Score >= 0.20?}

    ThresholdCheck -- Yes (Match Found) --> PrepSuccess[Prepare Verified Answer, Category, and Official Source URL]
    ThresholdCheck -- No (Low Confidence) --> PrepFallback[Prepare Safe Fallback Response directing to official contacts]

    PrepSuccess --> LogExchange[Persist User Message & Bot Response with Confidence to SQLite]
    PrepFallback --> LogExchange

    LogExchange --> Return200[Return HTTP 200 JSON Response]
    Return200 --> ClientReceive[Client Receives Payload]

    ClientReceive --> HideTyping[Hide Typing Indicator]
    HideTyping --> RenderBubble[Render Bot Message Bubble with Category & Confidence Badge]

    RenderBubble --> HasSource{Source URL Available & Not Fallback?}
    HasSource -- Yes --> RenderSource[Render Safe Source Link Button] --> ScrollBottom[Scroll Chat Window to Bottom]
    HasSource -- No --> ScrollBottom

    ScrollBottom --> Complete([Interaction Complete - Await Next Query])
```

---

## 3. Decision Points & Business Rules

1. **Client-Side Throttling:** Messages under 2 characters or exceeding 500 characters are halted before dispatching an HTTP request.
2. **Server-Side Validation:** The backend validates Content-Type and payload integrity, returning standard HTTP error codes (`400`, `415`).
3. **Institutional Protection Gate (Threshold Check):**
   - If `cosine_similarity >= 0.20`: Returns the official verified answer.
   - If `cosine_similarity < 0.20`: Directly engages the safety fallback. The system refuses to hallucinate unverified dates, fees, or faculty names.
4. **Audit Logging:** Every user message and system answer is logged to the SQLite database with timestamp and calculated confidence score.
