#!/bin/sh
export TEST_PROFILE=docker
pytest tests/test_api/test_auth.py::TestAuthEndpoints::test_get_current_user -vv --tb=short > /app/test_failure.log 2>&1
