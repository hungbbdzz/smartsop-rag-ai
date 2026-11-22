from app.routers.auth import router as auth_router
from app.routers.production_lines import router as production_lines_router
from app.routers.machines import router as machines_router
from app.routers.users import router as users_router
from app.routers.incident_tickets import router as incident_tickets_router
from app.routers.sop_documents import router as sop_documents_router
from app.routers.chat import router as chat_router
from app.routers.dashboard import router as dashboard_router
from app.routers.admin import router as admin_router

__all__ = [
    "auth_router",
    "production_lines_router",
    "machines_router",
    "users_router",
    "incident_tickets_router",
    "sop_documents_router",
    "chat_router",
    "dashboard_router",
    "admin_router",
]
