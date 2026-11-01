from .auth_routes import auth_bp
from .dashboard_routes import dashboard_bp
from .log_routes import log_bp
from .incident_routes import incident_bp
from .simulation_routes import simulation_bp
from .threat_routes import threat_bp
from .analytics_routes import analytics_bp
from .report_routes import report_bp

__all__ = [
    "auth_bp",
    "dashboard_bp",
    "log_bp",
    "incident_bp",
    "simulation_bp",
    "threat_bp",
    "analytics_bp",
    "report_bp",
]
