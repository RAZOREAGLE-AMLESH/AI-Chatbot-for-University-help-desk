"""
test/test_knowledge_base_audit.py — Regression Tests for Audited KIET Knowledge Base
AI Chatbot for University Help Desk | KIET Deemed to be University

Verifies that:
1. Institutional status reflects Deemed-to-be-University status (UGC Act Section 3).
2. Historical AKTU affiliation is accurately distinguished for earlier batches.
3. Admissions procedures include JEE Main, KEE, and direct portal applications.
4. Examination timetables, results, and re-evaluation differentiate university/autonomous
   governance from earlier AKTU batches.
5. NAAC 'A+' accreditation is verified.
6. Variable document requirements safely remain marked is_verified=0.
7. Database sync preserves record integrity without deleting history.
"""

import os
import pytest
from services.chatbot_service import get_answer, refresh_index
from data.seed_faqs import sync_faqs, SEED_FAQS
from models.faq import count_faqs, get_all_faqs


@pytest.fixture(scope="function")
def audited_test_db(tmp_path):
    """Provide a database populated with audited seed FAQs."""
    db_file = str(tmp_path / "test_audited_kb.db")
    os.environ["DATABASE_PATH"] = db_file
    sync_faqs(db_file)
    refresh_index(db_file)
    yield db_file
    if "DATABASE_PATH" in os.environ:
        del os.environ["DATABASE_PATH"]


class TestInstitutionalStatusKnowledge:
    """Tests verifying current institutional status and AKTU distinction."""

    def test_affiliation_query_reflects_deemed_university_and_aktu(self, audited_test_db):
        """Query about university affiliation must state Deemed-to-be-University and preserve AKTU context."""
        res = get_answer("Which university is KIET affiliated to?", db_path=audited_test_db)
        assert res["success"] is True
        assert res["confidence"] >= 0.5
        assert "deemed-to-be-university" in res["answer"].lower()
        assert "aktu" in res["answer"].lower()
        assert res["is_verified"] is True

    def test_about_kiet_reflects_deemed_university(self, audited_test_db):
        """Query 'What is KIET?' must state Deemed to be University and 1998 establishment."""
        res = get_answer("What is KIET?", db_path=audited_test_db)
        assert res["success"] is True
        assert "deemed to be university" in res["answer"].lower() or "deemed-to-be-university" in res["answer"].lower()
        assert "1998" in res["answer"]
        assert res["is_verified"] is True

    def test_full_form_mentions_current_designation(self, audited_test_db):
        """Query for full form should mention Krishna Institute of Engineering and Technology and university designation."""
        res = get_answer("What is the full form of KIET?", db_path=audited_test_db)
        assert res["success"] is True
        assert "krishna institute of engineering and technology" in res["answer"].lower()
        assert "deemed to be university" in res["answer"].lower() or "deemed-to-be-university" in res["answer"].lower()


class TestAdmissionsKnowledge:
    """Tests verifying updated admission pathways."""

    def test_admission_process_mentions_kiet_portal_and_kee(self, audited_test_db):
        """Admission query must reference direct KIET admissions and examination pathways including CUET."""
        res = get_answer("How can I get admission to KIET?", db_path=audited_test_db)
        assert res["success"] is True
        assert "kiet.edu/admissions" in res["answer"].lower()
        assert "kee" in res["answer"] or "kiet entrance examination" in res["answer"].lower()
        assert "jee" in res["answer"].lower()
        assert "cuet" in res["answer"].lower()
        assert res["is_verified"] is True

    def test_btech_eligibility_criteria(self, audited_test_db):
        """B.Tech eligibility query must reference 10+2 PCM requirements."""
        res = get_answer("What is the eligibility for B.Tech admission at KIET?", db_path=audited_test_db)
        assert res["success"] is True
        assert "10+2" in res["answer"] or "class xii" in res["answer"].lower()
        assert "physics" in res["answer"].lower() and "mathematics" in res["answer"].lower()
        assert res["is_verified"] is True

    def test_document_requirements_marked_unverified(self, audited_test_db):
        """Variable admission document requirements must be marked is_verified=False."""
        res = get_answer("What documents are required for KIET admission?", db_path=audited_test_db)
        assert res["success"] is True
        assert res["is_verified"] is False
        assert "kiet.edu/admissions" in res["answer"]


class TestExaminationsKnowledge:
    """Tests verifying examination, results, and re-evaluation distinctions."""

    def test_exam_timetable_distinguishes_university_from_aktu(self, audited_test_db):
        """Examination timetable answer must distinguish university/autonomous batches from AKTU."""
        res = get_answer("How do I check my examination timetable?", db_path=audited_test_db)
        assert res["success"] is True
        assert "examination cell" in res["answer"].lower()
        assert "aktu" in res["answer"].lower()
        assert res["is_verified"] is True

    def test_exam_results_distinguishes_erp_from_oneview(self, audited_test_db):
        """Results query must explain KIET ERP for university students, AKTU OneView for AKTU students, and be unverified."""
        res = get_answer("How do I check my exam results?", db_path=audited_test_db)
        assert res["success"] is True
        assert "erp" in res["answer"].lower()
        assert "oneview" in res["answer"].lower() or "aktu" in res["answer"].lower()
        assert "kiet.edu/erp" in res["source"]
        assert res["is_verified"] is False

    def test_exact_examination_results_query_high_confidence(self, audited_test_db):
        """Exact query 'How do I check my examination results?' must achieve high confidence and correct ERP source."""
        res = get_answer("How do I check my examination results?", db_path=audited_test_db)
        assert res["success"] is True
        assert res["confidence"] >= 0.95  # Significantly improved from 0.67
        assert "kiet.edu/erp" in res["source"]
        assert "grade sheet" in res["answer"].lower() or "grade sheets" in res["answer"].lower()
        assert res["is_verified"] is False

    def test_re_evaluation_explains_internal_and_aktu_routes(self, audited_test_db):
        """Re-evaluation query must explain examination cell procedure and AKTU procedure."""
        res = get_answer("How do I apply for a re-evaluation of my exam paper?", db_path=audited_test_db)
        assert res["success"] is True
        assert "examination cell" in res["answer"].lower()
        assert "aktu" in res["answer"].lower()
        assert res["is_verified"] is True


class TestAccreditationAndDatabaseSync:
    """Tests for NAAC accreditation and database synchronization."""

    def test_naac_accreditation_is_verified_a_plus(self, audited_test_db):
        """NAAC grade query must state Grade A+, current CGPA 3.32, previous CGPA 3.05, and be verified."""
        res = get_answer("What is KIET NAAC grade?", db_path=audited_test_db)
        assert res["success"] is True
        assert "a+" in res["answer"].lower()
        assert "3.32" in res["answer"]
        assert "3.05" in res["answer"]
        assert res["is_verified"] is True

    def test_fee_faqs_exist_and_verified(self, audited_test_db):
        """Fee payment and structure queries must be verified and direct to official portal."""
        res_pay = get_answer("How do I pay my semester fees?", db_path=audited_test_db)
        assert res_pay["success"] is True
        assert "erp" in res_pay["answer"].lower()
        assert "demand draft" in res_pay["answer"].lower()
        assert res_pay["is_verified"] is True

        res_struct = get_answer("Where can I find information about KIET fee structure?", db_path=audited_test_db)
        assert res_struct["success"] is True
        assert "admissions" in res_struct["source"].lower()
        assert res_struct["is_verified"] is True

    def test_sync_faqs_idempotency(self, audited_test_db):
        """Repeated synchronization must not duplicate FAQ rows."""
        initial_count = count_faqs(audited_test_db)
        updated, inserted = sync_faqs(audited_test_db)
        assert inserted == 0
        assert count_faqs(audited_test_db) == initial_count
        assert count_faqs(audited_test_db) == len(SEED_FAQS)
