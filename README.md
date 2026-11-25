# LANDWISE — National Digital Platform for Land Governance

**LANDWISE** is a centralized national digital research repository, policy collaboration platform, and evidence analytics portal built with **Django**. It empowers researchers, government officials, students, and citizens to discover, review, and collaborate on empirical research in land governance, land reforms, agricultural policy, cadastral titling, rural development, and environmental sustainability.

---

## Core Pillars & Features

### 1. Research Repository & Smart Document Intelligence
- **Upload & Automated Ingestion:** Researchers and administrators can upload PDF/DOCX research papers and policy briefs.
- **Automated PDF Text Extraction:** Extracts full text and page counts using `PyMuPDF` (`fitz`) with a `pypdf` fallback (`repository/utils.py`).
- **Auto-Categorization & Keyword Extraction:** Automatically classifies documents into policy domains and extracts salient keyword tags from extracted text.
- **In-Browser PDF Preview & Citations:** Embedded interactive PDF reader with fullscreen mode, verified download counters, and one-click **APA, MLA, and Chicago** citation generation.
- **Smart Search & Recommendations:** Multi-criteria filtering (category, region, document type, sort order), `Q`-object search ranking, and related-document recommendations.
- **Editorial Approval Workflow:** Dedicated `/repository/approvals/` review queue for platform administrators to approve or request revisions with editorial feedback.

### 2. Multi-Stakeholder Collaboration
- **Threaded Peer Review:** Nested comments and replies on research papers (`collaboration/models.py`).
- **Favourites & Reading Lists:** Save and organize key papers for quick access.
- **Real-Time Notifications:** Unread notification feed for comment replies, document approvals, and revision requests.
- **Collaboration Hub:** Centralized forum highlighting active policy discussions across institutions.

### 3. National Evidence Analytics & Geospatial GIS
- **Chart.js Dashboards:** Interactive visualizations for policy domain distribution, state coverage, monthly ingestion trajectory, and top downloaded papers.
- **Leaflet.js Cadastral Map:** Interactive regional research hub map across India with cluster popups and direct state-filtered repository links.
- **Analytics API:** JSON endpoint at `/analytics/api/stats/`.

### 4. Role-Based Access Control (5 Roles)
- **Platform Admin (`admin`):** Full oversight, document approval/rejection queue, category & user management.
- **Researcher (`researcher`):** Upload documents, track submission status, participate in peer review.
- **Government Official (`official`):** Access priority policy briefs, state cadastral records, and analytics.
- **Student (`student`):** Search, read, download, export citations, and manage saved favourites.
- **Public User (`public`):** Browse and read approved open-access research.

---

## Tech Stack

- **Backend:** Python, Django 6.0 (Clean MVT architecture)
- **Frontend:** HTML5, CSS3, Bootstrap 5, Vanilla JavaScript
- **Database:** SQLite (development, PostgreSQL-ready ORM)
- **PDF Processing:** `pypdf` / `PyMuPDF` (`fitz`)
- **Data Visualization:** Chart.js 4.4.1
- **Geospatial Mapping:** Leaflet.js 1.9.4
- **Typography & Design System:** Playfair Display (headings) + Inter (body) in a custom forest-green (`#1B3A2F`), parchment (`#FAF4E9`), and antique-gold (`#C4A574`) government-tech aesthetic (`static/css/landwise.css`).

---

## Project Structure

```text
├── config/             # Django project settings, root URLs, WSGI/ASGI
├── core/               # Landing page and shared templates
├── accounts/           # Custom Profile model, 5 user roles, auth, dashboards
├── repository/         # Documents, categories, tags, PDF utils, approval workflow
├── collaboration/      # Comments, nested replies, favourites, notifications, hub
├── analytics/          # Chart.js & Leaflet.js dashboard and stats API
├── static/             # CSS (landwise.css), JS, and visual assets
├── templates/          # Base layout and app-specific Django templates
├── manage.py
├── requirements.txt
└── README.md
```

---

## Local Setup & Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/MastMaula1017/landwise-governance-portal.git
   cd landwise-governance-portal
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply database migrations**
   ```bash
   python manage.py migrate
   ```

5. **Seed sample users, research papers, and discussions**
   ```bash
   python manage.py seed_users
   python manage.py seed_repository
   python manage.py seed_collaboration
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```
   Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

---

## Demo Accounts

After running `python manage.py seed_users`, you can sign in with any of the following accounts:

| Role | Username | Password |
| :--- | :--- | :--- |
| **Platform Admin** | `admin` | `admin123` |
| **Researcher** | `researcher` | `researcher123` |
| **Government Official** | `official` | `official123` |
| **Student** | `student` | `student123` |
| **Public Citizen** | `citizen` | `citizen123` |

---

## Key Routes

- `/` — Landing Page
- `/repository/` — Research Repository & Smart Search
- `/repository/upload/` — Upload Research Paper (Researcher/Admin)
- `/repository/approvals/` — Admin Document Review Queue (Admin)
- `/collaboration/` — Collaboration Hub
- `/collaboration/favourites/` — Saved Favourites
- `/collaboration/notifications/` — Notifications Feed
- `/analytics/` — National Evidence Dashboard (Chart.js + Leaflet.js)
- `/accounts/dashboard/` — Role-Aware User Dashboard
- `/accounts/profile/` — User Profile Settings
