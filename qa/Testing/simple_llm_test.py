#!/usr/bin/env python3
"""
Simple standalone test for LLM prompts
Tests the conservative prompts directly with Ollama
"""

import json
import requests
import time

# Test cases
TEST_CASES = [
    {
        "name": "Basic Grammar Fixes",
        "input": "lets test this refinement feature. i have been working on data analysis for my research project this week.",
        "context": "research_progress"
    },
    {
        "name": "Simple Announcement", 
        "input": "meeting moved to friday at 2pm please bring your progress reports",
        "context": "announcements"
    },
    {
        "name": "Already Good Text",
        "input": "I completed the literature review and identified three key research gaps. The methodology is well-defined and ready for implementation.",
        "context": "research_progress"
    },
    {
        "name": "Challenge Description",
        "input": "having issues with my code its not working properly getting error messages when i try to run the analysis cant figure out whats wrong",
        "context": "challenges"
    },
    {
        "name": "Short Text",
        "input": "need help with statistics",
        "context": "challenges"
    }
]

# Conservative prompts (copied from our backend)
PROMPTS = {
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

    "challenges": """Clean up this challenges text with minimal formatting. Fix basic issues only, do NOT expand content.

Rules:
- Fix grammar/spelling errors only
- Add bullet points ONLY if there are clearly separate challenges
- Keep text shorter or same length as original
- Do NOT add emojis or fancy formatting
- Do NOT change wording or add explanations

TEXT: {text}

Respond with JSON:
{{"refined_text": "cleaned version", "suggestions": ["grammar fix", "structure tip", "clarity note"]}}"""
}

def test_ollama_api(text, context):
    """Test a single case with Ollama API"""
    prompt_template = PROMPTS.get(context, PROMPTS["research_progress"])
    prompt = prompt_template.format(text=text)
    
    try:
        response = requests.post(
            "http://172.30.98.14:11434/api/generate",
            json={
                "model": "gemma3:4b",
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.2,
                    "top_p": 0.7,
                    "top_k": 15,
                    "num_ctx": 512,
                    "num_predict": 200,
                    "repeat_penalty": 1.1,
                    "num_gpu": 0
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            return result.get("response", "No response")
        else:
            return f"API Error: {response.status_code}"
            
    except Exception as e:
        return f"Error: {e}"

def analyze_result(original, result):
    """Analyze if the result meets our conservative criteria"""
    issues = []
    
    # Check length expansion
    original_len = len(original)
    result_len = len(result)
    length_ratio = result_len / original_len if original_len > 0 else 1.0
    
    if length_ratio > 1.3:
        issues.append(f"Too much expansion: {length_ratio:.2f}x")
    
    # Check for unwanted formatting
    if "📢" in result or "⚠️" in result or "🎯" in result:
        issues.append("Contains emojis")
    
    if "**Important" in result or "**Action Required" in result:
        issues.append("Contains dramatic headers")
    
    # Check for excessive bold formatting
    if result.count("**") > original.count("**") + 4:
        issues.append("Too much bold formatting")
    
    return issues, length_ratio

def main():
    """Run all test cases"""
    print("🧪 Testing LLM Conservative Prompts")
    print("=" * 60)
    
    results = []
    
    for i, test_case in enumerate(TEST_CASES, 1):
        print(f"\n📝 Test {i}: {test_case['name']}")
        print(f"Input: '{test_case['input']}'")
        print(f"Context: {test_case['context']}")
        
        # Call Ollama API
        raw_response = test_ollama_api(test_case['input'], test_case['context'])
        
        # Try to extract JSON from response
        refined_text = test_case['input']  # fallback
        try:
            # Look for JSON in the response
            import re
            json_match = re.search(r'\{.*"refined_text".*\}', raw_response, re.DOTALL)
            if json_match:
                json_data = json.loads(json_match.group(0))
                refined_text = json_data.get("refined_text", test_case['input'])
            else:
                refined_text = raw_response
        except:
            refined_text = raw_response
        
        print(f"Output: '{refined_text}'")
        
        # Analyze result
        issues, length_ratio = analyze_result(test_case['input'], refined_text)
        
        status = "✅ PASS" if len(issues) == 0 else "❌ FAIL"
        print(f"Status: {status} (length: {length_ratio:.2f}x)")
        
        if issues:
            print(f"Issues: {', '.join(issues)}")
        
        results.append({
            "name": test_case['name'],
            "passed": len(issues) == 0,
            "length_ratio": length_ratio,
            "issues": issues
        })
        
        time.sleep(1)  # Be nice to the API
    
    # Summary
    print("\n" + "=" * 60)
    print("📊 SUMMARY")
    total = len(results)
    passed = sum(1 for r in results if r["passed"])
    failed = total - passed
    avg_ratio = sum(r["length_ratio"] for r in results) / total
    
    print(f"Total tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Pass rate: {(passed/total*100):.1f}%")
    print(f"Average length ratio: {avg_ratio:.2f}x")
    
    if passed == total:
        print("\n✅ All tests passed! LLM is behaving conservatively.")
    else:
        print(f"\n❌ {failed} tests failed. LLM may need more tuning.")

if __name__ == "__main__":
    main()