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

# Extended Hospital Features Blueprints
from .departments import departments_bp
from .wards import wards_bp
from .clinical_orders import clinical_orders_bp
from .communication import communication_bp
from .opd_queue import opd_queue_bp
from .shift_handover import shift_handover_bp
from .encounters import encounters_bp
from .nursing_api import nursing_bp

# Complete Modern Hospital Specialized Blueprints
from .emergency_api import emergency_bp
from .ot_api import ot_bp
from .radiology_api import radiology_bp
from .blood_bank_api import blood_bank_bp
from .support_api import support_bp
from .inventory_api import inventory_bp
from .finance_ext_api import finance_ext_bp
from .people_api import people_bp
from .governance_api import governance_bp
from .patient_portal_api import patient_portal_bp


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

    # Extended hospital workflows
    app.register_blueprint(departments_bp, url_prefix="/api")
    app.register_blueprint(wards_bp, url_prefix="/api")
    app.register_blueprint(clinical_orders_bp, url_prefix="/api")
    app.register_blueprint(communication_bp, url_prefix="/api")
    app.register_blueprint(opd_queue_bp, url_prefix="/api")
    app.register_blueprint(shift_handover_bp, url_prefix="/api")
    app.register_blueprint(encounters_bp, url_prefix="/api")
    app.register_blueprint(nursing_bp, url_prefix="/api")

    # Specialized modules
    app.register_blueprint(emergency_bp, url_prefix="/api")
    app.register_blueprint(ot_bp, url_prefix="/api")
    app.register_blueprint(radiology_bp, url_prefix="/api")
    app.register_blueprint(blood_bank_bp, url_prefix="/api")
    app.register_blueprint(support_bp, url_prefix="/api")
    app.register_blueprint(inventory_bp, url_prefix="/api")
    app.register_blueprint(finance_ext_bp, url_prefix="/api")
    app.register_blueprint(people_bp, url_prefix="/api")
    app.register_blueprint(governance_bp, url_prefix="/api")
    app.register_blueprint(patient_portal_bp, url_prefix="/api")

    # Global Poka-Yoke error handler: serialize domain validation errors cleanly to HTTP 400
    from utils.exception_handler import ValidationError
    from flask import jsonify

    @app.errorhandler(ValidationError)
    def handle_validation_error(err):
        return jsonify({
            "error": "Validation failed",
            "message": str(err.message),
            "field": getattr(err, "field", None),
            "status_code": 400
        }), 400
