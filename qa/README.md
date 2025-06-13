# QA and Testing Scripts

This directory contains QA (Quality Assurance) scripts, integration tests, and utilities for testing the DoR-Dash application.

## Directory Structure

```
qa/
├── README.md                 # This file
├── database/                 # Database testing and verification scripts
│   ├── check_db_state.py     # Check current database state
│   └── init_test_data.py     # Initialize test data
├── integration/              # Integration tests
│   └── api_tests.py          # API endpoint integration tests
└── utils/                    # Testing utilities
    └── ssh_runner.py         # Utility to run tests on deployed container
```

## Usage

### Check Database State
```bash
python qa/database/check_db_state.py
```

### Run Integration Tests
```bash
python qa/integration/api_tests.py
```

## Notes

- Unit tests are located in `backend/tests/`
- QA scripts are designed to work with deployed containers
- Integration tests verify the full stack is working correctly