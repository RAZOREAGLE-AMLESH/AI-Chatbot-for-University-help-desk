# AI Chatbot for University Help Desk

## Project Description

The **AI Chatbot for University Help Desk** is an intelligent software system designed to provide quick and automated assistance to university students, faculty, and staff. The chatbot can answer frequently asked questions related to university services, academic information, departments, facilities, schedules, and other common queries.

The system aims to reduce the workload of university help-desk staff by providing users with instant responses and making important university information easily accessible.

## Team Members

| Member           | Role        | Responsibility                                   |
| ---------------- | ----------- | ------------------------------------------------ |
| **Anant Singh**  | Team Member | Project development and  Frontend development    | 
| **Agraj Dixit**  | Team Member | Backend, AI integration and project coordination  |
| **Amlesh Singh** | Team Member | Deployment, documentation and testing           |

## Technologies

* HTML
* CSS
* JavaScript
* Python
* AI / Natural Language Processing
* Flask
* Git
* GitHub

## Project Structure

```text
AI-Chatbot-for-University-help-desk/
│
├── README.md
├── docs/
│   ├── SRS/
│   └── UML/
│
├── src/
│   ├── frontend/
│   └── backend/
│
├── test/
│
└── .gitignore
```

## Software Engineering Tools

Software Engineering involves several activities such as requirements analysis, system design, implementation, testing, version control, documentation, and project management.

| Activity                   | Example Tools           |
| -------------------------- | ----------------------- |
| Requirements Documentation | MS Word, Google Docs    |
| UML Design                 | Draw.io, StarUML        |
| Programming                | VS Code                 |
| Version Control            | Git                     |
| Code Repository            | GitHub                  |
| Project Management         | GitHub Projects, Trello |
| API Testing                | Postman                 |
| Testing                    | PyTest                  |
| Documentation              | Markdown, MS Word       |

# Experiment 1: Introduction to Software Engineering Tools and Project Setup

## Aim

To select a real-world software project, form a project team, create a GitHub repository, establish the initial project structure, and demonstrate basic Git and GitHub version-control operations.

## Objectives

* Select an appropriate real-world software project.
* Define project team roles and responsibilities.
* Create a GitHub repository.
* Create the initial project structure.
* Perform basic Git operations such as `add`, `commit`, `push`, `pull`, and `status`.
* Understand collaborative software development using GitHub.

## Tools Required

| Tool                        | Purpose                                      |
| --------------------------- | -------------------------------------------- |
| Visual Studio Code          | Creating and managing project files          |
| Git                         | Version control and tracking project changes |
| GitHub                      | Remote repository and team collaboration     |
| Web Browser                 | Accessing GitHub and managing the repository |
| Git Bash / VS Code Terminal | Executing Git commands                       |

## Introduction

**Git** is a distributed version-control system used to track changes in source code. **GitHub** is a cloud-based platform used to host Git repositories and support collaborative software development.

Version control helps developers maintain project history, collaborate with team members, manage different versions of software, and recover previous versions when required.

### Basic Git Workflow

```text
Working Directory
       ↓
    git add
       ↓
 Staging Area
       ↓
  git commit
       ↓
Local Repository
       ↓
  git push
       ↓
Remote Repository (GitHub)
```

# Problem Statement

Develop an **AI Chatbot for University Help Desk** using Software Engineering principles. Create a GitHub repository for the project, organise the project team, create the initial project structure, and demonstrate essential Git operations.

# Selected Project

**Project Title:** AI Chatbot for University Help Desk

**Domain:** Artificial Intelligence / Education / University Services

**Objective:** Develop an AI-powered chatbot that provides students and university users with quick answers to common questions related to university services, academic information, departments, facilities, schedules, and other help-desk queries.

The chatbot is intended to provide 24/7 assistance and reduce the workload of the university help-desk staff.

# Project Team

| Role                    | Responsibility                                        | Member           |
| ----------------------- | ----------------------------------------------------- | ---------------- |
| Project Coordinator     | Planning, coordination and project management         | **Amlesh Singh** |
| AI / Backend Developer  | Chatbot logic, backend development and AI integration | **Anant Singh**  |
| Frontend Developer      | User interface and chatbot interaction                | **Agraj Dixit**  |
| Documentation & Testing | Documentation, testing and bug reporting, Deployment  | **Amlesh Singh** |

# Project Setup

Create the following project structure in VS Code:

```text
AI-Chatbot-for-University-help-desk/
│
├── README.md
├── docs/
│   ├── SRS/
│   └── UML/
├── src/
│   ├── frontend/
│   └── backend/
├── test/
└── .gitignore
```

## Repository Creation Steps

1. Sign in to GitHub.
2. Create a new repository.
3. Repository name: `AI-Chatbot-for-University-help-desk`
4. Add a `README.md` file.
5. Select **Public** or **Private** visibility.
6. Click **Create Repository**.
7. Add the team members as collaborators.
8. Clone the repository or connect the local project to GitHub.

# Basic Git Commands

| Operation                 | Command                                  |
| ------------------------- | ---------------------------------------- |
| Check Git version         | `git --version`                          |
| Initialize repository     | `git init`                               |
| Check status              | `git status`                             |
| Add files                 | `git add .`                              |
| Commit changes            | `git commit -m "Initial project setup"`  |
| Connect remote repository | `git remote add origin <repository-url>` |
| Rename branch             | `git branch -M main`                     |
| Push changes              | `git push -u origin main`                |
| Pull latest changes       | `git pull origin main`                   |
| View history              | `git log --oneline`                      |

# Version Control Demonstration

## Step 1: Initialize the Local Repository

```bash
git init
```

## Step 2: Check Repository Status

```bash
git status
```

## Step 3: Add Project Files

```bash
git add .
```

## Step 4: Create the First Commit

```bash
git commit -m "Initial project setup"
```

## Step 5: Connect the Local Repository to GitHub

```bash
git remote add origin <repository-url>
```

## Step 6: Push the Project to GitHub

```bash
git branch -M main
git push -u origin main
```

## Step 7: Make a Change

After modifying `README.md` or another project file:

```bash
git add .
git commit -m "Update project documentation"
```

## Step 8: Push the Latest Changes

```bash
git push
```

## Step 9: View Commit History

```bash
git log --oneline
```

## Step 10: Obtain Changes Made by Other Team Members

```bash
git pull origin main
```

# Repository Structure

```text
AI-Chatbot-for-University-help-desk/
│
├── README.md
├── docs/
│   ├── SRS/
│   └── UML/
├── src/
│   ├── frontend/
│   └── backend/
├── test/
└── .gitignore
```

### File and Folder Description

**README.md** – Contains project description, objectives, technologies, team information, and setup details.

**docs/** – Contains project engineering documentation:
  - [Software Requirements Specification (SRS)](docs/SRS/SRS.md)
  - [Use Case Diagram & Specs](docs/UML/use-case-diagram.md)
  - [Class Diagram](docs/UML/class-diagram.md)
  - [Activity Diagram](docs/UML/activity-diagram.md)
  - [Sequence Diagram](docs/UML/sequence-diagram.md)
  - [System Architecture & ER Diagram](docs/UML/system-architecture.md)
  - [Software Testing Documentation](docs/TESTING.md)

**src/** – Contains the source code of the chatbot.

**src/frontend/** – Contains the chatbot user interface.

**src/backend/** – Contains backend logic, API implementation, and AI chatbot functionality.

**test/** – Contains test cases and testing files.

**.gitignore** – Contains files and folders that should not be tracked by Git.

# Expected Outcome

The GitHub repository should contain the initial **AI Chatbot for University Help Desk** project structure, README file, documentation folders, source-code folders, testing folder, and Git version history.

All team members should be able to access the repository and collaborate using GitHub.

# Observation

Git and GitHub provide an effective mechanism for maintaining software versions and collaborating among team members. The Working Directory, Staging Area, Local Repository, and Remote Repository form the basic Git workflow.

Using GitHub allows the project team to maintain a history of changes, collaborate on the chatbot development, and manage different versions of the project.

# Result

The **AI Chatbot for University Help Desk** project was successfully selected and the project team was formed. A GitHub repository was created, the initial project structure was established, and basic Git version-control operations including **add, commit, push, pull, status, and log** were demonstrated successfully.

---

# How to Run the Application

## 1. Prerequisites
- Python 3.10+ (tested on Python 3.14)
- Install required dependencies:
  ```bash
  pip install -r requirements.txt
  ```

## 2. Initialize and Seed the Knowledge Base
Populate the initial KIET FAQ knowledge base into SQLite:
```bash
python src/backend/data/seed_faqs.py
```

## 3. Start the Flask Backend Server
Launch the backend application:
```bash
python src/backend/app.py
```
The application will start on `http://127.0.0.1:5000`.

## 4. Open the Frontend Interface
- **Recommended Method (Via Flask):** Navigate to `http://127.0.0.1:5000/chat` in your web browser while the Flask server is running.
- **Local File Note:** Opening `src/frontend/index.html` directly in a browser (e.g., via `file:///`) may not work correctly because the frontend communicates directly with the Flask backend API (`http://127.0.0.1:5000/api/chat`). Accessing the interface through the Flask route at `http://127.0.0.1:5000/chat` is recommended to ensure seamless API connectivity.

## 5. Run the Automated Test Suite
Execute the 70 PyTest unit and integration tests:
```bash
pytest
```

## 6. Production Deployment Notes

> **Note:** The current project setup is configured for local academic development, testing, and evaluation. Full production deployment has not yet been completed.

When preparing and deploying the application into a production environment, implement the following operational safeguards:
- **Disable Flask Debug Mode:** Run with `DEBUG = False` and set `FLASK_ENV=production` to ensure debug endpoints and detailed stack traces are not exposed.
- **Set a Strong SECRET_KEY:** Configure a cryptographically secure, unpredictable `SECRET_KEY` via environment variables rather than using development defaults.
- **Set a Strong ADMIN_API_KEY:** Assign a strong, confidential administrative API key via `ADMIN_API_KEY` to secure the FAQ management endpoints.
- **Use a Production WSGI Server:** Replace the built-in Flask development server with a battle-tested WSGI/ASGI server (e.g., Waitress on Windows, Gunicorn on Linux) behind a reverse proxy (e.g., Nginx).
- **Enforce HTTPS:** Serve all client-server communications over TLS/HTTPS to protect chatbot conversations, credentials, and API payloads in transit.
