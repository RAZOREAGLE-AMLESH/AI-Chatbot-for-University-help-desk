# Use Case Documentation
## AI Chatbot for University Help Desk (KIET)

---

## 1. Description

The Use Case Diagram defines the interactions between the system actors and the core capabilities provided by the **AI Chatbot for University Help Desk**.

### Identified Actors
1. **University User (Student / Parent / Visitor):** Interacts with the public chatbot interface to ask questions, view responses, read official links, and start new conversations.
2. **Help Desk Administrator:** Manages and audits the institutional FAQ database, monitors conversation statistics, and rebuilds the NLP indexing engine.
3. **NLP Search Engine (Internal System Actor):** Normalizes queries, computes TF-IDF representations, and calculates cosine similarity scores.

---

## 2. Mermaid Use Case Diagram

```mermaid
flowchart LR
    %% Actors
    User(["University User (Student/Parent/Visitor)"])
    Admin(["Help Desk Administrator"])
    NLP[["NLP & TF-IDF Engine"]]

    %% User Subsystem
    subgraph UserBoundary ["Public Help Desk Interface"]
        UC1["Open Help Desk Chat"]
        UC2["Select Suggested Question"]
        UC3["Ask Custom Question"]
        UC4["View Verified Answer & Category"]
        UC5["Access Official KIET Source Link"]
        UC6["Receive Safe Fallback Guidance"]
        UC7["Start New Conversation (Reset Session)"]
    end

    %% Admin Subsystem
    subgraph AdminBoundary ["Admin Management Subsystem"]
        UC8["Authenticate via Admin Key"]
        UC9["View Knowledge Base FAQs"]
        UC10["Add New Verified FAQ"]
        UC11["Update Existing FAQ"]
        UC12["Delete Outdated FAQ"]
        UC13["Search FAQ Records"]
        UC14["View Chat & FAQ Statistics"]
        UC15["Trigger TF-IDF Index Rebuild"]
    end

    %% User Relationships
    User --> UC1
    User --> UC2
    User --> UC3
    User --> UC7
    UC2 --> UC4
    UC3 --> UC4
    UC4 -.->|includes| UC5
    UC3 -.->|low confidence| UC6

    %% Internal NLP Processing
    UC3 -.->|evaluates query| NLP
    NLP -.->|returns similarity score| UC4

    %% Admin Relationships
    Admin --> UC8
    UC8 --> UC9
    UC8 --> UC10
    UC8 --> UC11
    UC8 --> UC12
    UC8 --> UC13
    UC8 --> UC14
    UC8 --> UC15

    UC10 -.->|triggers| UC15
    UC11 -.->|triggers| UC15
    UC12 -.->|triggers| UC15
```

---

## 3. Use Case Specifications

### UC-1: Ask Custom Question
- **Primary Actor:** University User
- **Preconditions:** The user is on the chatbot interface (`/chat` or `index.html`) and the Flask server is running.
- **Main Flow:**
  1. User enters a query into the input field (e.g., "What courses are offered at KIET?").
  2. User presses Enter or clicks Send.
  3. System displays a typing indicator while processing.
  4. Backend preprocesses the text and queries the TF-IDF engine.
  5. The matched FAQ response, confidence score, and category are rendered in a bot message bubble.
  6. The exchange is logged in the SQLite database under the active session ID.
- **Alternative Flow (Low Confidence):**
  - If the query does not match any FAQ with confidence >= 0.20, the system returns a safe fallback directing the user to official KIET contact channels.

### UC-2: Manage FAQs (Admin)
- **Primary Actor:** Help Desk Administrator
- **Preconditions:** Administrator possesses the valid `ADMIN_API_KEY`.
- **Main Flow:**
  1. Admin transmits an HTTP request with header `X-Admin-Key`.
  2. System validates the key using constant-time comparison.
  3. Admin creates, updates, or deletes an FAQ record.
  4. Database updates transactionally, and the NLP engine automatically rebuilds the in-memory TF-IDF index.
