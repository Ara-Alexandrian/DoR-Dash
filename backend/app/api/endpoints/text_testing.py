"""
Text Refinement Testing Suite
Test cases to validate conservative LLM behavior
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
import asyncio
import os
import json
from datetime import datetime
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

def generate_qa_report(results: List[TestResult], summary: Dict[str, Any]) -> str:
    """Generate a detailed QA report in markdown format"""
    timestamp = datetime.now()
    
    report = f"""# LLM Text Refinement QA Report

**Generated**: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}  
**Model**: Gemma 3 4B  
**Test Suite Version**: 1.0  

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {summary['total_tests']} |
| Passed | {summary['passed']} |
| Failed | {summary['failed']} |
| Pass Rate | {summary['pass_rate']} |
| Average Length Ratio | {summary['average_length_ratio']} |

## Test Results

"""
    
    for i, result in enumerate(results, 1):
        status_emoji = "✅" if result.passed else "❌"
        report += f"""### {i}. {result.test_name} {status_emoji}

**Context**: `{result.context}`  
**Length Ratio**: {result.length_ratio:.2f}x  

**Input**:
```
{result.input_text}
```

**Output**:
```
{result.output_text}
```

"""
        if result.issues:
            report += f"**Issues**:\n"
            for issue in result.issues:
                report += f"- {issue}\n"
        
        report += "\n---\n\n"
    
    report += f"""## Assessment

### Conservative Behavior Validation

The LLM text refinement system should demonstrate:

1. **Minimal Expansion** (≤ 1.3x original length)
2. **No Unwanted Formatting** (no emojis, dramatic headers)
3. **Grammar Focus** (fix obvious errors only)
4. **Content Preservation** (maintain original meaning)

### Recommendations

Based on this test run:

"""
    
    if summary['passed'] == summary['total_tests']:
        report += "- ✅ **All tests passed** - LLM is behaving conservatively as expected\n"
        report += "- ✅ No further tuning required\n"
    else:
        report += f"- ⚠️ **{summary['failed']} tests failed** - Review failed cases above\n"
        report += "- 🔧 Consider adjusting prompts or model parameters\n"
    
    avg_ratio = float(summary['average_length_ratio'].replace('x', ''))
    if avg_ratio > 1.2:
        report += f"- ⚠️ **Average expansion** ({avg_ratio:.2f}x) is high - consider stricter length limits\n"
    else:
        report += f"- ✅ **Length control** ({avg_ratio:.2f}x) is within acceptable range\n"
    
    report += f"""
---

*Report generated by DoR-Dash LLM Testing Suite*  
*For issues or questions, contact the development team*
"""
    
    return report

def save_qa_report(content: str) -> str:
    """Save the QA report to the qa/LLM-QA folder"""
    try:
        # Create QA directory structure
        qa_dir = "/config/workspace/gitea/DoR-Dash/qa/LLM-QA"
        os.makedirs(qa_dir, exist_ok=True)
        
        # Generate filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"llm_qa_report_{timestamp}.md"
        filepath = os.path.join(qa_dir, filename)
        
        # Save report
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filepath
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save QA report: {str(e)}")

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
    
    summary = {
        "total_tests": total_tests,
        "passed": passed_tests,
        "failed": failed_tests,
        "pass_rate": f"{(passed_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%",
        "average_length_ratio": f"{avg_length_ratio:.2f}x"
    }
    
    # Generate and save QA report
    try:
        report_content = generate_qa_report(results, summary)
        report_path = save_qa_report(report_content)
        report_saved = True
        report_location = report_path
    except Exception as e:
        report_saved = False
        report_location = f"Failed to save report: {str(e)}"
    
    return {
        "summary": summary,
        "results": results,
        "recommendations": [
            "Tests should mostly pass with minimal expansion",
            "Length ratio should be close to 1.0 (same length)",
            "No emojis or dramatic formatting should appear",
            "Grammar and basic structure fixes are acceptable"
        ],
        "qa_report": {
            "generated": report_saved,
            "location": report_location,
            "timestamp": datetime.now().isoformat()
        }
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