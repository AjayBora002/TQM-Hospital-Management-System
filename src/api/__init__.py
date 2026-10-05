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
