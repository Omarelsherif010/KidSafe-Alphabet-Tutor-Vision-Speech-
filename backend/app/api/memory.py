"""
Memory API endpoints
"""
from fastapi import APIRouter, HTTPException
from ..services.memory_service import get_memory_service

router = APIRouter(prefix="/api/session", tags=["memory"])

@router.get("/{session_id}/memory")
async def get_session_memory(session_id: str):
    """Get session memory and derived state"""
    try:
        memory_service = get_memory_service()
        return {
            "conversation_history": memory_service.get_conversation_history(session_id),
            "derived_state": memory_service.get_derived_state(session_id),
            "session_stats": memory_service.get_session_stats(session_id)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory retrieval failed: {str(e)}")

@router.delete("/{session_id}/memory")
async def clear_session_memory(session_id: str):
    """Clear session memory (parental control)"""
    try:
        memory_service = get_memory_service()
        success = memory_service.clear_session(session_id)
        return {"success": success, "message": "Session memory cleared"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Memory clear failed: {str(e)}")
