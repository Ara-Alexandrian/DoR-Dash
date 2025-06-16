"""
Knowledge Base API Endpoints
Admin functions for managing the dynamic terminology learning system
"""

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from pydantic import BaseModel, Field
from typing import List, Dict, Optional, Any
from datetime import datetime
from app.api.endpoints.auth import User, get_current_user, get_admin_user

# Safe import of knowledge base service
try:
    from app.services.knowledge_base import knowledge_service, KnowledgeSnapshot, TerminologyEntry
    KNOWLEDGE_BASE_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Warning: Knowledge base service not available: {e}")
    KNOWLEDGE_BASE_AVAILABLE = False
    
    # Create dummy classes to prevent import errors
    class KnowledgeSnapshot:
        pass
    class TerminologyEntry:
        pass
    knowledge_service = None

router = APIRouter()

class SnapshotRequest(BaseModel):
    force: bool = Field(False, description="Force snapshot even if one was recently taken")

class SnapshotResponse(BaseModel):
    success: bool
    message: str
    snapshot: Optional[Dict[str, Any]] = None

class TerminologyResponse(BaseModel):
    term: str
    category: str
    frequency: int
    confidence_score: float
    contexts: List[str]
    user_approved: bool
    first_seen: datetime
    last_seen: datetime

class KnowledgeStatsResponse(BaseModel):
    total_terms: int
    approved_terms: int
    categories: Dict[str, int]
    top_terms: List[Dict[str, Any]]
    last_snapshot: Optional[datetime]

class TermApprovalRequest(BaseModel):
    action: str = Field(..., description="'approve' or 'reject'")

@router.post("/snapshot", response_model=SnapshotResponse)
async def create_knowledge_snapshot(
    request: SnapshotRequest,
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_admin_user)
):
    """
    Create a snapshot of all submissions to update the knowledge base
    Only admin users can trigger this
    """
    if not KNOWLEDGE_BASE_AVAILABLE:
        raise HTTPException(
            status_code=503,
            detail="Knowledge base service is not available"
        )
    
    try:
        # Run snapshot in background for better performance
        snapshot = await knowledge_service.snapshot_submissions()
        
        return SnapshotResponse(
            success=True,
            message=f"Knowledge base updated! Found {snapshot.new_terms_found} new terms from {snapshot.total_submissions} submissions.",
            snapshot={
                "timestamp": snapshot.timestamp.isoformat(),
                "total_submissions": snapshot.total_submissions,
                "new_terms_found": snapshot.new_terms_found,
                "updated_terms": snapshot.updated_terms,
                "top_terms": snapshot.top_terms[:10]
            }
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to create knowledge snapshot: {str(e)}"
        )

@router.get("/terminology", response_model=List[TerminologyResponse])
async def get_terminology(
    category: Optional[str] = None,
    min_confidence: float = 0.0,
    limit: int = 100,
    current_user: User = Depends(get_admin_user)
):
    """
    Get terminology from the knowledge base
    Filter by category and confidence level
    """
    try:
        vocabulary = knowledge_service.get_domain_vocabulary(
            category=category, 
            min_confidence=min_confidence
        )
        
        # Convert to response format and limit results
        results = []
        for term, entry in list(vocabulary.items())[:limit]:
            results.append(TerminologyResponse(
                term=entry.term,
                category=entry.category,
                frequency=entry.frequency,
                confidence_score=entry.confidence_score,
                contexts=entry.contexts[:3],  # Limit contexts shown
                user_approved=entry.user_approved,
                first_seen=entry.first_seen,
                last_seen=entry.last_seen
            ))
        
        return results
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve terminology: {str(e)}"
        )

@router.get("/stats", response_model=KnowledgeStatsResponse)
async def get_knowledge_stats(
    current_user: User = Depends(get_admin_user)
):
    """
    Get statistics about the knowledge base
    """
    try:
        import sqlite3
        
        with sqlite3.connect(knowledge_service.db_path) as conn:
            # Get total terms
            total_terms = conn.execute('SELECT COUNT(*) FROM terminology').fetchone()[0]
            
            # Get approved terms
            approved_terms = conn.execute(
                'SELECT COUNT(*) FROM terminology WHERE user_approved = TRUE'
            ).fetchone()[0]
            
            # Get categories breakdown
            category_stats = conn.execute('''
                SELECT category, COUNT(*) 
                FROM terminology 
                GROUP BY category 
                ORDER BY COUNT(*) DESC
            ''').fetchall()
            categories = dict(category_stats)
            
            # Get top terms
            top_terms_raw = conn.execute('''
                SELECT term, frequency, confidence_score, category
                FROM terminology 
                ORDER BY frequency DESC 
                LIMIT 15
            ''').fetchall()
            
            top_terms = [
                {
                    "term": term,
                    "frequency": freq,
                    "confidence_score": conf,
                    "category": cat
                }
                for term, freq, conf, cat in top_terms_raw
            ]
            
            # Get last snapshot time
            last_snapshot_raw = conn.execute(
                'SELECT MAX(timestamp) FROM snapshots'
            ).fetchone()[0]
            
            last_snapshot = None
            if last_snapshot_raw:
                last_snapshot = datetime.fromisoformat(last_snapshot_raw)
        
        return KnowledgeStatsResponse(
            total_terms=total_terms,
            approved_terms=approved_terms,
            categories=categories,
            top_terms=top_terms,
            last_snapshot=last_snapshot
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get knowledge base stats: {str(e)}"
        )

@router.post("/terminology/{term}/approve")
async def approve_terminology(
    term: str,
    request: TermApprovalRequest,
    current_user: User = Depends(get_admin_user)
):
    """
    Approve or reject a terminology entry
    This affects the AI refinement suggestions
    """
    try:
        if request.action == "approve":
            success = await knowledge_service.approve_term(term, current_user.id)
            if success:
                return {"success": True, "message": f"Term '{term}' approved"}
            else:
                raise HTTPException(status_code=404, detail="Term not found")
                
        elif request.action == "reject":
            success = await knowledge_service.reject_term(term, current_user.id)
            if success:
                return {"success": True, "message": f"Term '{term}' rejected and removed"}
            else:
                raise HTTPException(status_code=404, detail="Term not found")
        else:
            raise HTTPException(status_code=400, detail="Action must be 'approve' or 'reject'")
            
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to update term: {str(e)}"
        )

@router.post("/analyze-text")
async def analyze_text_terminology(
    text: str,
    current_user: User = Depends(get_admin_user)
):
    """
    Analyze a piece of text for terminology extraction (testing endpoint)
    """
    try:
        terms = knowledge_service.extract_terminology(text)
        quality_issues = knowledge_service.analyze_writing_quality(text)
        
        return {
            "text_length": len(text),
            "word_count": len(text.split()),
            "extracted_terms": terms,
            "writing_quality_issues": quality_issues,
            "domain_context": knowledge_service.get_enhanced_prompt_context("general")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to analyze text: {str(e)}"
        )

@router.get("/enhanced-context/{context_type}")
async def get_enhanced_context(
    context_type: str,
    current_user: User = Depends(get_current_user)
):
    """
    Get enhanced AI prompt context based on learned domain vocabulary
    Available to all users for refinement
    """
    try:
        enhanced_context = knowledge_service.get_enhanced_prompt_context(context_type)
        vocabulary_count = len(knowledge_service.get_domain_vocabulary(min_confidence=0.6))
        
        return {
            "context_type": context_type,
            "enhanced_context": enhanced_context,
            "vocabulary_terms_used": vocabulary_count,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get enhanced context: {str(e)}"
        )