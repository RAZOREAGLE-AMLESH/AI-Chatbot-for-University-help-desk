# Software Requirements Specification (SRS)
## AI Chatbot for University Help Desk
### Target Institution: KIET Group of Institutions, Ghaziabad

---

## Document Control

| Attribute | Details |
|---|---|
| **Project Title** | AI Chatbot for University Help Desk |
| **Institution** | KIET Group of Institutions, Ghaziabad |
| **Department** | Information Technology / Computer Science & Engineering |
| **Document Version** | 1.1.0 |
| **Status** | Audited & Verified Against Implementation |

### Project Team

| Member | Role | Responsibility |
|---|---|---|
| **Amlesh Singh** | Project Coordinator | Project Planning, Testing, Deployment & Documentation |
| **Anant Singh** | AI / Backend Developer | Chatbot Logic, NLP Engine & API Development |
| **Agraj Dixit** | Frontend Developer | Web Interface, UX Design & Client Integration |

---

## 1. Introduction

The **AI Chatbot for University Help Desk** is an intelligent, automated conversational software system developed for **KIET Group of Institutions, Ghaziabad**. Higher educational institutions handle thousands of recurring queries each academic session concerning admissions, degree programmes, examination schedules, contact points, campus facilities, and institutional policies.

Traditional help-desk operations depend heavily on manual staff intervention during standard working hours. This project introduces a 24/7 web-based automated help desk driven by Natural Language Processing (NLP) techniques, enabling students, parents, applicants, and staff to obtain instant, verified institutional answers.

---

## 2. Purpose

The primary purpose of this specification is to:
1. Define the complete functional and non-functional requirements for the university help desk chatbot system based on the implemented software baseline.
2. Provide a clear technical and architectural baseline for development, testing, and evaluation.
3. Serve as the formal Software Development Project (SDP) documentation for academic evaluation and future enhancements.

---

## 3. Scope

### In-Scope Capabilities
- **Institutional Query Resolution:** Automated answers to questions regarding KIET overview, approved programmes, general admission procedures, campus facilities, fee payment processes, anti-ragging policies, and central contact points.
- **NLP Information Retrieval:** TF-IDF (Term Frequencyâ€“Inverse Document Frequency) vectorization combined with cosine similarity matching over an official knowledge base.
- **Confidence Scoring & Safe Fallbacks:** Calculation of real similarity scores against a strict confidence threshold (`0.20`). If a query cannot be answered with confidence, the bot provides safe fallback guidance rather than fabricating institutional data.
- **Session-Based Conversation Logging:** Storage of user and bot messages, timestamps, and confidence values in a persistent SQLite database.
- **Admin Management API:** Authenticated CRUD operations (protected by `X-Admin-Key` header with constant-time string comparison) to add, update, delete, search, and rebuild FAQ knowledge base indices.
- **Responsive Web Client:** Accessible interface built with HTML5, CSS3, and Vanilla JavaScript with suggested question chips, character counter, and multi-turn session persistence.

### Out-of-Scope Capabilities
- Direct access to personal student marks, confidential financial ledgers, or payment gateway transactions.
- Automated generation of speculative examination dates or unapproved fee amounts.
- Third-party paid cloud AI APIs or proprietary large language models (LLMs).

---

## 4. Intended Users

1. **Prospective Students & Parents:** Inquiring about programmes, admission eligibility, campus location, and general fee structures.
2. **Current Enrolled Students:** Inquiring about semester fee payment procedures, AKTU exam result portals, hostel facilities, library, ERP access, and campus help-desk channels.
3. **Faculty & Campus Visitors:** Seeking department contacts, campus location details, and institutional affiliations.
4. **Help Desk Administrators:** Managing, auditing, verifying, and updating the FAQ database via administrative endpoints.

---

## 5. Overall Description

### 5.1 Product Perspective
The system operates as a lightweight, modular client-server web application. The frontend communicates with a Python Flask REST API over HTTP/JSON. The backend coordinates with an embedded SQLite database and an in-memory TF-IDF index derived from verified institutional records.

```text
+-----------------------+           HTTP / JSON           +------------------------+
|   Web Browser Client  | <=============================> |   Flask REST Backend   |
| (HTML5 / CSS3 / JS)   |   POST /api/chat                | (Python 3.14 / Routes) |
+-----------------------+   GET  /chat                    +-----------+------------+
                                                                      |
                                            +-------------------------+-------------------------+
                                            |                                                   |
                                 +----------v-----------+                            +----------v-----------+
                                 |   NLP / TF-IDF Index |                            |   SQLite Database    |
                                 |  Cosine Similarity   |                            | (instance/chatbot.db)|
                                 +----------------------+                            +----------------------+
```

### 5.2 Operating Environment
- **Server Platform:** Python 3.10+ (tested on Python 3.14.4) on Windows, Linux, or macOS.
- **Database Engine:** SQLite 3 (native standard library).
- **Client Platform:** Any modern standards-compliant web browser (Edge, Chrome, Firefox, Safari) on desktop or mobile devices.

---

## 6. Functional Requirements

### FR-1: Chat Interaction
- **FR-1.1:** The system shall accept user queries via `POST /api/chat` with JSON payload `{"message": string, "session_id": string (optional)}`.
- **FR-1.2:** The system shall reject empty, whitespace-only, or non-string inputs with HTTP status `400 Bad Request`.
- **FR-1.3:** The system shall enforce a maximum input length of 500 characters.
- **FR-1.4:** The system shall return a structured JSON response containing `success`, `answer`, `category`, `source`, `confidence`, `is_verified`, and `session_id`.

### FR-2: Natural Language Query Matching
- **FR-2.1:** The NLP engine shall preprocess all inputs by lowercasing, expanding English contractions, stripping punctuation, filtering stopwords, and stemming common suffixes.
- **FR-2.2:** The system shall represent FAQ entries and user queries as TF-IDF sparse vectors.
- **FR-2.3:** The system shall compute real cosine similarity scores between the query vector and candidate question vectors.
- **FR-2.4:** The system shall support question variations for FAQs to recognize common phrasing and synonyms (e.g., "courses" and "programmes").
- **FR-2.5:** If the maximum similarity score is below `0.20`, the system shall return a safe institutional fallback message directing the user to official channels (`https://www.kiet.edu/` and `info@kiet.edu`).

### FR-3: Data Persistence & Multi-Turn History
- **FR-3.1:** The system shall maintain user sessions by creating a new conversation record upon first contact and appending subsequent messages to the same session ID.
- **FR-3.2:** The system shall store user messages, bot responses, timestamps (UTC ISO format), and calculated confidence scores in the `message` table.
- **FR-3.3:** The system shall provide an endpoint `GET /api/chat/history?session_id=<id>` to retrieve prior conversation history.

### FR-4: Knowledge Base Seeding & Integrity
- **FR-4.1:** The system shall provide a standalone seeding tool (`src/backend/data/seed_faqs.py`) sourcing data strictly from official KIET web pages.
- **FR-4.2:** Each FAQ record must store `category`, `source_url`, and an `is_verified` flag (0 or 1).
- **FR-4.3:** Out of 33 seeded FAQ records, 31 are verified (`is_verified = 1`). Entries whose details fluctuate (e.g. NAAC grade in FAQ #7 and admissions document checklists in FAQ #14) are explicitly marked unverified (`is_verified = 0`) to prevent publishing outdated claims.
- **FR-4.4:** The system shall not fabricate examination dates, faculty contacts, or fee structures.

### FR-5: Administrative FAQ Management
- **FR-5.1:** All administrative routes under `/api/admin/*` must require authentication via the `X-Admin-Key` header.
- **FR-5.2:** Missing or invalid keys must return `401 Unauthorized` or `403 Forbidden` respectively.
- **FR-5.3:** Administrators shall be able to list, search, view, create, update, and delete FAQs.
- **FR-5.4:** Modifying FAQs must trigger an automatic reload of the in-memory TF-IDF index.

### FR-6: User Interface
- **FR-6.1:** The UI shall display KIET institutional branding and live connection status.
- **FR-6.2:** The UI shall present suggested questions as clickable buttons.
- **FR-6.3:** The UI shall show an animated typing indicator while awaiting the backend response.
- **FR-6.4:** The UI shall distinguish verified sources (`âœ“ Verified Source:`) from general links (`Reference Link:`) based on `data.is_verified`.
- **FR-6.5:** The UI shall offer a "New Chat" confirmation dialog that resets the conversation and generates a fresh session ID.

---

## 7. Non-Functional Requirements

### NFR-1: Performance & Latency
- **NFR-1.1:** The system is designed for responsive local operation. Benchmarked measurements on the local development environment show a mean query response latency of approximately **43 ms** (ranging from 29 ms for cache hits up to ~170 ms on cold-start disk commits).
- **NFR-1.2:** Database writes must occur synchronously with minimal overhead per message.

### NFR-2: Security & Authentication
- **NFR-2.1:** No external API keys or credentials shall be exposed to the client.
- **NFR-2.2:** Admin authentication uses a pre-shared secret key transmitted via the `X-Admin-Key` HTTP header. The secret is compared against `os.environ["ADMIN_API_KEY"]` using constant-time string comparison (`hmac.compare_digest`) to protect against timing side-channel attacks. Note: Cryptographic HMAC signature generation over message bodies is not implemented.
- **NFR-2.3:** SQL queries must utilize parameterized bindings exclusively to prevent SQL injection vulnerabilities.
- **NFR-2.4:** Cross-Site Scripting (XSS) prevention: user inputs and bot outputs rendered into the DOM must be sanitized or set via `textContent`.

### NFR-3: Usability & Accessibility
- **NFR-3.1:** The user interface must be fully functional across mobile and desktop viewports (`320px` to `1920px`) using CSS dynamic viewport units (`100dvh`).
- **NFR-3.2:** Implemented accessibility features include:
  - Semantic HTML5 landmark structure (`<header>`, `<main>`, `<footer>`, `<section>`).
  - ARIA live region (`role="log"`, `aria-live="polite"`) for screen readers on incoming messages.
  - Explicit `aria-label` attributes on icon-only buttons (`#clear-chat-btn`, `#send-btn`, `#user-input`).
  - Visible focus indicators (`:focus-within` border glow) on interactive controls.
  - Keyboard navigation supporting `Enter` to send and `Shift + Enter` for multi-line entry.
  *(Note: Formal WCAG 2.1 compliance certification has not been externally audited).*

### NFR-4: Portability & Maintainability
- **NFR-4.1:** The application shall run using standard Python 3 and vanilla web standards without external runtime daemons or commercial licenses.
- **NFR-4.2:** The codebase must adhere to standard modular software engineering separation of concerns (`models/`, `routes/`, `services/`, `utils/`).

---

## 8. Hardware and Software Requirements

### Hardware Requirements
- **Processor:** 1.0 GHz Dual-Core CPU or higher.
- **RAM:** Minimum 512 MB available RAM (1 GB recommended).
- **Storage:** Minimum 100 MB free disk space for application files and SQLite database.
- **Network:** Localhost network stack (standard TCP/IP port 5000).

### Software Requirements
- **Operating System:** Windows 10/11, Ubuntu 20.04+, or macOS 12+.
- **Python Environment:** Python 3.10 to 3.14 (currently verified on Python 3.14.4).
- **Web Browser:** Modern standards-compliant browser (Microsoft Edge, Google Chrome, Mozilla Firefox, Safari).
- **Testing Tool:** PyTest 8.0+ (currently verified on PyTest 9.2.0).

---

## 9. Technology Stack

| Component | Technology | Version | Rationale |
|---|---|---|---|
| **Web Server / Backend** | Python + Flask | Python 3.14.4 / Flask 3.1.3 | Lightweight, standard WSGI microframework ideal for academic project evaluation. |
| **NLP Engine** | Pure Python TF-IDF + Cosine Similarity | Custom pure Python | Dependency-free mathematical implementation ensuring high speed and zero external C-dependencies. |
| **Database** | SQLite 3 | Embedded (Python stdlib) | Zero-configuration relational database with zero external server dependencies. |
| **Frontend Framework** | HTML5 + CSS3 + Vanilla JavaScript | ES6+ | Clean, transparent implementation without build pipelines or node bundlers. |
| **Testing Suite** | PyTest | 9.2.0 | Standard Python automated testing framework with 70 automated test cases. |
| **Version Control** | Git + GitHub | 2.x | Distributed source code management and team collaboration. |

---

## 10. System Constraints

1. **No External Paid APIs:** The system functions entirely on-premise without requiring third-party cloud credits, OpenAI tokens, or Gemini API keys.
2. **Local Single-Node Deployment:** The SQLite database is designed for single-process embedded access.
3. **Strict Information Integrity:** The knowledge base explicitly avoids guessing examination timetables or fluctuating fee schedules.

---

## 11. Assumptions and Dependencies

- **Assumptions:**
  - Users have access to a device with a modern browser supporting JavaScript ES6 and the Fetch API.
  - Institutional policies are updated by administrators via `/api/admin/faqs`.
- **Dependencies:**
  - Python Standard Library (`sqlite3`, `math`, `re`, `json`, `hashlib`, `hmac`, `uuid`, `datetime`).
  - Installed packages: `Flask==3.1.3`, `pytest==9.2.0`.

---

## 12. External Interface Requirements

### User Interfaces
- Single-page responsive web application (`src/frontend/index.html`) featuring an academic header, message stream, suggestion chips, and an expandable message input bar. Accessible at `http://127.0.0.1:5000/chat`.

### Hardware Interfaces
- Standard keyboard and pointer/touchscreen interfaces.

### Software Interfaces
- RESTful HTTP JSON API endpoints hosted on port 5000 (`/api/chat`, `/api/health`, `/api/admin/*`).
- SQLite filesystem database interface via standard library `sqlite3`.
