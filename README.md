# Ntsako McGiven Tech Suite

Welcome to the **Ntsako McGiven Tech Suite** repository. This platform serves as a centralized web portfolio and application hub showcasing operational software systems, food safety compliance tools, data analytics platforms, and cybersecurity initiatives designed and developed by **Ntsako Given Banyini**.

---

## 📌 Executive Summary & Key Systems

The suite integrates multiple specialized tech projects into a single responsive Flask-based web infrastructure:

1. **Packhouse Electronic Route File Portal** *(Logistics & Food Safety)*
   - A digital clipboard entry and cold chain compliance tracking system designed for fresh produce export packhouses (e.g., Tzaneen, Musina, Makhado).
   - Validates temperature thresholds ($\le 4.0^\circ\text{C}$) for export compliance.
   - Automatically generates official, downloadable PDF inspection route certificates using `ReportLab`.

2. **EventPro Management System** *(Web Application)*
   - An interactive event management and reservation system built with a localized database architecture for seat allocation, scheduling, and user management.

3. **RIROS Inspection Clipboard Portal** *(Data Analytics)*
   - A multi-view analytics platform that transforms daily paper-based clipboard entries into consolidated weekly operational metrics and KPIs.

4. **Cybersecurity Threat Intelligence Dashboard** *(Defensive Security)*
   - A defensive security framework for real-time log parsing, IP threat scoring, and monitoring server vulnerability metrics.

5. **Digital Forensics Evidence Analyzer** *(Digital Forensics)*
   - An analytical utility for cryptographic hash verification ($\text{SHA-256}$ / $\text{MD5}$), metadata extraction, and chain-of-custody tracking.

---

## 🛠️ Technology Stack

- **Backend Framework:** Python / Flask
- **Database Architecture:** Flask-SQLAlchemy (SQLite locally, PostgreSQL on Render)
- **Form Handling & Validation:** Flask-WTF / WTForms with CSRF protection
- **Document Generation:** ReportLab (PDF Engine)
- **Frontend Technologies:** HTML5, Modern CSS, Jinja2 Templating
- **Security Protocols:** Content Security Policy (CSP), Frame Options (`SAMEORIGIN`), XSS Filtering, CSRF Protection

---

## 🚀 Quick Start Guide (Local Setup)

Follow these steps to run the application on your local development machine:

### 1. Open Terminal and Navigate to the Repository
```bash
cd ~/NtsakoMcGivenTechSuite
```

### 2. Activate the Project Virtual Environment
Ensure Conda does not interfere with project dependencies:
```bash
conda deactivate
source venv/bin/activate
```

### 3. Install Dependencies
Install all required Python libraries:
```bash
pip install -r requirements.txt
```

### 4. Launch the Application
Start the Flask local development server:
```bash
python app.py
```

### 5. Access via Browser
Open your browser and navigate to:
```text
http://127.0.0.1:5000
```
- **Homepage & Projects:** `http://127.0.0.1:5000/`
- **Packhouse Portal Demo:** `http://127.0.0.1:5000/packhouse-portal`

---

## ☁️ Production Deployment

This project is configured for seamless deployment on **Render** using Gunicorn and PostgreSQL.

1. Ensure the `DATABASE_URL` environment variable is attached in your Render dashboard.
2. Build Command: `pip install -r requirements.txt`
3. Start Command: `gunicorn app:app`

---

## 👤 Author & Contact

**Ntsako Given Banyini**  
*Ntsako McGiven Tech Suite*  
- **Portfolio:** [ntsakomcgiventechsuite.onrender.com](https://ntsakomcgiventechsuite.onrender.com)
