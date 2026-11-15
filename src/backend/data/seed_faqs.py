"""
data/seed_faqs.py — KIET Knowledge Base Seed Data
AI Chatbot for University Help Desk | KIET Deemed to be University

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
IMPORTANT DATA INTEGRITY & AUDIT NOTICE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Institutional Status:
  KIET (established in 1998, Delhi-NCR, Ghaziabad) achieved Autonomous
  status in 2024 and was conferred Deemed-to-be-University status under
  Section 3 of the UGC Act, 1956 in November 2025.
  Degrees for university programmes are conferred by KIET Deemed to be University.
  Earlier batches enrolled under AKTU affiliation remain governed by
  AKTU academic and examination regulations until degree completion.

Accreditation:
  NAAC Grade 'A+' (CGPA 3.05 on 4-point scale, Cycle-1).

Admissions:
  Admissions are processed directly via the KIET Admissions Portal:
  B.Tech pathways: JEE (Main) / KIET Entrance Examination (KEE) / 10+2 PCM Composite Merit.

Fields:
    is_verified  = 1  — verified from official KIET source
    is_verified  = 0  — unverified / variable (must be checked with official portal)
    source_url        — direct link to official KIET / regulatory page

The following information is intentionally NOT hardcoded:
  ✗ Exact semester examination schedules / date sheets
  ✗ Exact fee breakdowns by year/programme
  ✗ Individual faculty personal contact details

Usage:
    python seed_faqs.py                    # updates/syncs existing FAQs without deleting history
    python seed_faqs.py --clear            # clears all FAQs first, then seeds
    python seed_faqs.py --db /path/to.db  # operates on a specific DB file
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
"""

import sys
import os

# Allow running this script directly from src/backend/data/
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from models import init_db, get_connection
from models.faq import create_faq, update_faq, get_all_faqs


# ──────────────────────────────────────────────
# Seed dataset (Audited for KIET Deemed to be University)
# Each entry: (question, answer, category, source_url, is_verified)
# ──────────────────────────────────────────────

SEED_FAQS = [

    # ── About KIET ────────────────────────────────────────────────────────

    (
        "What is KIET Group of Institutions?",
        "KIET (established in 1998 in Ghaziabad, Delhi-NCR) is a leading "
        "higher-education institution originally founded as Krishna Institute "
        "of Engineering and Technology. In 2024, it achieved autonomous status, "
        "and in November 2025, it was conferred Deemed-to-be-University status "
        "under Section 3 of the UGC Act, 1956, becoming KIET Deemed to be University. "
        "It offers undergraduate, postgraduate, and doctoral programmes in "
        "engineering, pharmacy, management, and computer applications. Earlier "
        "batches enrolled under AKTU affiliation complete their degrees under AKTU regulations.",
        "About KIET",
        "https://www.kiet.edu/about-kiet",
        1,
    ),
    (
        "Where is KIET located?",
        "KIET Group of Institutions is located at:\n"
        "13 Km Milestone, Delhi-Meerut Expressway,\n"
        "Ghaziabad – 201 206, Uttar Pradesh, India.\n\n"
        "It is easily accessible from Delhi via the Delhi-Meerut Expressway.",
        "About KIET",
        "https://www.kiet.edu/contact-us",
        1,
    ),
    (
        "When was KIET established?",
        "KIET was established in 1998. It has grown into a premier technical "
        "institution in Delhi-NCR, now recognized as KIET Deemed to be University.",
        "About KIET",
        "https://www.kiet.edu/about-kiet",
        1,
    ),
    (
        "What is the full form of KIET?",
        "KIET historically stands for Krishna Institute of Engineering and Technology "
        "(later known as KIET Group of Institutions). Following its conferment of "
        "Deemed-to-be-University status under Section 3 of the UGC Act, 1956, it is "
        "officially designated as KIET Deemed to be University.",
        "About KIET",
        "https://www.kiet.edu/about-kiet",
        1,
    ),
    (
        "Which university is KIET affiliated to?",
        "KIET is now a Deemed-to-be-University under Section 3 of the UGC Act, 1956 "
        "(KIET Deemed to be University) and awards its own degrees for university "
        "programmes. Previously, it operated as an autonomous institute affiliated "
        "with Dr. A.P.J. Abdul Kalam Technical University (AKTU), Lucknow. Earlier "
        "batches enrolled under the AKTU affiliation framework continue to be governed "
        "by AKTU regulations until degree completion.",
        "About KIET",
        "https://www.kiet.edu/about-kiet",
        1,
    ),
    (
        "Is KIET approved by AICTE?",
        "Yes, technical programmes at KIET are approved by the All India Council "
        "for Technical Education (AICTE), New Delhi, and recognized under UGC norms.",
        "About KIET",
        "https://www.kiet.edu/about-kiet",
        1,
    ),
    (
        "What is KIET's NAAC grade?",
        "KIET is accredited with an 'A+' Grade by the National Assessment and "
        "Accreditation Council (NAAC). In its current accreditation cycle (Cycle-3, "
        "2022–2027), KIET achieved a CGPA of 3.32 on a 4-point scale, having previously "
        "secured a CGPA of 3.05 in its second cycle. For official accreditation documents, "
        "visit: https://www.kiet.edu/about-kiet",
        "About KIET",
        "https://www.kiet.edu/about-kiet",
        1,
    ),

    # ── Programmes Offered ────────────────────────────────────────────────

    (
        "What B.Tech programmes does KIET offer?",
        "KIET offers B.Tech (Bachelor of Technology) programmes in the following branches:\n"
        "• Computer Science and Engineering (CSE)\n"
        "• Information Technology (IT)\n"
        "• Electronics and Communication Engineering (ECE)\n"
        "• Electrical Engineering (EE)\n"
        "• Mechanical Engineering (ME)\n"
        "• Civil Engineering (CE)\n"
        "• Computer Science and Engineering (AI & ML)\n"
        "• Computer Science and Engineering (Data Science)\n\n"
        "For the complete and updated list, visit: https://www.kiet.edu/programmes",
        "Programmes",
        "https://www.kiet.edu/programmes",
        1,
    ),
    (
        "Does KIET offer M.Tech programmes?",
        "Yes, KIET offers M.Tech (Master of Technology) programmes in various "
        "specialisations. For the current list of M.Tech programmes and eligibility, "
        "please visit: https://www.kiet.edu/programmes",
        "Programmes",
        "https://www.kiet.edu/programmes",
        1,
    ),
    (
        "Does KIET offer MBA?",
        "Yes, KIET offers an MBA (Master of Business Administration) programme. "
        "For details on specialisations, intake, and eligibility, visit: "
        "https://www.kiet.edu/programmes",
        "Programmes",
        "https://www.kiet.edu/programmes",
        1,
    ),
    (
        "Does KIET offer MCA?",
        "Yes, KIET offers an MCA (Master of Computer Applications) programme. "
        "For admission details and curriculum, visit: https://www.kiet.edu/programmes",
        "Programmes",
        "https://www.kiet.edu/programmes",
        1,
    ),

    # ── Admissions ────────────────────────────────────────────────────────

    (
        "How can I get admission to KIET?",
        "Admission to KIET Deemed to be University is conducted through the official "
        "admissions portal (https://www.kiet.edu/admissions).\n\n"
        "Depending on the programme and seat quota, admission pathways include:\n"
        "• For B.Tech / Undergraduate Technical Programmes: JEE (Main) score, on-campus "
        "KIET Entrance Examination (KEE), CUET (UG) scores, or 10+2 qualifying-examination "
        "PCM composite merit.\n"
        "• For Other Programmes (B.Pharm, MBA, MCA, M.Tech): CUET (UG/PG), CAT, MAT, "
        "GATE, GPAT, or qualifying academic merit as applicable per programme guidelines.\n\n"
        "Steps to apply:\n"
        "1. Register online on the KIET admissions portal (kiet.edu).\n"
        "2. Submit the application with relevant entrance examination or academic scores.\n"
        "3. Complete seat selection, counseling/evaluation, and document verification.\n"
        "4. Pay the admission fee.\n\n"
        "(Note: Earlier batches were admitted via AKTU state counseling; current admissions follow KIET University procedures). Official details: https://www.kiet.edu/admissions",
        "Admissions",
        "https://www.kiet.edu/admissions",
        1,
    ),
    (
        "What is the eligibility for B.Tech admission at KIET?",
        "To be eligible for B.Tech admission at KIET:\n"
        "• Passed or appearing in 10+2 (Class XII) with Physics and Mathematics as compulsory subjects, plus Chemistry or an approved technical vocational subject.\n"
        "• Minimum 45% aggregate marks (40% for reserved category candidates) in required subjects.\n"
        "• Valid score in an accepted pathway: JEE (Main), on-campus KIET Entrance Examination (KEE), CUET (UG), or 10+2 qualifying-examination composite merit, depending on the branch and admission quota.\n\n"
        "For specific programme guidelines and annual admission updates, visit: https://www.kiet.edu/admissions",
        "Admissions",
        "https://www.kiet.edu/admissions",
        1,
    ),
    (
        "What documents are required for KIET admission?",
        "Documents typically required for admission verification at KIET include:\n"
        "• Class X mark sheet and certificate (proof of date of birth)\n"
        "• Class XII mark sheet and passing certificate\n"
        "• Entrance scorecard (JEE Main / KEE / CUET / other qualifying exam)\n"
        "• Seat allotment / offer letter from KIET (or AKTU allotment letter for students admitted under state counseling)\n"
        "• Category / Caste certificate (if applicable)\n"
        "• Transfer Certificate (TC) and Migration Certificate\n"
        "• Aadhaar card / Government photo identity proof\n"
        "• Recent passport-size photographs\n\n"
        "Because document requirements may vary by programme, always confirm the latest checklist at: https://www.kiet.edu/admissions",
        "Admissions",
        "https://www.kiet.edu/admissions",
        0,   # unverified flag as requirements can vary by admission cycle
    ),

    # ── Contact & General Help Desk ───────────────────────────────────────

    (
        "What is the contact number for KIET?",
        "You can contact KIET at:\n"
        "📞 +91-120-2988300\n"
        "📧 info@kiet.edu\n\n"
        "For department-specific contacts, visit: https://www.kiet.edu/contact-us",
        "Contact",
        "https://www.kiet.edu/contact-us",
        1,
    ),
    (
        "What is KIET's official website?",
        "The official website of KIET is:\n"
        "🌐 https://www.kiet.edu/",
        "Contact",
        "https://www.kiet.edu/",
        1,
    ),
    (
        "What is the email address of KIET?",
        "The official email address of KIET is:\n"
        "📧 info@kiet.edu\n\n"
        "For specific enquiries, refer to individual department pages on the website.",
        "Contact",
        "https://www.kiet.edu/contact-us",
        1,
    ),

    # ── Facilities ────────────────────────────────────────────────────────

    (
        "Does KIET have a hostel?",
        "Yes, KIET provides hostel facilities for both boys and girls with "
        "mess, Wi-Fi, and security amenities. For availability, regulations, "
        "and fee details, contact the hostel administration or visit: "
        "https://www.kiet.edu/facilities",
        "Facilities",
        "https://www.kiet.edu/facilities",
        1,
    ),
    (
        "Does KIET have a library?",
        "Yes, KIET has a well-equipped central library with a vast collection "
        "of technical books, print/e-journals, research databases, and reading "
        "halls. For details, visit: https://www.kiet.edu/facilities",
        "Facilities",
        "https://www.kiet.edu/facilities",
        1,
    ),
    (
        "What sports facilities are available at KIET?",
        "KIET provides extensive sports and recreation infrastructure including "
        "cricket, football, basketball, badminton courts, table tennis, and gymnasium "
        "facilities. For more information, visit: https://www.kiet.edu/facilities",
        "Facilities",
        "https://www.kiet.edu/facilities",
        1,
    ),
    (
        "Is there a canteen or food facility at KIET?",
        "Yes, KIET has cafeterias and food outlets on campus providing hygienic "
        "meals, refreshments, and snacks for students and staff. "
        "For details, visit: https://www.kiet.edu/facilities",
        "Facilities",
        "https://www.kiet.edu/facilities",
        1,
    ),

    # ── Examinations ──────────────────────────────────────────────────────

    (
        "How do I check my examination timetable?",
        "Examination timetables depend on your academic registration:\n"
        "• KIET Deemed to be University / Autonomous Batches: Timetables for Mid Semester Examinations (MSE), Pre-University Exams (PUE), and End Semester Examinations (ESE) are scheduled by the KIET Examination Cell and published on the KIET Student ERP portal and official site (https://www.kiet.edu/).\n"
        "• Earlier Batches under AKTU: Students enrolled under AKTU affiliation must check the examination schedule on the AKTU website: https://aktu.ac.in/ under 'Examination' → 'Date Sheet'.\n\n"
        "⚠️ Dates change each semester — always consult your ERP portal and official notices.",
        "Examinations",
        "https://www.kiet.edu/",
        1,
    ),
    (
        "How do I check my exam results?",
        "How to check semester examination results and download grade sheets:\n"
        "• KIET Deemed to be University / Autonomous Batches: Semester results and provisional grade sheets are issued by the KIET Examination Cell and accessed online through the KIET Student ERP portal (https://www.kiet.edu/erp/) using your student login credentials.\n"
        "• Earlier Batches under AKTU Affiliation: Results for students enrolled under AKTU regulations are published on the AKTU OneView portal (https://erp.aktu.ac.in/) by entering your AKTU roll number.\n\n"
        "For mark sheet distribution, grade corrections, or result discrepancies, contact the KIET Examination Cell or visit the ERP portal: https://www.kiet.edu/erp/",
        "Examinations",
        "https://www.kiet.edu/erp/",
        0,
    ),
    (
        "How do I apply for a re-evaluation of my exam paper?",
        "Re-evaluation and grievance procedures depend on your governing university:\n"
        "• KIET Deemed to be University / Autonomous Batches: Re-evaluation, scrutiny, and viewing of evaluated answer sheets are managed by the KIET Examination Cell under the Controller of Examinations. Applications must be submitted through the KIET ERP portal or Examination Cell within the announced window after results.\n"
        "• Earlier Batches under AKTU: Students registered under AKTU must apply for Challenge Evaluation / Scrutiny online via the AKTU portal (https://erp.aktu.ac.in/) within the timeline specified by AKTU.\n\n"
        "Contact the KIET Examination Cell for specific forms, timelines, and guidelines.",
        "Examinations",
        "https://www.kiet.edu/",
        1,
    ),

    # ── Fee Payment ───────────────────────────────────────────────────────

    (
        "How do I pay my semester fees?",
        "Semester fee payments at KIET can be completed through:\n"
        "• Online Payment: Via net banking, UPI, debit/credit cards through the KIET student ERP portal (MasterSoft / student fee portal).\n"
        "• Demand Draft (DD): Drawn in favour of 'KIET GROUP OF INSTITUTIONS' payable at Ghaziabad / Delhi.\n\n"
        "For the exact fee amount, payment window, and due date, check your student ERP account or visit: https://www.kiet.edu/admissions",
        "Fees",
        "https://www.kiet.edu/admissions",
        1,
    ),
    (
        "Where can I find information about KIET fee structure?",
        "The official fee structure for KIET programmes is available on the "
        "KIET admissions page. Fee amounts are subject to annual revision "
        "and must be verified directly from the official source:\n"
        "🔗 https://www.kiet.edu/admissions\n\n"
        "⚠️ This chatbot does not store hardcoded fee amounts as they are updated annually.",
        "Fees",
        "https://www.kiet.edu/admissions",
        1,
    ),

    # ── Scholarships ──────────────────────────────────────────────────────

    (
        "Are scholarships available at KIET?",
        "Yes, various scholarships are available to KIET students, including:\n"
        "• Uttar Pradesh State Government Scholarships (UP Scholarship Portal)\n"
        "• Merit-based institutional scholarships\n"
        "• SC/ST/OBC category financial assistance schemes\n"
        "• National Scholarship Portal (NSP) central government schemes\n\n"
        "For eligibility criteria and application deadlines, visit the student scholarship section on: https://www.kiet.edu/",
        "Scholarships",
        "https://www.kiet.edu/",
        1,
    ),

    # ── Placements ────────────────────────────────────────────────────────

    (
        "Does KIET have a placement cell?",
        "Yes, KIET has a dedicated Training and Placement Cell (CRPC / T&P Cell) "
        "that coordinates campus recruitment, industry internships, and training "
        "for students. Top multinational and core companies recruit annually. "
        "For placement records and recruiter details, visit: https://www.kiet.edu/placements",
        "Placements",
        "https://www.kiet.edu/placements",
        1,
    ),
    (
        "How do I register for campus placements?",
        "To register for campus recruitment at KIET:\n"
        "1. Log in to the KIET placement / ERP portal with your student credentials.\n"
        "2. Complete your academic profile, verify semester marks, and upload your resume.\n"
        "3. Register for upcoming company recruitment drives announced by the T&P Cell.\n\n"
        "For guidance, contact the Training and Placement Cell: https://www.kiet.edu/placements",
        "Placements",
        "https://www.kiet.edu/placements",
        1,
    ),

    # ── ERP / Student Portal ──────────────────────────────────────────────

    (
        "How do I access the KIET student ERP portal?",
        "The KIET student ERP portal (MasterSoft / institutional ERP) can be accessed "
        "via the official KIET website. Log in using your assigned student roll number / "
        "registration ID and password. For portal access issues, contact the campus IT "
        "helpdesk or visit: https://www.kiet.edu/",
        "Student Portal",
        "https://www.kiet.edu/",
        1,
    ),
    (
        "I forgot my ERP portal password. What should I do?",
        "If you forgot your KIET ERP portal password:\n"
        "1. Click the 'Forgot Password' link on the ERP login screen.\n"
        "2. Follow the recovery link sent to your registered email or phone.\n"
        "3. If you still cannot log in, visit the campus IT helpdesk or contact the registrar office.\n\n"
        "Official portal: https://www.kiet.edu/",
        "Student Portal",
        "https://www.kiet.edu/",
        1,
    ),

    # ── Anti-Ragging ──────────────────────────────────────────────────────

    (
        "What is the anti-ragging policy at KIET?",
        "KIET strictly enforces a zero-tolerance policy against ragging in accordance "
        "with UGC and AICTE regulations. Ragging in any form is prohibited on and "
        "off campus. Incidents can be reported to:\n"
        "• The KIET Anti-Ragging Committee & Proctorial Board\n"
        "• National Anti-Ragging 24x7 Helpline: 1800-180-5522\n"
        "• UGC Anti-Ragging Portal: https://antiragging.in/\n\n"
        "Violators face strict disciplinary and legal action.",
        "Student Welfare",
        "https://www.kiet.edu/",
        1,
    ),

    # ── Fallback / help pointers ──────────────────────────────────────────

    (
        "How do I contact the KIET help desk?",
        "You can reach the KIET help desk through the following official channels:\n"
        "📞 Phone : +91-120-2988300\n"
        "📧 Email : info@kiet.edu\n"
        "🌐 Web   : https://www.kiet.edu/contact-us\n\n"
        "For specific department queries, consult the respective department page.",
        "Contact",
        "https://www.kiet.edu/contact-us",
        1,
    ),
]


# ──────────────────────────────────────────────
# Seeding and Synchronization functions
# ──────────────────────────────────────────────

def sync_faqs(db_path: str = None) -> tuple[int, int]:
    """
    Synchronize existing FAQ records in the database with audited SEED_FAQS.
    Updates existing records in place without modifying conversations or messages.
    Inserts any new FAQs that do not yet exist.

    Args:
        db_path : Path to SQLite database file.

    Returns:
        (updated_count, inserted_count)
    """
    init_db(db_path)
    existing = get_all_faqs(db_path)
    # Map lowercase question to existing record
    existing_by_question = {f["question"].strip().lower(): f for f in existing}

    updated = 0
    inserted = 0

    for question, answer, category, source_url, is_verified in SEED_FAQS:
        q_key = question.strip().lower()
        if q_key in existing_by_question:
            faq_id = existing_by_question[q_key]["id"]
            update_faq(
                faq_id=faq_id,
                updates={
                    "question": question,
                    "answer": answer,
                    "category": category,
                    "source_url": source_url,
                    "is_verified": is_verified,
                },
                db_path=db_path,
            )
            updated += 1
        else:
            create_faq(
                question=question,
                answer=answer,
                category=category,
                source_url=source_url,
                is_verified=is_verified,
                db_path=db_path,
            )
            inserted += 1

    return updated, inserted


def seed(db_path: str = None, clear: bool = False) -> int:
    """
    Populate or synchronize the FAQ table with KIET seed data.

    Args:
        db_path : Path to the SQLite database file. Uses default if None.
        clear   : If True, delete all existing FAQs before inserting.

    Returns:
        Number of records affected/inserted.
    """
    init_db(db_path)

    if clear:
        conn = get_connection(db_path)
        try:
            conn.execute("DELETE FROM faq")
            conn.commit()
            print("  Cleared existing FAQs.")
        finally:
            conn.close()

        inserted = 0
        for question, answer, category, source_url, is_verified in SEED_FAQS:
            create_faq(
                question=question,
                answer=answer,
                category=category,
                source_url=source_url,
                is_verified=is_verified,
                db_path=db_path,
            )
            inserted += 1
        return inserted
    else:
        updated, inserted = sync_faqs(db_path)
        return updated + inserted


# ──────────────────────────────────────────────
# CLI entry point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    clear_flag = "--clear" in sys.argv
    db_arg = None
    for i, arg in enumerate(sys.argv):
        if arg == "--db" and i + 1 < len(sys.argv):
            db_arg = sys.argv[i + 1]

    print("=" * 55)
    print("  KIET AI Chatbot — FAQ Database Synchronizer & Seeder")
    print("=" * 55)
    if db_arg:
        print(f"  Database : {db_arg}")
    if clear_flag:
        print("  Mode     : CLEAR then seed")
    else:
        print("  Mode     : Safe In-Place Sync (preserves history)")

    count = seed(db_path=db_arg, clear=clear_flag)
    print(f"  ✅ Processed {count} FAQ records.")
    print("=" * 55)
