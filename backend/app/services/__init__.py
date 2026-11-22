"""
Business service layer for SmartSOP AI.
"""

from app.services.ticket_service import suggest_sop_for_incident

__all__ = [
    "suggest_sop_for_incident",
]
