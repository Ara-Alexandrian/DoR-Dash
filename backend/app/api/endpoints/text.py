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

# Conservative formatting prompt templates - focus on markdown formatting and organization
ACADEMIC_PROMPTS = {
    "research_progress": """Format this research progress text with proper markdown formatting and organization. Add appropriate bullet points, emojis for visual appeal, and improve readability WITHOUT changing the core meaning or content.

Guidelines:
- Use bullet points (•) to organize key points
- Add relevant emojis sparingly (🔬 for experiments, 📊 for data, etc.)
- Use **bold** for important terms
- Keep original meaning unchanged
- Improve structure and readability only

TEXT: {text}

Respond with JSON:
{{"refined_text": "formatted version with markdown", "suggestions": ["formatting tip1", "organization tip2", "readability tip3"]}}""",

    "challenges": """Format this challenges text with proper markdown formatting. Organize into bullet points, add emojis for visual appeal, but preserve the original meaning and tone.

Guidelines:
- Use bullet points (•) for each challenge
- Add relevant emojis (⚠️ for issues, 🤔 for questions, etc.)
- Use **bold** for key challenges
- Keep original content and meaning
- Only improve organization and readability

TEXT: {text}

Respond with JSON:
{{"refined_text": "formatted version with markdown", "suggestions": ["formatting tip1", "organization tip2", "readability tip3"]}}""",

    "goals": """Format these goals/next steps with markdown formatting. Create organized bullet points and add visual appeal with emojis while preserving original content.

Guidelines:
- Use bullet points (•) or numbered lists for steps
- Add relevant emojis (🎯 for goals, 📅 for timelines, etc.)
- Use **bold** for important objectives
- Keep original meaning and content
- Only improve structure and visual appeal

TEXT: {text}

Respond with JSON:
{{"refined_text": "formatted version with markdown", "suggestions": ["formatting tip1", "organization tip2", "visual tip3"]}}""",

    "announcements": """Format this announcement with proper markdown structure. Add emojis for visual appeal and organize content with bullet points while keeping the original message intact.

Guidelines:
- Use bullet points (•) for key items
- Add relevant emojis (📢 for announcements, ⚠️ for important, etc.)
- Use **bold** for critical information
- Keep original tone and content
- Only improve formatting and readability

TEXT: {text}

Respond with JSON:
{{"refined_text": "formatted version with markdown", "suggestions": ["formatting tip1", "organization tip2", "visual tip3"]}}""",

    "general": """Format this text with markdown formatting for better readability. Add bullet points, emojis, and structure while preserving the original content and meaning.

Guidelines:
- Use bullet points (•) to organize thoughts
- Add appropriate emojis for visual appeal
- Use **bold** for emphasis
- Keep original content and meaning unchanged
- Only improve formatting and structure

TEXT: {text}

Respond with JSON:
{{"refined_text": "formatted version with markdown", "suggestions": ["formatting tip1", "organization tip2", "readability tip3"]}}"""
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
        
        # Call Ollama API with Gemma 4B for more conservative formatting
        async with httpx.AsyncClient(timeout=httpx.Timeout(60.0)) as client:
            response = await client.post(
                settings.OLLAMA_API_URL,
                json={
                    "model": "gemma2:2b",  # Use Gemma 2B for faster, more conservative responses
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "temperature": 0.1,      # Very low temperature for consistent formatting only
                        "top_p": 0.8,
                        "top_k": 20,
                        "num_ctx": 1024,         # Smaller context for efficiency
                        "num_predict": 400,      # Shorter responses for formatting
                        "repeat_penalty": 1.05,  # Lower repeat penalty
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
                    "model": "gemma2:2b",
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
                    "model": "gemma2:2b",
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