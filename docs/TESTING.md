# Software Testing Documentation
## AI Chatbot for University Help Desk (KIET)

---

## 1. Testing Strategy

The quality assurance strategy for the **AI Chatbot for University Help Desk** employs automated multi-level testing to ensure correctness, reliability, security, and institutional data integrity.

### Testing Levels
1. **Unit Testing:** Validates isolated modules, NLP preprocessing routines, sparse vector computations, cosine similarity math, and model-level CRUD operations.
2. **Integration Testing:** Tests interactions between Flask route controllers, service orchestrators, and the SQLite persistence layer using isolated in-memory test databases (`tmp_path`).
3. **API & End-to-End Testing:** Validates HTTP protocol handling, header verification, Content-Type negotiation, JSON payload validation, status codes, and error payloads.
4. **Safety & Fallback Verification:** Ensures that unanswerable, out-of-domain, or fabricated queries strictly trigger institutional fallbacks without hallucinating.

---

## 2. Test Environment & Configuration

- **Framework:** PyTest 9.2.0 (running on Python 3.14.4)
- **Runner Configuration:** `pytest.ini` (`testpaths = test`, `python_files = test_*.py`, `addopts = -v --tb=short`)
- **Isolation Mechanism:** Fixtures in `test/conftest.py` allocate a temporary database file per test function, guaranteeing zero test cross-contamination.

---

## 3. Summary of Test Suites & Test Cases

The test suite contains **70 automated test cases** distributed across 5 test modules:

```text
test/
├── test_health.py      (8 tests)   - Health check, metadata, and root endpoints
├── test_chat.py        (15 tests)  - Input validation, NLP answers, confidence scores, fallbacks
├── test_database.py    (18 tests)  - FAQ & conversation database CRUD operations
├── test_admin.py       (14 tests)  - Admin authentication, authorization, and FAQ management
└── test_nlp.py         (15 tests)  - Tokenization, stopwords, stemming, TF-IDF, and cosine similarity
```

### Module Breakdown and Actual Test Cases

#### A. Health & Root Controller (`test/test_health.py` — 8 Tests)
| Test ID | Function Name | Purpose / Scenario | Expected Status | Actual Result |
|---|---|---|---|---|
| TC-H01 | `test_health_returns_200` | Verifies `/api/health` returns HTTP 200 | 200 OK | PASSED |
| TC-H02 | `test_health_returns_json` | Verifies `/api/health` payload is valid JSON | Valid JSON | PASSED |
| TC-H03 | `test_health_status_ok` | Checks `status == "ok"` field in health JSON | "ok" | PASSED |
| TC-H04 | `test_health_contains_institution` | Checks KIET institution name in metadata | "KIET" present | PASSED |
| TC-H05 | `test_root_returns_200` | Checks GET `/` returns HTTP 200 | 200 OK | PASSED |
| TC-H06 | `test_root_contains_endpoints` | Checks GET `/` lists available API endpoints | Dict present | PASSED |
| TC-H07 | `test_404_for_unknown_route` | Checks non-existent endpoint returns 404 | 404 Not Found | PASSED |
| TC-H08 | `test_404_response_is_json` | Checks 404 error response is JSON formatted | `{"success": false}` | PASSED |

#### B. Chat API Controller (`test/test_chat.py` — 15 Tests)
| Test ID | Function Name | Purpose / Scenario | Expected Status | Actual Result |
|---|---|---|---|---|
| TC-C01 | `test_chat_requires_json_content_type` | Reject non-JSON `text/plain` Content-Type | 415 Unsupported | PASSED |
| TC-C02 | `test_chat_rejects_empty_message` | Reject `{"message": ""}` | 400 Bad Request | PASSED |
| TC-C03 | `test_chat_rejects_whitespace_only_message` | Reject `{"message": "   "}` | 400 Bad Request | PASSED |
| TC-C04 | `test_chat_rejects_missing_message_field` | Reject JSON missing `"message"` key | 400 Bad Request | PASSED |
| TC-C05 | `test_chat_rejects_non_string_message` | Reject integer/boolean message types | 400 Bad Request | PASSED |
| TC-C06 | `test_chat_rejects_too_long_message` | Reject message exceeding 500 characters | 400 Bad Request | PASSED |
| TC-C07 | `test_chat_rejects_invalid_json` | Reject malformed JSON body | 400 Bad Request | PASSED |
| TC-C08 | `test_chat_returns_200_for_valid_message` | Standard valid query processing | 200 OK | PASSED |
| TC-C09 | `test_chat_response_has_required_fields` | Payload contains answer, category, confidence | All fields | PASSED |
| TC-C10 | `test_chat_confidence_is_float` | Confidence is real float in range `[0.0, 1.0]` | Float `0.0..1.0` | PASSED |
| TC-C11 | `test_chat_confidence_is_calculated_not_fabricated` | Gibberish yields low similarity score | `< 0.5` | PASSED |
| TC-C12 | `test_chat_unknown_query_returns_fallback` | Unanswerable query returns safe fallback text | Safe fallback | PASSED |
| TC-C13 | `test_chat_session_id_returned` | Auto-generated session ID on first contact | UUID returned | PASSED |
| TC-C14 | `test_chat_session_id_preserved` | Reuse provided session ID for subsequent turns | Same session | PASSED |
| TC-C15 | `test_chat_empty_knowledge_base_returns_graceful_message` | Handle empty FAQ table gracefully | Graceful reply | PASSED |

#### C. Database Models (`test/test_database.py` — 18 Tests)
| Test ID | Function Name | Purpose / Scenario | Expected Result | Actual Result |
|---|---|---|---|---|
| TC-D01 | `test_create_faq` | Insert FAQ into SQLite and check returned ID | ID > 0 | PASSED |
| TC-D02 | `test_get_faq_by_id` | Fetch specific FAQ record by primary key | Correct row | PASSED |
| TC-D03 | `test_get_faq_by_id_not_found` | Lookup non-existent ID (99999) | `None` | PASSED |
| TC-D04 | `test_get_all_faqs_empty` | Query empty FAQ table | `[]` | PASSED |
| TC-D05 | `test_get_all_faqs_with_records` | Query populated FAQ table | All records | PASSED |
| TC-D06 | `test_update_faq` | Update FAQ answer without altering question | Partial update | PASSED |
| TC-D07 | `test_update_faq_not_found` | Update non-existent FAQ record | `None` | PASSED |
| TC-D08 | `test_delete_faq` | Remove FAQ record | `True` & gone | PASSED |
| TC-D09 | `test_delete_faq_not_found` | Delete non-existent record | `False` | PASSED |
| TC-D10 | `test_search_faqs` | Search FAQs by substring keyword | Filtered list | PASSED |
| TC-D11 | `test_count_faqs` | Accurate count of records | Row count | PASSED |
| TC-D12 | `test_faq_has_created_at` | Non-empty ISO timestamp upon creation | ISO string | PASSED |
| TC-D13 | `test_is_verified_default_zero` | Default verification status is 0 | `is_verified == 0` | PASSED |
| TC-D14 | `test_create_conversation` | Create conversation session | Session created | PASSED |
| TC-D15 | `test_get_existing_conversation` | Retrieve existing session without duplicating | Same ID | PASSED |
| TC-D16 | `test_save_and_retrieve_messages` | Verify chronological message storage | 2 messages | PASSED |
| TC-D17 | `test_message_confidence_stored` | Store and retrieve float confidence value | Exact float | PASSED |
| TC-D18 | `test_count_conversations` | Accurate count of conversation sessions | Count matches | PASSED |

#### D. Admin Controller & Security (`test/test_admin.py` — 14 Tests)
| Test ID | Function Name | Purpose / Scenario | Expected Status | Actual Result |
|---|---|---|---|---|
| TC-A01 | `test_admin_without_key_returns_401` | Request without `X-Admin-Key` header | 401 Unauthorized | PASSED |
| TC-A02 | `test_admin_with_wrong_key_returns_403` | Request with incorrect admin key | 403 Forbidden | PASSED |
| TC-A03 | `test_admin_with_correct_key_returns_200` | Authorized admin request | 200 OK | PASSED |
| TC-A04 | `test_list_faqs_empty` | List FAQs on fresh database | `[]` count 0 | PASSED |
| TC-A05 | `test_create_faq_success` | Create FAQ via admin API | 201 Created | PASSED |
| TC-A06 | `test_create_faq_missing_field` | Reject FAQ payload missing required fields | 400 Bad Request | PASSED |
| TC-A07 | `test_get_single_faq` | Fetch single FAQ via admin API | 200 OK | PASSED |
| TC-A08 | `test_get_nonexistent_faq` | Fetch non-existent FAQ ID | 404 Not Found | PASSED |
| TC-A09 | `test_update_faq` | Update FAQ fields via PUT | 200 OK | PASSED |
| TC-A10 | `test_update_nonexistent_faq` | Update non-existent FAQ ID (checks 404 before validation) | 404 Not Found | PASSED |
| TC-A11 | `test_delete_faq` | Delete FAQ via DELETE | 200 OK | PASSED |
| TC-A12 | `test_delete_nonexistent_faq` | Delete non-existent FAQ ID | 404 Not Found | PASSED |
| TC-A13 | `test_search_faqs` | Admin keyword filter (`?search=admission`) | Filtered JSON | PASSED |
| TC-A14 | `test_admin_stats` | Retrieve total counts of FAQs, sessions, messages | Aggregate stats | PASSED |

#### E. NLP Engine & TF-IDF (`test/test_nlp.py` — 15 Tests)
| Test ID | Function Name | Purpose / Scenario | Expected Result | Actual Result |
|---|---|---|---|---|
| TC-N01 | `test_tokenise_basic` | Basic sentence tokenization | List of tokens | PASSED |
| TC-N02 | `test_stopwords_removed` | Standard English stopwords filtered out | No stopwords | PASSED |
| TC-N03 | `test_lowercasing` | Case insensitivity normalization | All lowercase | PASSED |
| TC-N04 | `test_empty_string` | Handle empty string input | `[]` | PASSED |
| TC-N05 | `test_none_input` | Handle `None` input safely | `[]` | PASSED |
| TC-N06 | `test_special_chars_removed` | Punctuation and symbols stripped | Clean tokens | PASSED |
| TC-N07 | `test_fit_builds_index` | Build TF-IDF index over corpus | `fitted == True` | PASSED |
| TC-N08 | `test_query_returns_results` | Query returns ranked candidate list | Non-empty list | PASSED |
| TC-N09 | `test_query_returns_tuples` | Candidates returned as `(index, score)` | Valid tuples | PASSED |
| TC-N10 | `test_similar_query_has_high_score` | Relevant query yields positive similarity | `score > 0` | PASSED |
| TC-N11 | `test_unrelated_query_has_lower_score` | Unrelated query scores below relevant query | Lower score | PASSED |
| TC-N12 | `test_scores_sorted_descending` | Candidates ranked in descending score order | Strict descending | PASSED |
| TC-N13 | `test_empty_corpus` | Query on unfitted/empty corpus | `[]` | PASSED |
| TC-N14 | `test_cosine_similarity_identical_vectors` | Self-similarity of identical vectors | `1.0` | PASSED |
| TC-N15 | `test_cosine_similarity_zero_vector` | Cosine similarity with empty vector | `0.0` | PASSED |

---

## 4. Current Test Suite Execution Result

Executed using PyTest 9.2.0 on Python 3.14.4:

```text
============================= test session starts =============================
platform win32 -- Python 3.14.4, pytest-9.2.0, pluggy-1.7.0 -- C:\Users\acer\AppData\Local\Programs\Python\Python314\python.exe
cachedir: .pytest_cache
rootdir: C:\Users\acer\Desktop\sdp_project
configfile: pytest.ini
testpaths: test
collecting ... collected 70 items

test/test_admin.py::TestAdminAuthentication::test_admin_without_key_returns_401 PASSED [  1%]
test/test_admin.py::TestAdminAuthentication::test_admin_with_wrong_key_returns_403 PASSED [  2%]
test/test_admin.py::TestAdminAuthentication::test_admin_with_correct_key_returns_200 PASSED [  4%]
test/test_admin.py::TestAdminFAQCRUD::test_list_faqs_empty PASSED        [  5%]
test/test_admin.py::TestAdminFAQCRUD::test_create_faq_success PASSED     [  7%]
test/test_admin.py::TestAdminFAQCRUD::test_create_faq_missing_field PASSED [  8%]
test/test_admin.py::TestAdminFAQCRUD::test_get_single_faq PASSED         [ 10%]
test/test_admin.py::TestAdminFAQCRUD::test_get_nonexistent_faq PASSED    [ 11%]
test/test_admin.py::TestAdminFAQCRUD::test_update_faq PASSED             [ 12%]
test/test_admin.py::TestAdminFAQCRUD::test_update_nonexistent_faq PASSED [ 14%]
test/test_admin.py::TestAdminFAQCRUD::test_delete_faq PASSED             [ 15%]
test/test_admin.py::TestAdminFAQCRUD::test_delete_nonexistent_faq PASSED [ 17%]
test/test_admin.py::TestAdminFAQCRUD::test_search_faqs PASSED            [ 18%]
test/test_admin.py::TestAdminFAQCRUD::test_admin_stats PASSED            [ 20%]
test/test_chat.py::TestChatEndpointValidation::test_chat_requires_json_content_type PASSED [ 21%]
test/test_chat.py::TestChatEndpointValidation::test_chat_rejects_empty_message PASSED [ 22%]
test/test_chat.py::TestChatEndpointValidation::test_chat_rejects_whitespace_only_message PASSED [ 24%]
test/test_chat.py::TestChatEndpointValidation::test_chat_rejects_missing_message_field PASSED [ 25%]
test/test_chat.py::TestChatEndpointValidation::test_chat_rejects_non_string_message PASSED [ 27%]
test/test_chat.py::TestChatEndpointValidation::test_chat_rejects_too_long_message PASSED [ 28%]
test/test_chat.py::TestChatEndpointValidation::test_chat_rejects_invalid_json PASSED [ 30%]
test/test_chat.py::TestChatEndpointResponses::test_chat_returns_200_for_valid_message PASSED [ 31%]
test/test_chat.py::TestChatEndpointResponses::test_chat_response_has_required_fields PASSED [ 32%]
test/test_chat.py::TestChatEndpointResponses::test_chat_confidence_is_float PASSED [ 34%]
test/test_chat.py::TestChatEndpointResponses::test_chat_confidence_is_calculated_not_fabricated PASSED [ 35%]
test/test_chat.py::TestChatEndpointResponses::test_chat_unknown_query_returns_fallback PASSED [ 37%]
test/test_chat.py::TestChatEndpointResponses::test_chat_session_id_returned PASSED [ 38%]
test/test_chat.py::TestChatEndpointResponses::test_chat_session_id_preserved PASSED [ 40%]
test/test_chat.py::TestChatEndpointResponses::test_chat_empty_knowledge_base_returns_graceful_message PASSED [ 41%]
test/test_database.py::TestFAQModel::test_create_faq PASSED              [ 42%]
test/test_database.py::TestFAQModel::test_get_faq_by_id PASSED           [ 44%]
test/test_database.py::TestFAQModel::test_get_faq_by_id_not_found PASSED [ 45%]
test/test_database.py::TestFAQModel::test_get_all_faqs_empty PASSED      [ 47%]
test/test_database.py::TestFAQModel::test_get_all_faqs_with_records PASSED [ 48%]
test/test_database.py::TestFAQModel::test_update_faq PASSED              [ 50%]
test/test_database.py::TestFAQModel::test_update_faq_not_found PASSED    [ 51%]
test/test_database.py::TestFAQModel::test_delete_faq PASSED              [ 52%]
test/test_database.py::TestFAQModel::test_delete_faq_not_found PASSED    [ 54%]
test/test_database.py::TestFAQModel::test_search_faqs PASSED             [ 55%]
test/test_database.py::TestFAQModel::test_count_faqs PASSED              [ 57%]
test/test_database.py::TestFAQModel::test_faq_has_created_at PASSED      [ 58%]
test/test_database.py::TestFAQModel::test_is_verified_default_zero PASSED [ 60%]
test/test_database.py::TestConversationModel::test_create_conversation PASSED [ 61%]
test/test_database.py::TestConversationModel::test_get_existing_conversation PASSED [ 62%]
test/test_database.py::TestConversationModel::test_save_and_retrieve_messages PASSED [ 64%]
test/test_database.py::TestConversationModel::test_message_confidence_stored PASSED [ 65%]
test/test_database.py::TestConversationModel::test_count_conversations PASSED [ 67%]
test/test_health.py::TestHealthEndpoint::test_health_returns_200 PASSED  [ 68%]
test/test_health.py::TestHealthEndpoint::test_health_returns_json PASSED [ 70%]
test/test_health.py::TestHealthEndpoint::test_health_status_ok PASSED    [ 71%]
test/test_health.py::TestHealthEndpoint::test_health_contains_institution PASSED [ 72%]
test/test_root.py::TestHealthEndpoint::test_root_returns_200 PASSED    [ 74%]
test/test_health.py::TestHealthEndpoint::test_root_contains_endpoints PASSED [ 75%]
test/test_health.py::TestHealthEndpoint::test_404_for_unknown_route PASSED [ 77%]
test/test_health.py::TestHealthEndpoint::test_404_response_is_json PASSED [ 78%]
test/test_nlp.py::TestPreprocessing::test_tokenise_basic PASSED          [ 80%]
test/test_nlp.py::TestPreprocessing::test_stopwords_removed PASSED       [ 81%]
test/test_nlp.py::TestPreprocessing::test_lowercasing PASSED             [ 82%]
test/test_nlp.py::TestPreprocessing::test_empty_string PASSED            [ 84%]
test/test_nlp.py::TestPreprocessing::test_none_input PASSED              [ 85%]
test/test_nlp.py::TestPreprocessing::test_special_chars_removed PASSED   [ 87%]
test/test_nlp.py::TestTFIDFEngine::test_fit_builds_index PASSED          [ 88%]
test/test_nlp.py::TestTFIDFEngine::test_query_returns_results PASSED     [ 90%]
test/test_nlp.py::TestTFIDFEngine::test_query_returns_tuples PASSED      [ 91%]
test/test_nlp.py::TestTFIDFEngine::test_similar_query_has_high_score PASSED [ 92%]
test/test_nlp.py::TestTFIDFEngine::test_unrelated_query_has_lower_score PASSED [ 94%]
test/test_nlp.py::TestTFIDFEngine::test_scores_sorted_descending PASSED  [ 95%]
test/test_nlp.py::TestTFIDFEngine::test_empty_corpus PASSED              [ 97%]
test/test_nlp.py::TestTFIDFEngine::test_cosine_similarity_identical_vectors PASSED [ 98%]
test/test_nlp.py::TestTFIDFEngine::test_cosine_similarity_zero_vector PASSED [100%]

============================= 70 passed in 4.37s ==============================
```

**Status:** All 70 test cases correspond directly to actual functions in `test/`, and all 70 pass.
