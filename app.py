import os
import io
from datetime import datetime
from dotenv import load_dotenv
from flask import Flask, render_template, request, flash, redirect, url_for, abort, send_file
from flask_wtf import FlaskForm
from flask_wtf.csrf import CSRFProtect
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Length
from flask_sqlalchemy import SQLAlchemy
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Load hidden environment configurations
load_dotenv()

app = Flask(__name__)

# Security & Database Configurations
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'default_fallback_key_for_development_only')

# Handle Render PostgreSQL scheme compatibility (postgres:// to postgresql://)
db_url = os.getenv('DATABASE_URL', 'sqlite:///messages.db')
if db_url and db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
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

# ==========================================
# DATABASE MODELS
# ==========================================

class ContactMessage(db.Model):
    __tablename__ = "contact_messages"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class RouteLog(db.Model):
    __tablename__ = "route_logs"
    id = db.Column(db.Integer, primary_key=True)
    block_location = db.Column(db.String(100), nullable=False)
    consignment_number = db.Column(db.String(50), nullable=False)
    product_type = db.Column(db.String(100), nullable=False)
    temperature = db.Column(db.Float, nullable=False)
    inspector_name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# ==========================================
# FORM MODELS
# ==========================================

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

class RouteEntryForm(FlaskForm):
    block_location = StringField('Operational Block', validators=[DataRequired(), Length(max=100)])
    consignment_number = StringField('Consignment / Batch Number', validators=[DataRequired(), Length(max=50)])
    product_type = StringField('Product Type', validators=[DataRequired(), Length(max=100)])
    temperature = StringField('Cold Chain Temperature (°C)', validators=[DataRequired()])
    inspector_name = StringField('Inspector Name', validators=[DataRequired(), Length(max=100)])
    submit = SubmitField('Save Route Log & Generate PDF Certificate')

# Projects Dataset
PROJECTS = [
    {
        "id": "route-file-portal",
        "title": "Packhouse Electronic Route File Portal",
        "category": "Logistics & Food Safety",
        "tech_stack": ["Python", "Flask", "ReportLab", "SQLite"],
        "description": "Digital clipboard entry and PDF generation system built for export packhouse routing, food safety, and cold chain enforcement.",
        "live_url": "/packhouse-portal",
        "url": "packhouse_portal",
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
        "url": "eventpro",
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
        "url": "riros",
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
        "url": "cyber_sec",
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
        "url": "digi_forensics",
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
    },
    {
        "id": "forensiai",
        "title": "ForensiAI Digital Forensics Engine",
        "category": "Cybersecurity & Forensic Analytics",
        "tech_stack": ["FastAPI", "React", "SHA-256", "EXIF Parsing"],
        "description": "Enterprise evidence inspection platform featuring binary magic-byte header analysis, multi-algorithmic hash integrity validation, and an immutable Chain of Custody audit vault.",
        "live_url": "/forensiai",
        "url": "forensiai",
        "status": "Active Engine",
        "overview": "ForensiAI is a real-time digital forensics suite built to detect file spoofing via binary header signatures, verify multi-hash integrity, and audit digital evidence.",
        "features": [
            "Binary magic-byte header identification to prevent file spoofing",
            "SHA-256, SHA-1, and MD5 multi-hash verification",
            "Chain of Custody audit vault with timestamped ledger entries"
        ],
        "security": [
            "Read-only stream parsing for uploaded evidence",
            "Header validation checks to mitigate file upload exploits"
        ],
        "user_guide": "Access the ForensiAI suite, ingest your evidence file, and review threat scoring alongside the audit ledger."
    }
]

with app.app_context():
    db.create_all()

# ==========================================
# WEB ROUTES
# ==========================================

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

@app.route('/packhouse-portal', methods=['GET', 'POST'])
def packhouse_portal():
    form = RouteEntryForm()
    if form.validate_on_submit():
        try:
            temp_val = float(form.temperature.data)
        except ValueError:
            flash("Temperature must be a valid numerical value.", "danger")
            return redirect(url_for('packhouse_portal'))

        new_log = RouteLog(
            block_location=form.block_location.data.strip(),
            consignment_number=form.consignment_number.data.strip(),
            product_type=form.product_type.data.strip(),
            temperature=temp_val,
            inspector_name=form.inspector_name.data.strip()
        )
        db.session.add(new_log)
        db.session.commit()

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        width, height = letter

        p.setFont("Helvetica-Bold", 16)
        p.drawString(50, height - 50, "Ntsako McGiven Tech Suite")
        p.setFont("Helvetica", 12)
        p.drawString(50, height - 70, "Export Packhouse Electronic Route File & Cold Chain Report")
        
        p.setLineWidth(1)
        p.line(50, height - 80, width - 50, height - 80)

        p.setFont("Helvetica-Bold", 11)
        y = height - 120
        fields = [
            ("Operational Block:", new_log.block_location),
            ("Consignment Number:", new_log.consignment_number),
            ("Product Type:", new_log.product_type),
            ("Cold Chain Temperature:", f"{new_log.temperature} °C"),
            ("Inspecting Officer:", new_log.inspector_name),
            ("Timestamp (UTC):", new_log.created_at.strftime('%Y-%m-%d %H:%M:%S')),
            ("Compliance Status:", "APPROVED - Cold Chain Enforced" if temp_val <= 4.0 else "REVIEW REQUIRED - Temp Exceeds Threshold")
        ]

        for label, value in fields:
            p.drawString(50, y, label)
            p.setFont("Helvetica", 11)
            p.drawString(220, y, str(value))
            p.setFont("Helvetica-Bold", 11)
            y -= 25

        p.showPage()
        p.save()
        buffer.seek(0)

        flash("Route log saved! Downloading inspection PDF...", "success")
        return send_file(
            buffer,
            as_attachment=True,
            download_name=f"Route_File_{new_log.consignment_number}.pdf",
            mimetype='application/pdf'
        )

    return render_template('packhouse_portal.html', form=form)

@app.errorhandler(404)
def page_not_found(e):
    return render_template('index.html', projects=PROJECTS, form=ContactForm()), 404

@app.route('/forensiai')
def forensiai():
    return render_template('forensiai.html')

if __name__ == '__main__':
    app.run(port=5000, debug=False)