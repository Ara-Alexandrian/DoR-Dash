from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
import httpx
import json
import re
import asyncio
from app.core.config import settings
from app.api.endpoints.auth import User, get_current_user

# Safe import of knowledge base service
try:
    from app.services.knowledge_base import knowledge_service
    KNOWLEDGE_BASE_AVAILABLE = True
except Exception as e:
    print(f"⚠️  Warning: Knowledge base service not available in text endpoint: {e}")
    KNOWLEDGE_BASE_AVAILABLE = False
    knowledge_service = None

router = APIRouter()

class TextRefinementRequest(BaseModel):
    text: str = Field(..., min_length=1, description="Text to refine and proofread")
    context: Optional[str] = Field(None, description="Context: research_progress, challenges, goals, announcements, or general")

class TextRefinementResponse(BaseModel):
    original_text: str
    refined_text: str
    suggestions: List[str]
    word_count_original: int
    word_count_refined: int
    improvements_made: List[str] = []

# Minimal formatting prompt templates - focus on basic cleanup and organization only
ACADEMIC_PROMPTS = {
    "research_progress": """Clean up this text with minimal formatting. Only fix obvious issues and add basic structure. Do NOT expand or rewrite content.

Rules:
- Fix grammar/spelling errors only
- Add bullet points ONLY if there are clearly separate items
- Use **bold** sparingly for key terms only
- Keep text shorter or same length as original
- Do NOT add emojis or fancy formatting
- Do NOT change wording or add new content

TEXT: {text}

Respond with JSON:
{{"refined_text": "cleaned version", "suggestions": ["grammar fix", "structure tip", "clarity note"]}}""",

    "challenges": """Clean up this challenges text with minimal formatting. Fix basic issues only, do NOT expand content.

Rules:
- Fix grammar/spelling errors only
- Add bullet points ONLY if there are clearly separate challenges
- Keep text shorter or same length as original
- Do NOT add emojis or fancy formatting
- Do NOT change wording or add explanations

TEXT: {text}

Respond with JSON:
{{"refined_text": "cleaned version", "suggestions": ["grammar fix", "structure tip", "clarity note"]}}""",

    "goals": """Clean up these goals/steps with minimal formatting. Fix basic issues only, do NOT expand content.

Rules:
- Fix grammar/spelling errors only
- Add numbered list ONLY if there are clearly separate steps
- Keep text shorter or same length as original
- Do NOT add emojis or fancy formatting
- Do NOT change wording or add details

TEXT: {text}

Respond with JSON:
{{"refined_text": "cleaned version", "suggestions": ["grammar fix", "structure tip", "clarity note"]}}""",

    "announcements": """Clean up this announcement with minimal formatting. Fix basic issues only, do NOT expand content.

Rules:
- Fix grammar/spelling errors only
- Add bullet points ONLY if there are clearly separate items
- Keep text shorter or same length as original
- Do NOT add emojis or fancy formatting
- Do NOT change wording or add emphasis

TEXT: {text}

Respond with JSON:
{{"refined_text": "cleaned version", "suggestions": ["grammar fix", "structure tip", "clarity note"]}}""",

    "general": """Clean up this text with minimal formatting. Fix basic issues only, do NOT expand content.

Rules:
- Fix grammar/spelling errors only
- Add basic structure ONLY if clearly needed
- Keep text shorter or same length as original
- Do NOT add emojis or fancy formatting
- Do NOT change wording or add content

TEXT: {text}

Respond with JSON:
{{"refined_text": "cleaned version", "suggestions": ["grammar fix", "structure tip", "clarity note"]}}"""
}

def determine_context(text: str) -> str:
    """Automatically determine context based on content"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ["progress", "experiment", "result", "methodology", "data", "analysis"]):
        return "research_progress"
    elif any(word in text_lower for word in ["challenge", "problem", "difficult", "obstacle", "issue"]):
        return "challenges"
    elif any(word in text_lower for word in ["goal", "plan", "next", "future", "objective", "aim", "will"]):
        return "goals"
    elif any(word in text_lower for word in ["announce", "deadline", "important", "notice", "reminder"]):
        return "announcements"
    else:
        return "general"

def analyze_improvements(original: str, refined: str) -> List[str]:
    """Analyze what improvements were made"""
    improvements = []
    
    orig_words = len(original.split())
    refined_words = len(refined.split())
    
    if refined_words != orig_words:
        if refined_words > orig_words:
            improvements.append(f"Expanded content (+{refined_words - orig_words} words)")
        else:
            improvements.append(f"Condensed content (-{orig_words - refined_words} words)")
    
    if original.count('.') != refined.count('.'):
        improvements.append("Improved sentence structure")
    
    if original.count(',') != refined.count(','):
        improvements.append("Enhanced punctuation")
    
    return improvements if improvements else ["Text clarity enhanced"]

@router.post("/refine-text", response_model=TextRefinementResponse)
async def refine_text(
    request: TextRefinementRequest,
    current_user: User = Depends(get_current_user)
):
    """
    Enhanced text refinement using Mistral 7B on CPU/RAM
    Optimized for academic and research writing
    """
    # Input validation
    if len(request.text.strip()) < 10:
        raise HTTPException(status_code=400, detail="Text must be at least 10 characters long")
    
    if len(request.text) > 2000:
        raise HTTPException(status_code=400, detail="Text must be less than 2000 characters for optimal processing")
    
    try:
        # Determine context and select appropriate prompt
        context = request.context or determine_context(request.text)
        prompt_template = ACADEMIC_PROMPTS.get(context, ACADEMIC_PROMPTS["general"])
        
        # Get enhanced domain context from knowledge base (if available)
        enhanced_context = ""
        if KNOWLEDGE_BASE_AVAILABLE and knowledge_service:
            try:
                enhanced_context = knowledge_service.get_enhanced_prompt_context(context)
            except Exception as e:
                print(f"⚠️  Warning: Could not get enhanced context: {e}")
        
        # Enhance the prompt with learned domain vocabulary
        enhanced_prompt = prompt_template.format(text=request.text)
        if enhanced_context and enhanced_context.strip():
            enhanced_prompt += enhanced_context + "\n\nPlease use this domain knowledge to provide more accurate and contextually appropriate suggestions."
        
        prompt = enhanced_prompt
        
        # Call Ollama API with Gemma 3 4B for more conservative formatting
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(
                settings.OLLAMA_API_URL,
                json={
                    "model": "gemma3:4b",  # Use Gemma 3 4B for better, more conservative responses
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.2,      # Slightly higher for more natural minimal fixes
                        "top_p": 0.7,
                        "top_k": 15,
                        "num_ctx": 512,          # Even smaller context to limit elaboration
                        "num_predict": 200,      # Much shorter responses to prevent expansion
                        "repeat_penalty": 1.1,
                        "num_thread": 4,         # Optimize CPU thread usage
                        "num_gpu": 0            # Force CPU-only processing
                    }
                }
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error calling Ollama API: {response.text}"
                )
            
            # Extract the result
            result = response.json()
            completion = result.get("response", "")
            
            # Improved JSON extraction with better parsing
            try:
                import json
                import re
                
                # Clean up the response - remove any prefixes or explanations
                cleaned_response = completion.strip()
                
                # Try multiple strategies to extract JSON
                json_data = None
                
                # Strategy 1: Look for JSON block with proper delimiters
                json_match = re.search(r'```json\s*(\{.*?\})\s*```', cleaned_response, re.DOTALL)
                if json_match:
                    try:
                        json_data = json.loads(json_match.group(1))
                    except json.JSONDecodeError:
                        pass
                
                # Strategy 2: Look for any JSON object in the response
                if not json_data:
                    json_match = re.search(r'(\{[^{}]*"refined_text"[^{}]*\})', cleaned_response, re.DOTALL)
                    if json_match:
                        try:
                            json_data = json.loads(json_match.group(1))
                        except json.JSONDecodeError:
                            pass
                
                # Strategy 3: Try parsing the entire response as JSON
                if not json_data:
                    try:
                        json_data = json.loads(cleaned_response)
                    except json.JSONDecodeError:
                        pass
                
                # If we successfully parsed JSON, use it
                if json_data and isinstance(json_data, dict):
                    refined_text = json_data.get("refined_text", request.text)
                    suggestions = json_data.get("suggestions", [])
                    
                    # STRICT: If refined text is significantly longer than original, reject it
                    original_length = len(request.text)
                    refined_length = len(refined_text)
                    if refined_length > original_length * 1.3:  # Allow max 30% expansion
                        refined_text = request.text  # Use original if too much expansion
                        suggestions = ["AI response was too verbose - kept original text"]
                    
                    # Ensure suggestions is a list and limit to 3
                    if not isinstance(suggestions, list):
                        suggestions = [str(suggestions)] if suggestions else []
                    suggestions = suggestions[:3]  # Reduced from 5 to 3
                    
                    # Analyze improvements made
                    improvements = analyze_improvements(request.text, refined_text)
                    
                    return TextRefinementResponse(
                        original_text=request.text,
                        refined_text=refined_text,
                        suggestions=suggestions,
                        word_count_original=len(request.text.split()),
                        word_count_refined=len(refined_text.split()),
                        improvements_made=improvements
                    )
                
                # If JSON parsing failed, try to extract at least the refined text
                # Look for patterns like "Refined text:" or similar
                refined_match = re.search(r'(?:refined|improved|corrected).*?text[:\-\s]*([^{}\[\]]+?)(?:\n|$)', cleaned_response, re.IGNORECASE | re.DOTALL)
                if refined_match:
                    refined_text = refined_match.group(1).strip()
                    # Clean up any quotes or extra formatting
                    refined_text = re.sub(r'^["\'`]+|["\'`]+$', '', refined_text).strip()
                else:
                    # Last resort - use the original text
                    refined_text = request.text
                
                return TextRefinementResponse(
                    original_text=request.text,
                    refined_text=refined_text,
                    suggestions=["AI response format was not recognized. Please try again."],
                    word_count_original=len(request.text.split()),
                    word_count_refined=len(refined_text.split()),
                    improvements_made=["Text processing attempted"]
                )
                
            except Exception as parse_error:
                # Ultimate fallback
                return TextRefinementResponse(
                    original_text=request.text,
                    refined_text=request.text,
                    suggestions=[f"Error processing AI response: {str(parse_error)}"],
                    word_count_original=len(request.text.split()),
                    word_count_refined=len(request.text.split()),
                    improvements_made=["Error occurred during processing"]
                )
                
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error communicating with Ollama API: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error refining text: {str(e)}"
        )

@router.get("/health")
async def check_ai_service():
    """
    Check if Ollama service is available and ready for text refinement
    """
    try:
        # Simple health check with minimal resource usage
        async with httpx.AsyncClient(timeout=httpx.Timeout(10.0)) as client:
            response = await client.post(
                settings.OLLAMA_API_URL,
                json={
                    "model": "gemma3:4b",
                    "prompt": "Test",
                    "stream": False,
                    "options": {
                        "num_predict": 3,
                        "num_thread": 2,
                        "num_gpu": 0
                    }
                }
            )
            
            if response.status_code == 200:
                return {
                    "status": "healthy", 
                    "model": "gemma3:4b",
                    "endpoint": settings.OLLAMA_API_URL,
                    "cpu_optimized": True,
                    "purpose": "markdown_formatting"
                }
            else:
                return {
                    "status": "unhealthy", 
                    "error": f"HTTP {response.status_code}",
                    "endpoint": settings.OLLAMA_API_URL
                }
                
    except Exception as e:
        return {
            "status": "unhealthy", 
            "error": str(e),
            "endpoint": settings.OLLAMA_API_URL
        }

@router.post("/feedback")
async def submit_feedback(
    feedback_data: dict,
    current_user: User = Depends(get_current_user)
):
    """
    Submit feedback about text refinement results to improve the knowledge base
    """
    try:
        # Validate required fields
        if not feedback_data.get("feedback_type"):
            raise HTTPException(status_code=400, detail="Feedback type is required")
        
        # Prepare feedback entry for knowledge base
        feedback_entry = {
            "timestamp": feedback_data.get("timestamp", datetime.now().isoformat()),
            "user_id": current_user.id,
            "user_role": current_user.role,
            "feedback_type": feedback_data.get("feedback_type"),
            "feedback_text": feedback_data.get("feedback_text", ""),
            "context": feedback_data.get("context", {}),
            "user_context": feedback_data.get("user_context", {})
        }
        
        # Try to store feedback in knowledge base if available
        try:
            from app.services.knowledge_base import get_knowledge_base_service
            kb_service = get_knowledge_base_service()
            
            # Store feedback for future training/improvement
            await kb_service.store_feedback(feedback_entry)
            
        except Exception as kb_error:
            # Continue even if knowledge base storage fails
            print(f"Warning: Could not store feedback in knowledge base: {kb_error}")
        
        # Always log feedback to a file for manual review
        import os
        import json
        
        # Ensure feedback directory exists
        feedback_dir = "/app/data/feedback"
        os.makedirs(feedback_dir, exist_ok=True)
        
        # Write feedback to timestamped file
        feedback_filename = f"feedback_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{current_user.id}.json"
        feedback_path = os.path.join(feedback_dir, feedback_filename)
        
        with open(feedback_path, 'w') as f:
            json.dump(feedback_entry, f, indent=2)
        
        return {
            "success": True,
            "message": "Feedback submitted successfully",
            "feedback_id": feedback_filename
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error submitting feedback: {str(e)}"
        )