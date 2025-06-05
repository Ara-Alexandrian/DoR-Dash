from fastapi import APIRouter

from app.api.endpoints import text, auth, updates, faculty_updates, meetings, users, roster, presentations, registration

api_router = APIRouter()

# Include individual routers
api_router.include_router(text.router, prefix="/text", tags=["text"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(updates.router, prefix="/updates", tags=["updates"])
api_router.include_router(faculty_updates.router, prefix="/faculty-updates", tags=["faculty-updates"])
api_router.include_router(meetings.router, prefix="/meetings", tags=["meetings"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(roster.router, prefix="/roster", tags=["roster"])
api_router.include_router(presentations.router, prefix="/presentations", tags=["presentations"])
api_router.include_router(registration.router, prefix="/registration", tags=["registration"])
# api_router.include_router(requests.router, prefix="/requests", tags=["requests"])
# api_router.include_router(files.router, prefix="/files", tags=["files"])