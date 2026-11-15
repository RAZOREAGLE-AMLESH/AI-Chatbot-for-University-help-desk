# Class Diagram Documentation
## AI Chatbot for University Help Desk (KIET)

---

## 1. Description

The Class Diagram reflects the object-oriented and modular structure of the implemented system, illustrating the domain models, service layers, configuration classes, and controller blueprints.

---

## 2. Mermaid Class Diagram

```mermaid
classDiagram
    %% Configuration Hierarchy
    class Config {
        +str SECRET_KEY
        +str ADMIN_API_KEY
        +bool DEBUG
        +bool TESTING
        +str HOST
        +int PORT
        +str APP_NAME
        +str APP_VERSION
        +str INSTITUTION
        +str DATABASE_PATH
    }

    class DevelopmentConfig {
        +bool DEBUG
        +str HOST
    }

    class ProductionConfig {
        +bool DEBUG
        +str HOST
    }

    class TestingConfig {
        +bool TESTING
        +bool DEBUG
        +str DATABASE_PATH
    }

    Config <|-- DevelopmentConfig
    Config <|-- ProductionConfig
    Config <|-- TestingConfig

    %% Domain Entities (Database Models)
    class FAQ {
        +int id
        +str question
        +str answer
        +str category
        +str source_url
        +int is_verified
        +str last_verified
        +str created_at
        +str updated_at
    }

    class Conversation {
        +int id
        +str session_id
        +str created_at
    }

    class Message {
        +int id
        +int conversation_id
        +str sender
        +str message
        +float confidence
        +str timestamp
    }

    Conversation "1" *-- "0..*" Message : contains

    %% Core Services
    class TFIDFEngine {
        -list corpus_tokens
        -dict idf
        -list tfidf_vectors
        -bool fitted
        +fit(questions: list)
        +query(text: str, k: int) list
        -_compute_tf(tokens: list) dict
        -_compute_idf() dict
        -_cosine_similarity(vec_a, vec_b) float
        -_vectorise_query(query: str) dict
        +is_fitted() bool
        +corpus_size() int
    }

    class ChatbotService {
        +CONFIDENCE_THRESHOLD: float = 0.20
        +TOP_K: int = 5
        +get_answer(user_message: str, session_id: str, db_path: str) dict
        +initialise_chatbot(db_path: str) int
        +refresh_index(db_path: str)
        -_load_and_index(db_path: str)
    }

    class DatabaseService {
        +list_faqs(category: str, db_path: str) list
        +find_faq(faq_id: int, db_path: str) dict
        +find_faqs_by_keyword(query: str, db_path: str) list
        +add_faq(question, answer, category, source_url, is_verified) dict
        +edit_faq(faq_id: int, updates: dict, db_path: str) dict
        +remove_faq(faq_id: int, db_path: str) bool
        +record_exchange(session_id, user_msg, bot_resp, confidence)
        +get_chat_history(session_id: str, limit: int) list
        +get_stats(db_path: str) dict
    }

    class NLPService {
        +STOPWORDS: set
        +preprocess(text: str) list
        -_strip_suffix(word: str) str
    }

    %% Route Blueprints / Controllers
    class ChatController {
        +chat() POST /api/chat
        +chat_history() GET /api/chat/history
    }

    class AdminController {
        +admin_stats() GET /api/admin/stats
        +admin_list_faqs() GET /api/admin/faqs
        +admin_get_faq(id) GET /api/admin/faqs/id
        +admin_create_faq() POST /api/admin/faqs
        +admin_update_faq(id) PUT /api/admin/faqs/id
        +admin_delete_faq(id) DELETE /api/admin/faqs/id
        +admin_rebuild_index() POST /api/admin/index/rebuild
    }

    class HealthController {
        +health_check() GET /api/health
    }

    %% Dependencies
    ChatbotService ..> TFIDFEngine : uses
    ChatbotService ..> DatabaseService : calls
    ChatbotService ..> NLPService : uses
    ChatController ..> ChatbotService : invokes
    AdminController ..> DatabaseService : calls
    AdminController ..> ChatbotService : triggers refresh
    DatabaseService ..> FAQ : queries/persists
    DatabaseService ..> Conversation : manages
    DatabaseService ..> Message : persists
```

---

## 3. Structural Highlights

1. **Layered Separation:**
   - **Controllers (Routes):** Handle HTTP protocol parsing, header verification, and JSON serialization.
   - **Service Layer (`services/`):** Encapsulates core chatbot logic, NLP tokenization, similarity calculation, and database transaction abstractions.
   - **Data Layer (`models/`):** Directly executes parameterized SQLite queries with explicit foreign key constraints.
2. **Implementation Mapping Note:**
   - `Config` and `TFIDFEngine` are implemented as Python classes.
   - `ChatController`, `AdminController`, and `HealthController` represent Flask Blueprints (`routes/chat.py`, `routes/admin.py`, `routes/health.py`).
   - `FAQ`, `Conversation`, and `Message` represent relational SQLite tables and their corresponding model functions (`models/faq.py`, `models/conversation.py`), avoiding heavyweight ORM dependencies while maintaining relational integrity.
3. **Stateless Scalability:** The `TFIDFEngine` maintains an in-memory sparse index that is cleanly rebuilt whenever administrative changes occur via `refresh_index()`.
