"""
Text Refinement Testing Suite
Test cases to validate conservative LLM behavior
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import asyncio
from app.api.endpoints.auth import User, get_current_user
from app.api.endpoints.text import refine_text
from pydantic import BaseModel

router = APIRouter()

class TestCase(BaseModel):
    name: str
    input_text: str
    context: str
    expected_behavior: str
    max_length_ratio: float = 1.3  # Maximum allowed expansion

class TestResult(BaseModel):
    test_name: str
    input_text: str
    output_text: str
    passed: bool
    issues: List[str]
    length_ratio: float
    context: str

# Test cases covering different scenarios
TEST_CASES = [
    TestCase(
        name="Basic Grammar Fixes",
        input_text="lets test this refinement feature. i have been working on data analysis for my research project this week.",
        context="research_progress",
        expected_behavior="Should fix capitalization and grammar only, no expansion"
    ),
    
    TestCase(
        name="Run-on Sentence",
        input_text="found some interesting patterns in the dataset but having trouble with statistical significance testing need to figure out visualization techniques also my advisor wants me to present next week",
        context="research_progress", 
        expected_behavior="Should add punctuation and maybe break into sentences, no bullet points unless clearly needed"
    ),
    
    TestCase(
        name="Challenge Description",
        input_text="having issues with my code its not working properly getting error messages when i try to run the analysis cant figure out whats wrong",
        context="challenges",
        expected_behavior="Should fix grammar and punctuation, maybe separate issues, no dramatic formatting"
    ),
    
    TestCase(
        name="Simple Announcement",
        input_text="meeting moved to friday at 2pm please bring your progress reports",
        context="announcements",
        expected_behavior="Should fix basic grammar, NO emojis or fancy headers like 'Important Announcement!'"
    ),
    
    TestCase(
        name="Goals List",
        input_text="next week i want to finish data collection complete first draft of paper submit to conference review literature on topic",
        context="goals",
        expected_behavior="Could add basic structure but should NOT expand or add emojis"
    ),
    
    TestCase(
        name="Already Good Text",
        input_text="I completed the literature review and identified three key research gaps. The methodology is well-defined and ready for implementation.",
        context="research_progress",
        expected_behavior="Should leave mostly unchanged since it's already well-written"
    ),
    
    TestCase(
        name="Informal Style",
        input_text="hey everyone just wanted to update on my progress been working hard this week got some good results",
        context="general",
        expected_behavior="Should maintain informal tone while fixing grammar, not make it overly formal"
    ),
    
    TestCase(
        name="Technical Content",
        input_text="used random forest algorithm achieved 85% accuracy on test set but overfitting issues need hyperparameter tuning",
        context="research_progress",
        expected_behavior="Should fix grammar but preserve technical terms and meaning exactly"
    ),
    
    TestCase(
        name="Short Text",
        input_text="need help with statistics",
        context="challenges",
        expected_behavior="Very short text should stay short, maybe just grammar fixes"
    ),
    
    TestCase(
        name="Multiple Issues",
        input_text="ive been struggling with my research lately cant seem to make progress on the data analysis part also my advisor is asking for updates but i dont have much to show yet feeling frustrated",
        context="challenges",
        expected_behavior="Should organize and fix grammar but NOT add motivational content or dramatic emphasis"
    )
]

async def run_single_test(test_case: TestCase, current_user: User) -> TestResult:
    """Run a single test case and evaluate results"""
    try:
        # Create a mock request object
        from app.api.endpoints.text import TextRefinementRequest
        request = TextRefinementRequest(
            text=test_case.input_text,
            context=test_case.context
        )
        
        # Call the refinement function
        result = await refine_text(request, current_user)
        
        # Analyze the result
        issues = []
        input_length = len(test_case.input_text)
        output_length = len(result.refined_text)
        length_ratio = output_length / input_length if input_length > 0 else 1.0
        
        # Check for common issues
        if length_ratio > test_case.max_length_ratio:
            issues.append(f"Text expanded too much: {length_ratio:.2f}x original length")
        
        if "📢" in result.refined_text or "⚠️" in result.refined_text or "🎯" in result.refined_text:
            issues.append("Contains emojis (should be minimal or none)")
        
        if "**Important" in result.refined_text or "**Action Required" in result.refined_text:
            issues.append("Contains dramatic formatting headers")
        
        if result.refined_text.count("**") > test_case.input_text.count("**") + 4:
            issues.append("Added too much bold formatting")
        
        # Check if very short text was expanded unnecessarily
        if input_length < 50 and length_ratio > 1.5:
            issues.append("Short text was expanded unnecessarily")
        
        passed = len(issues) == 0
        
        return TestResult(
            test_name=test_case.name,
            input_text=test_case.input_text,
            output_text=result.refined_text,
            passed=passed,
            issues=issues,
            length_ratio=length_ratio,
            context=test_case.context
        )
        
    except Exception as e:
        return TestResult(
            test_name=test_case.name,
            input_text=test_case.input_text,
            output_text="ERROR",
            passed=False,
            issues=[f"Exception occurred: {str(e)}"],
            length_ratio=0.0,
            context=test_case.context
        )

@router.post("/run-tests")
async def run_all_tests(current_user: User = Depends(get_current_user)):
    """
    Run all text refinement test cases
    Only available to admin users
    """
    if current_user.role not in ["admin", "faculty"]:
        raise HTTPException(status_code=403, detail="Only admin/faculty can run tests")
    
    results = []
    
    for test_case in TEST_CASES:
        result = await run_single_test(test_case, current_user)
        results.append(result)
        
        # Small delay to avoid overwhelming the LLM
        await asyncio.sleep(0.5)
    
    # Calculate summary statistics
    total_tests = len(results)
    passed_tests = sum(1 for r in results if r.passed)
    failed_tests = total_tests - passed_tests
    avg_length_ratio = sum(r.length_ratio for r in results) / total_tests if total_tests > 0 else 0
    
    return {
        "summary": {
            "total_tests": total_tests,
            "passed": passed_tests,
            "failed": failed_tests,
            "pass_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
            "average_length_ratio": f"{avg_length_ratio:.2f}x"
        },
        "results": results,
        "recommendations": [
            "Tests should mostly pass with minimal expansion",
            "Length ratio should be close to 1.0 (same length)",
            "No emojis or dramatic formatting should appear",
            "Grammar and basic structure fixes are acceptable"
        ]
    }

@router.get("/test-cases")
async def get_test_cases(current_user: User = Depends(get_current_user)):
    """Get all test cases for review"""
    if current_user.role not in ["admin", "faculty"]:
        raise HTTPException(status_code=403, detail="Only admin/faculty can view test cases")
    
    return {
        "test_cases": TEST_CASES,
        "count": len(TEST_CASES)
    }