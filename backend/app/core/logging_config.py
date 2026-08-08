import logging
import json
import sys
import datetime
from app.core.middleware import get_current_correlation_id

class JSONFormatter(logging.Formatter):
    """
    Structured JSON log formatter mapping records for metrics scraping (Prometheus/Loki).
    """
    def format(self, record: logging.LogRecord) -> str:
        log_payload = {
            "timestamp": datetime.datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "name": record.name,
            "message": record.getMessage(),
            "correlation_id": get_current_correlation_id()
        }
        
        # Include exception tracebacks if present
        if record.exc_info:
            log_payload["exception"] = self.formatException(record.exc_info)
            
        return json.dumps(log_payload)

def setup_structured_logging() -> None:
    """
    Configure global logging configuration to redirect JSON outputs to stdout.
    """
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)
    
    # Clear default handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
        
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(JSONFormatter())
    root_logger.addHandler(handler)
    
    logging.getLogger("app").info("Structured JSON logging initialized successfully.")
