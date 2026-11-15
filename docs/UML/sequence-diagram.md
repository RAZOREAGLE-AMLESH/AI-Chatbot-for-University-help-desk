# Sequence Diagram Documentation
## AI Chatbot for University Help Desk (KIET)

---

## 1. Description

The Sequence Diagram illustrates the runtime chronology of messages and function calls exchanged between actors and software components during a query transaction.

---

## 2. Mermaid Sequence Diagram

```mermaid
sequenceDiagram
    autonumber
    actor User as University User
    participant UI as Frontend Client (script.js)
    participant API as Flask Chat API (routes/chat.py)
    participant CS as Chatbot Service (chatbot_service.py)
    participant NLP as TF-IDF Engine (nlp_service.py)
    participant DB as SQLite DB (database_service.py)

    User->>UI: Submits Query ("What courses are offered at KIET?")
    activate UI
    UI->>UI: Validate length & retrieve persistent session_id
    UI->>UI: Render User Bubble & Show Typing Indicator

    UI->>API: POST /api/chat { message, session_id }
    activate API

    API->>API: validate_chat_input(payload)
    alt Invalid Input
        API-->>UI: 400 Bad Request { success: false, error: "..." }
        UI->>User: Display Error Banner
    else Valid Input
        API->>CS: get_answer(user_message, session_id)
        activate CS

        CS->>NLP: query(user_message, k=5)
        activate NLP
        NLP->>NLP: preprocess(query_text)
        NLP->>NLP: compute cosine similarity
        NLP-->>CS: return [(candidate_index, similarity_score)]
        deactivate NLP

        alt Confidence Score >= 0.20
            CS->>CS: Resolve matched FAQ from in-memory cache
        else Low Confidence (< 0.20)
            CS->>CS: Assemble official fallback response & contacts
        end

        CS->>DB: record_exchange(session_id, user_msg, bot_resp, confidence)
        activate DB
        DB->>DB: get_or_create_conversation(session_id)
        DB->>DB: save_message(user_msg)
        DB->>DB: save_message(bot_resp, confidence)
        DB-->>CS: exchange committed
        deactivate DB

        CS-->>API: return { success: true, answer, category, source, confidence, session_id }
        deactivate CS

        API-->>UI: 200 OK JSON Response
        deactivate API

        UI->>UI: Hide Typing Indicator
        UI->>UI: Render Bot Message Bubble with Category & Confidence
        alt Official Source Link Exists
            UI->>UI: Render Verified/Reference Link Card
        end
        UI->>User: Display Bot Response to User
    end
    deactivate UI
```

---

## 3. Sequence Highlights

1. **Client Isolation:** The UI immediately updates with the user's bubble and animated indicator, guaranteeing responsiveness.
2. **In-Memory Query Performance:** Query vectorization and candidate comparison happen entirely in memory via `TFIDFEngine`, ensuring responsive local retrieval.
3. **Guaranteed Transactional Logging:** Regardless of whether the answer is a verified FAQ match or a safe fallback, `record_exchange()` synchronously writes both interaction halves to the SQLite database.
