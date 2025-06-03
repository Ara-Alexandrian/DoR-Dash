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
        prompt = f"""You are a copy editor focused on grammar, spelling, and communication flow. 

Please proofread the following text and fix only:
- Grammar and spelling errors
- Punctuation issues
- Sentence structure problems
- Communication flow improvements
- Suggest bullet points if the content would benefit from a list format

Keep the original meaning and tone. Do not make creative changes or assume meanings not present in the original text.

TEXT TO PROOFREAD:
{request.text}

Respond ONLY with valid JSON in this exact format:
{{
    "refined_text": "Your corrected version of the text",
    "suggestions": ["Grammar/spelling tip 1", "Flow improvement tip 2", "Formatting suggestion 3"]
}}

Do not include any other text outside the JSON."""
        
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
                    
                    # Ensure suggestions is a list
                    if not isinstance(suggestions, list):
                        suggestions = [str(suggestions)] if suggestions else []
                    
                    return TextRefinementResponse(
                        original_text=request.text,
                        refined_text=refined_text,
                        suggestions=suggestions
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
                    suggestions=["AI response format was not recognized. Please try again."]
                )
                
            except Exception as parse_error:
                # Ultimate fallback
                return TextRefinementResponse(
                    original_text=request.text,
                    refined_text=request.text,
                    suggestions=[f"Error processing AI response: {str(parse_error)}"]
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