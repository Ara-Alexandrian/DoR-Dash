# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

[... Previous content remains the same ...]

## Recent Updates

- Testing confirmed that file upload works great for other file types
- Issue identified: When accessing the edit button for a particular submission, it redirects to the old edit item page instead of the new inline solution
- Verification link: https://dd.kronisto.net/updates
- **NEW**: LLM text refinement testing suite implemented with automated QA reports
- **NEW**: QA folder structure reorganized for better organization
- **NEW**: UI refinement process implemented to address redirect and inline editing challenges
- **NEW**: Dashboard redesigned with Mermaid-powered development roadmap
- **NEW**: Platform updates/changelog section added to dashboard

## Quality Assurance (QA) Structure

The project now has a comprehensive QA system:

### QA Directory Structure
```
qa/
├── LLM-QA/               # LLM text refinement QA reports
├── Validation/           # General system validation reports  
├── database/             # Database testing scripts
├── integration/          # API integration tests
└── utils/                # Testing utilities
```

### LLM Testing Suite
- **Endpoint**: `/api/v1/text-testing/run-tests` (admin only)
- **Purpose**: Validate conservative LLM behavior
- **Output**: Automatic report generation in `qa/LLM-QA/`
- **Model**: Gemma 3 4B on Ollama server (172.30.98.14:11434)

### Test Cases Cover:
- Basic grammar fixes
- Announcement formatting (no emojis/dramatic headers)
- Challenge descriptions
- Technical content preservation
- Length expansion limits (max 30%)

### When to Run LLM Tests:
- After changing LLM prompts
- After model updates
- Before production deployments
- When text refinement issues are reported

See `qa/README.md` for detailed usage instructions.

[... Rest of the previous content remains unchanged ...]