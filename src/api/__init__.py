"""
__init__.py -- Registration and exports for all HMS REST API blueprints
"""
from .dashboard import dashboard_bp
from .patients import patients_bp
from .doctors import doctors_bp
from .appointments import appointments_bp
from .rooms import rooms_bp
from .staff import staff_bp
from .medicines import medicines_bp
from .bills import bills_bp
from .audit import audit_bp
from .auth import auth_bp
from .admissions import admissions_bp
from .prescriptions import prescriptions_bp
from .export import export_bp
from .system import system_bp
from .lab_tests import lab_tests_bp
from .triage import triage_bp
from .purchase_orders import purchase_orders_bp
from .quality_audit import quality_audit_bp

def register_api(app):
    """
    Registers all modular API blueprints onto the Flask application
    under the '/api' URL prefix.
    """
    app.register_blueprint(dashboard_bp, url_prefix="/api")
    app.register_blueprint(patients_bp, url_prefix="/api")
    app.register_blueprint(doctors_bp, url_prefix="/api")
    app.register_blueprint(appointments_bp, url_prefix="/api")
    app.register_blueprint(rooms_bp, url_prefix="/api")
    app.register_blueprint(staff_bp, url_prefix="/api")
    app.register_blueprint(medicines_bp, url_prefix="/api")
    app.register_blueprint(bills_bp, url_prefix="/api")
    app.register_blueprint(audit_bp, url_prefix="/api")
    app.register_blueprint(auth_bp, url_prefix="/api")
    app.register_blueprint(admissions_bp, url_prefix="/api")
    app.register_blueprint(prescriptions_bp, url_prefix="/api")
    app.register_blueprint(export_bp, url_prefix="/api")
    app.register_blueprint(system_bp, url_prefix="/api")
    app.register_blueprint(lab_tests_bp, url_prefix="/api")
    app.register_blueprint(triage_bp, url_prefix="/api")
    app.register_blueprint(purchase_orders_bp, url_prefix="/api")
    app.register_blueprint(quality_audit_bp, url_prefix="/api")




