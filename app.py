import os
from flask import Flask, render_template, request, flash, redirect, url_for, abort
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from dotenv import load_dotenv

# Load hidden environment configurations
load_dotenv()

app = Flask(__name__)

# Security & Database Configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_fallback_key_for_development_only')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///messages.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# SECURITY HEADER: Set basic Content Security Policy & Frame options on all responses
@app.after_request
def set_security_headers(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response

# Database Model for Messages
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# Form Model
class ContactForm(FlaskForm):
    name = StringField('Your Name', validators=[
        DataRequired(message="Please enter your name."),
        Length(min=2, max=50, message="Name must be between 2 and 50 characters.")
    ])
    email = StringField('Your Email', validators=[
        DataRequired(message="Please enter your email address."),
        Email(message="Please provide a valid email address.")
    ])
    message = TextAreaField('Your Message', validators=[
        DataRequired(message="Please type your message."),
        Length(min=10, max=1000, message="Message must be between 10 and 1000 characters.")
    ])
    submit = SubmitField('Send Message')

# Projects Dataset
PROJECTS = [
    {
        "id": "route-file-portal",
        "title": "Packhouse Electronic Route File Portal",
        "category": "Logistics & Food Safety",
        "tech_stack": ["Python", "Flask", "ReportLab", "SQLite"],
        "description": "Digital clipboard entry and PDF generation system built for export packhouse routing, food safety, and cold chain enforcement.",
        "live_url": "http://127.0.0.1:5001",
        "status": "Active / Local",
        "overview": "The Packhouse Electronic Route File Portal digitizes paper-based routing and quality control forms across citrus and fresh produce export facilities in regional operational blocks (Tzaneen, Musina, Makhado).",
        "features": [
            "Automated PDF inspection summary sheet creation using ReportLab",
            "Real-time validation of temperature logs for cold chain enforcement",
            "Electronic route file tracking per consignment batch",
            "Export certification metadata verification"
        ],
        "security": [
            "Jinja2 auto-escaping to block Cross-Site Scripting (XSS)",
            "CSRF token validation on form inputs",
            "Input sanitization for packhouse batch numbers and temperatures"
        ],
        "user_guide": "Select your operational block, enter consignment details, log cold chain metrics, and click 'Generate Route File PDF'."
    },
    {
        "id": "eventpro",
        "title": "EventPro Management System",
        "category": "Web Application",
        "tech_stack": ["PHP", "PDO", "MySQL", "phpMyAdmin"],
        "description": "Online event management and reservation system constructed with a localized database architecture.",
        "live_url": "#",
        "status": "Prototype",
        "overview": "EventPro is a robust web application designed for booking, managing, and tracking events through an interactive localized web interface.",
        "features": [
            "User registration and role-based access control",
            "Event schedule creation and venue assignment",
            "Automated booking confirmations and seat availability tracking",
            "Relational database design managed via phpMyAdmin"
        ],
        "security": [
            "Prepared Statements with PHP PDO to eliminate SQL Injection",
            "Password hashing using password_hash() with bcrypt",
            "Session validation on protected admin endpoints"
        ],
        "user_guide": "Log in to the dashboard, browse available events, and select seats to generate an automated reservation token."
    },
    {
        "id": "riros",
        "title": "RIROS Inspection Clipboard Portal",
        "category": "Data Analytics",
        "tech_stack": ["Python", "Streamlit", "SQLite"],
        "description": "Multi-view analytics web interface automating daily regional operations and weekly export inspection reporting metrics.",
        "live_url": "#",
        "status": "Active",
        "overview": "RIROS (Daily Inspection Clipboard Entry Portal) turns daily manual inspection data into interactive visual analytics, simplifying weekly reporting across regional hubs.",
        "features": [
            "Interactive Streamlit dashboard with custom filtering",
            "Automatic weekly consolidation of inspector clipboard entries",
            "KPI tracking for food safety standards and compliance rates",
            "Exportable summaries in CSV and tabular formats"
        ],
        "security": [
            "Parametrized SQLite queries to secure local database reads",
            "Restricted execution scope in local Python environment"
        ],
        "user_guide": "Upload clipboard log files or submit daily totals, then use the date filter to generate regional weekly metrics."
    },
    {
        "id": "cyber-sec",
        "title": "Cybersecurity Threat Intelligence Dashboard",
        "category": "Cybersecurity Initiative",
        "tech_stack": ["Python", "Network Security", "Flask"],
        "description": "Upcoming security monitoring framework focused on vulnerability tracking, secure log parsing, and defensive network posture analysis.",
        "live_url": "#",
        "status": "Future Project",
        "overview": "A planned defensive security tool designed to ingest application logs, detect anomalous request patterns, and monitor web server vulnerability metrics.",
        "features": [
            "Real-time HTTP request log parsing and IP threat scoring",
            "Automated alert triggers for failed login spikes or brute-force attempts",
            "Visual threat matrix dashboard"
        ],
        "security": [
            "Sanitized input parsing for raw server log files",
            "Encrypted local storage for audit logs"
        ],
        "user_guide": "Currently in design phase. Future release will allow uploading server logs for security analysis."
    },
    {
        "id": "digi-forensics",
        "title": "Digital Forensics Evidence Analyzer",
        "category": "Digital Forensics",
        "tech_stack": ["Python", "File System Analysis", "Hashing"],
        "description": "Planned analytical tool designed for safe file integrity verification, metadata extraction, and secure audit trail preservation.",
        "live_url": "#",
        "status": "Future Project",
        "overview": "An upcoming digital forensics software utility engineered to calculate cryptographic hashes and extract file metadata for legal compliance and chain of custody tracking.",
        "features": [
            "SHA-256 and MD5 cryptographic hash generation for file integrity verification",
            "EXIF and filesystem metadata extraction",
            "Immutable audit log report generation"
        ],
        "security": [
            "Read-only file handling to preserve evidence state",
            "Cryptographic hashing to detect unauthorized file tampering"
        ],
        "user_guide": "Currently in design phase. Future release will accept target file paths for automated digital forensic auditing."
    }
]

with app.app_context():
    db.create_all()

@app.route('/', methods=['GET', 'POST'])
def home():
    form = ContactForm()
    if form.validate_on_submit():
        new_message = ContactMessage(
            name=form.name.data.strip(),
            email=form.email.data.strip(),
            message=form.message.data.strip()
        )
        db.session.add(new_message)
        db.session.commit()
        flash("Thank you! Your message has been securely recorded.", "success")
        return redirect(url_for('home'))
    return render_template('index.html', projects=PROJECTS, form=form)

@app.route('/project/<project_id>')
def project_detail(project_id):
    project = next((p for p in PROJECTS if p["id"] == project_id), None)
    if not project:
        abort(404)
    return render_template('project_detail.html', project=project)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', projects=PROJECTS, form=ContactForm()), 404

if __name__ == '__main__':
    app.run(port=5000, debug=False)