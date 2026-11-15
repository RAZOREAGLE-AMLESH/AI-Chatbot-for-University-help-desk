# System Architecture Documentation
## AI Chatbot for University Help Desk (KIET)

---

## 1. Architectural Overview

The **AI Chatbot for University Help Desk** is engineered using a decoupled **Three-Tier Architecture**:
1. **Presentation Tier (Client):** Responsive Single Page Application (SPA) built with HTML5, CSS3, and modern Vanilla JavaScript.
2. **Application Tier (Backend Logic):** RESTful Web Service built on Python Flask, incorporating modular Routing, Services, Validators, and an in-memory TF-IDF Natural Language Processing engine.
3. **Data Tier (Persistence):** Embedded relational SQLite database managing FAQs, session entities, and transactional chat audit logs.

---

## 2. Mermaid System Architecture Diagram

```mermaid
flowchart TD
    subgraph ClientTier ["Presentation Tier (Web Client)"]
        UI_HTML["HTML5 UI Structure (index.html)"]
        UI_CSS["Responsive CSS3 Styling (style.css)"]
        UI_JS["Client Application Logic (script.js)"]
        LocalStorage[("Browser LocalStorage (session_id)")]
        UI_JS <--> LocalStorage
    end

    subgraph APITier ["Application Tier (Flask REST API)"]
        App["Flask App Factory (app.py)"]
        Config["Configuration Management (config.py)"]

        subgraph Routes ["Routing Layer"]
            ChatRoute["Chat Route (/api/chat)"]
            AdminRoute["Admin Route (/api/admin/*)"]
            HealthRoute["Health Route (/api/health)"]
            StaticRoute["Static / UI Route (/chat, /style.css, /script.js)"]
        end

        subgraph Middleware ["Middleware & Utilities"]
            CORS["CORS Preflight & Header Injection"]
            Auth["Admin Key Authenticator (hmac)"]
            Validator["Input Validation (validators.py)"]
        end

        subgraph ServiceLayer ["Business & AI Services"]
            ChatbotService["Chatbot Orchestrator (chatbot_service.py)"]
            NLP["TF-IDF Vectorizer & Cosine Similarity (nlp_service.py)"]
            DBService["Database Service Layer (database_service.py)"]
        end

        App --> Routes
        App --> Middleware
        ChatRoute --> Validator
        AdminRoute --> Auth
        ChatRoute --> ChatbotService
        AdminRoute --> DBService
        AdminRoute --> ChatbotService
        ChatbotService --> NLP
        ChatbotService --> DBService
    end

    subgraph DataTier ["Data Tier (Persistence)"]
        SQLite[("SQLite Embedded Database (instance/chatbot.db)")]
        TableFAQ["FAQ Table (Verified Knowledge Base)"]
        TableConv["Conversation Table (Sessions)"]
        TableMsg["Message Table (Audit Trail)"]

        SQLite --- TableFAQ
        SQLite --- TableConv
        SQLite --- TableMsg
    end

    %% Tier Connections
    UI_JS <== "HTTP POST /api/chat (JSON)" ==> ChatRoute
    UI_JS <== "HTTP GET /chat, /style.css, /script.js" ==> StaticRoute
    DBService <== "Parameterized SQL Queries" ==> SQLite
```

---

## 3. Database Entity Relationship (ER) Sub-diagram

```mermaid
erDiagram
    CONVERSATION ||--o{ MESSAGE : contains

    CONVERSATION {
        int id PK "Auto Increment"
        string session_id UK "Unique UUID"
        string created_at "ISO UTC Timestamp"
    }

    MESSAGE {
        int id PK "Auto Increment"
        int conversation_id FK "References conversation(id)"
        string sender "CHECK ('user', 'bot')"
        string message "Message content"
        float confidence "Calculated Cosine Similarity"
        string timestamp "ISO UTC Timestamp"
    }

    FAQ {
        int id PK "Auto Increment"
        string question "FAQ Question text"
        string answer "FAQ Answer text"
        string category "Domain Category"
        string source_url "Official KIET Link"
        int is_verified "1=Verified, 0=Unverified"
        string last_verified "Verification Date"
        string created_at "ISO UTC Timestamp"
        string updated_at "ISO UTC Timestamp"
    }
```

---

## 4. Architectural Principles

1. **Zero External Runtime Footprint:** No external message brokers, cache servers (e.g. Redis), or container daemons are strictly required for college-level evaluation.
2. **Deterministic Information Retrieval:** Unlike generative models that risk hallucinating non-existent degrees or exam dates, TF-IDF + Cosine Similarity strictly selects answers from verified institutional rows.
3. **Defense in Depth:**
   - Parameterized SQL prevents SQL injection.
   - Text escaping prevents cross-site scripting (XSS).
   - Strict confidence cutoff (0.20) prevents out-of-domain false positives.
   - Constant-time secret checking prevents timing side-channel attacks on the admin panel.
