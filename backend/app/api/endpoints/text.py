from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
import httpx
from app.core.config import settings

router = APIRouter()

class TextRefinementRequest(BaseModel):
    text: str

class TextRefinementResponse(BaseModel):
    original_text: str
    refined_text: str
    suggestions: list[str]

@router.post("/refine-text", response_model=TextRefinementResponse)
async def refine_text(request: TextRefinementRequest):
    """
    Refines text using Ollama API (Mistral AI)
    """
    try:
        # Prepare prompt for Mistral model
        prompt = f"""Proofread the following text for grammar and spelling errors. 
        Improve its clarity and conciseness. 
        Offer suggestions for better phrasing.
        
        TEXT TO PROOFREAD:
        {request.text}
        
        Please respond in the following JSON format:
        {{
            "refined_text": "The revised, improved text with corrections",
            "suggestions": ["Suggestion 1", "Suggestion 2", "Suggestion 3"]
        }}
        """
        
        # Call Ollama API
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.OLLAMA_API_URL,
                json={
                    "model": "mistral",
                    "prompt": prompt,
                    "stream": False,
                    "options": {
                        "num_ctx": 4096,
                        "cpu_only": True  # Ensure CPU-only operation
                    }
                },
                timeout=60.0  # Increased timeout for CPU-based inference
            )
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=500,
                    detail=f"Error calling Ollama API: {response.text}"
                )
            
            # Extract the result
            result = response.json()
            completion = result.get("response", "")
            
            # Simple extraction - in a production app, we'd use proper JSON parsing with error handling
            # This is a simplified example
            try:
                import json
                import re
                
                # Try to extract JSON from the completion
                json_match = re.search(r'({.*})', completion, re.DOTALL)
                if json_match:
                    json_str = json_match.group(1)
                    data = json.loads(json_str)
                    
                    return TextRefinementResponse(
                        original_text=request.text,
                        refined_text=data.get("refined_text", "Error parsing refined text"),
                        suggestions=data.get("suggestions", ["Error parsing suggestions"])
                    )
                else:
                    # Fallback if we can't parse proper JSON
                    return TextRefinementResponse(
                        original_text=request.text,
                        refined_text=completion,
                        suggestions=["Could not parse suggestions from AI response"]
                    )
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                return TextRefinementResponse(
                    original_text=request.text,
                    refined_text=completion,
                    suggestions=["Could not parse suggestions from AI response"]
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