from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import List, Optional
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

# Enhanced academic prompt templates
ACADEMIC_PROMPTS = {
    "research_progress": """You are an expert academic writing assistant specializing in research documentation. Refine this research progress text for clarity and professionalism.

Focus on: clear methodology, accurate terminology, logical flow, professional tone.

TEXT: {text}

Respond with JSON:
{{"refined_text": "refined version", "suggestions": ["tip1", "tip2", "tip3"]}}""",

    "challenges": """You are an expert academic writing assistant. Refine this text about research challenges to be professional and solution-oriented.

Focus on: clear problem identification, constructive framing, academic tone.

TEXT: {text}

Respond with JSON:
{{"refined_text": "refined version", "suggestions": ["tip1", "tip2", "tip3"]}}""",

    "goals": """You are an expert academic writing assistant. Refine these research goals/next steps to be specific and professionally presented.

Focus on: specific objectives, clear timelines, professional language, logical sequencing.

TEXT: {text}

Respond with JSON:
{{"refined_text": "refined version", "suggestions": ["tip1", "tip2", "tip3"]}}""",

    "announcements": """You are an expert academic communication assistant. Refine this faculty announcement for clarity and professionalism.

Focus on: clear communication, professional tone, important information highlighted.

TEXT: {text}

Respond with JSON:
{{"refined_text": "refined version", "suggestions": ["tip1", "tip2", "tip3"]}}""",

    "general": """You are an expert academic writing assistant. Refine this text for grammar, clarity, and professional academic style.

Focus on: grammar corrections, clear language, professional tone, logical flow.

TEXT: {text}

Respond with JSON:
{{"refined_text": "refined version", "suggestions": ["tip1", "tip2", "tip3"]}}"""
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
        
        # Call Ollama API with CPU optimizations
        async with httpx.AsyncClient(timeout=httpx.Timeout(90.0)) as client:
            response = await client.post(
                settings.OLLAMA_API_URL,
                json={
                    "model": "mistral:7b",  # Specify 7B variant for CPU efficiency
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.3,      # Lower temperature for consistent academic writing
                        "top_p": 0.9,
                        "top_k": 40,
                        "num_ctx": 2048,         # Optimized context window for CPU
                        "num_predict": 600,      # Reasonable token limit
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
                    
                    # Ensure suggestions is a list and limit to 5
                    if not isinstance(suggestions, list):
                        suggestions = [str(suggestions)] if suggestions else []
                    suggestions = suggestions[:5]
                    
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
                    "model": "mistral:7b",
                    "prompt": "Test",
                    "stream": False,
                    "options": {
                        "num_predict": 5,
                        "num_thread": 2,
                        "num_gpu": 0
                    }
                }
            )
            
            if response.status_code == 200:
                return {
                    "status": "healthy", 
                    "model": "mistral:7b",
                    "endpoint": settings.OLLAMA_API_URL,
                    "cpu_optimized": True
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