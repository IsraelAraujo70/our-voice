# Testing Guide - OUR Voice Backend

## Overview

This document outlines the testing infrastructure, guidelines, and procedures for the OUR Voice Django backend.

## Running Tests

### Prerequisites

- Docker environment is running
- Backend containers are up and running

### Basic Test Commands

```bash
# Run all tests with coverage
docker exec our-voice_backend_1 uv run pytest

# Run tests with detailed output
docker exec our-voice_backend_1 uv run pytest -v

# Run tests with coverage report
docker exec our-voice_backend_1 uv run pytest --cov=apps --cov-report=term-missing

# Run specific app tests
docker exec our-voice_backend_1 uv run pytest apps/accounts/tests/

# Run specific test file
docker exec our-voice_backend_1 uv run pytest apps/accounts/tests/test_models.py

# Run specific test method
docker exec our-voice_backend_1 uv run pytest apps/accounts/tests/test_models.py::TestUserModel::test_create_user_with_email_and_handle

# Generate HTML coverage report
docker exec our-voice_backend_1 uv run pytest --cov=apps --cov-report=html
```

### Test Markers

```bash
# Run only unit tests
docker exec our-voice_backend_1 uv run pytest -m unit

# Run only integration tests
docker exec our-voice_backend_1 uv run pytest -m integration

# Skip slow tests
docker exec our-voice_backend_1 uv run pytest -m "not slow"
```

## Test Structure

```
backend/
├── tests/                          # Global test utilities
│   ├── conftest.py                 # Global fixtures
│   ├── factories.py                # Factory Boy factories
│   └── utils.py                    # Test helper functions
├── apps/
│   ├── accounts/
│   │   └── tests/
│   │       ├── test_models.py      # Model tests
│   │       ├── test_views.py       # API endpoint tests
│   │       └── test_authentication.py  # Auth-specific tests
│   ├── posts/
│   │   └── tests/
│   │       ├── test_models.py      # Post model tests
│   │       ├── test_views.py       # Post API tests
│   │       └── test_archival.py    # Archival functionality
│   ├── moderation/
│   │   └── tests/
│   │       ├── test_models.py      # Vote & decision models
│   │       ├── test_views.py       # Moderation API tests
│   │       └── test_voting_threshold.py  # Threshold logic
│   └── interactions/
│       └── tests/
│           ├── test_models.py      # Interaction models
│           └── test_views.py       # Interaction API tests
```

## Coverage Requirements

- **Critical Paths**: Minimum 80% coverage
- **Models**: 90% coverage
- **ViewSets**: 85% coverage
- **Business Logic**: 95% coverage
- **Utilities**: 70% coverage

### Checking Coverage

```bash
# View coverage report in terminal
docker exec our-voice_backend_1 uv run pytest --cov=apps --cov-report=term-missing

# Generate HTML report (accessible at backend/htmlcov/index.html)
docker exec our-voice_backend_1 uv run pytest --cov=apps --cov-report=html
```

## Regression Test Checklist

Use this checklist before releases and after major changes:

### 🔐 Authentication Flow
- [ ] User registration with unique email and handle
- [ ] Login returns valid authentication token
- [ ] Protected endpoints require valid authentication
- [ ] Token authentication works for API calls
- [ ] Invalid tokens are properly rejected
- [ ] Soft-deleted users cannot authenticate
- [ ] Password changes work correctly
- [ ] User profile updates require authentication

### 📝 Post Management
- [ ] Create post with text content
- [ ] Create post with image attachment
- [ ] Edit own posts only (authorization check)
- [ ] Delete own posts (soft delete)
- [ ] View public feed in chronological order
- [ ] Filter posts by author handle
- [ ] Create reply posts with proper threading
- [ ] Create quoted posts with original reference
- [ ] Post visibility settings work correctly
- [ ] Pagination works on post listings

### 🗳️ Community Voting Mechanism
- [ ] Authenticated users can vote to remove posts
- [ ] Users cannot vote twice on the same post
- [ ] Vote weight is correctly calculated (default 1.0)
- [ ] Only REMOVE votes count toward archival threshold
- [ ] Only active votes count toward threshold
- [ ] 5-vote threshold triggers post archival
- [ ] Archived posts show correct status and timestamp
- [ ] Vote history is preserved after archival
- [ ] ModerationDecision is created with accurate data
- [ ] Weighted votes calculate threshold correctly
- [ ] Threshold is configurable via environment variable

### 📋 Post Archival
- [ ] Posts archive at exactly 5.0 vote weight
- [ ] Archived posts preserve original content
- [ ] Archived posts remain readable
- [ ] Archive method is idempotent
- [ ] Archival doesn't affect replies/quotes
- [ ] Multiple posts archive independently
- [ ] Archive timestamp is accurate

### 💝 User Interactions
- [ ] Like posts (unique constraint enforced)
- [ ] Unlike posts (remove like)
- [ ] Repost with optional quote text
- [ ] Remove reposts
- [ ] Bookmark posts for later
- [ ] Remove bookmarks
- [ ] Reply to posts with threading
- [ ] Edit own replies only
- [ ] Delete own replies
- [ ] Users can only see their own interactions
- [ ] Interaction counts are accurate

### 👑 Administrative Functions
- [ ] Superuser can promote users to staff
- [ ] Superuser can promote users to admin
- [ ] Superuser can remove privileges
- [ ] Users cannot remove their own privileges
- [ ] Staff users have limited permissions
- [ ] Superuser can hard delete users
- [ ] Regular users can soft delete own account
- [ ] Cannot delete last superuser account
- [ ] Admin actions are properly logged

### 🔍 API Endpoints
- [ ] All endpoints return proper HTTP status codes
- [ ] Error responses include meaningful messages
- [ ] Pagination works on all list endpoints
- [ ] Query parameters work for filtering
- [ ] POST endpoints validate required fields
- [ ] PUT/PATCH endpoints validate permissions
- [ ] DELETE endpoints handle cascading properly
- [ ] Related objects are included via select_related
- [ ] Anonymous access works for public endpoints
- [ ] Authentication required for protected endpoints

### 🛡️ Data Integrity
- [ ] Unique constraints are enforced
- [ ] Foreign key relationships work correctly
- [ ] Cascade deletions work as expected
- [ ] Soft deletes exclude from default querysets
- [ ] Timestamps are automatically managed
- [ ] Model validation prevents invalid data
- [ ] Database migrations apply cleanly
- [ ] Indexes improve query performance

### 🔄 Edge Cases
- [ ] Empty request bodies handled gracefully
- [ ] Invalid JSON returns proper error
- [ ] Very long text fields are truncated/validated
- [ ] Special characters in handles/emails work
- [ ] Concurrent votes on same post handled correctly
- [ ] High-precision decimal weights work
- [ ] Zero and negative vote weights handled
- [ ] Non-existent resource IDs return 404
- [ ] Permission denied returns 403

## Writing New Tests

### Test Naming Conventions

```python
# Good test names
def test_user_can_create_post():
def test_vote_weight_defaults_to_one():
def test_archived_posts_remain_readable():
def test_cannot_vote_twice_on_same_post():

# Avoid generic names
def test_post():
def test_vote():
def test_user():
```

### Test Organization

1. **Unit Tests**: Test individual model methods and properties
2. **Integration Tests**: Test API endpoints and business logic
3. **Edge Cases**: Test boundary conditions and error scenarios

### Using Factories

```python
from tests.factories import UserFactory, PostFactory, VoteFactory

# Create test data
user = UserFactory(handle="testuser")
post = PostFactory(author=user)
vote = VoteFactory(post=post, voter=user)

# Create multiple objects
users = UserFactory.create_batch(5)
```

### Using Test Utilities

```python
from tests.utils import (
    create_authenticated_client,
    assert_paginated_response,
    create_votes_for_archival,
    assert_archived
)

# Get authenticated client
client, user = create_authenticated_client()

# Test pagination
response = client.get("/api/posts/")
assert_paginated_response(response.data, expected_count=10)

# Test archival
post = PostFactory()
create_votes_for_archival(post, 5)
assert_archived(post)
```

### Database Transactions

```python
import pytest

@pytest.mark.django_db
def test_database_operation():
    # Test that uses database
    user = User.objects.create_user(...)

@pytest.mark.django_db(transaction=True)
def test_transaction_behavior():
    # Test that needs real database transactions
    pass
```

## Performance Testing

### Query Count Testing

```python
from django.test import override_settings
from django.db import connection

def test_query_count():
    with override_settings(DEBUG=True):
        initial_queries = len(connection.queries)

        # Perform operation
        response = client.get("/api/posts/")

        query_count = len(connection.queries) - initial_queries
        assert query_count <= 5  # Reasonable limit
```

### Using Test Utilities for Performance

```python
from tests.utils import QueryCountAssertMixin

class TestPostViews(QueryCountAssertMixin):
    def test_post_list_query_count(self):
        with self.assertMaxQueryCount(3):
            response = client.get("/api/posts/")
```

## Debugging Tests

### Running Tests with PDB

```bash
# Drop into debugger on failure
docker exec our-voice_backend_1 uv run pytest --pdb

# Drop into debugger on first failure
docker exec our-voice_backend_1 uv run pytest --pdb -x
```

### Verbose Output

```bash
# Show detailed test output
docker exec our-voice_backend_1 uv run pytest -v -s

# Show captured stdout
docker exec our-voice_backend_1 uv run pytest -s
```

### Failed Test Re-runs

```bash
# Re-run only failed tests
docker exec our-voice_backend_1 uv run pytest --lf

# Re-run failed tests first, then all others
docker exec our-voice_backend_1 uv run pytest --ff
```

## Continuous Integration

Tests are automatically run on:
- Pull request creation/updates
- Merges to main branch
- Scheduled daily runs

### CI Commands

The CI pipeline runs these commands:
```bash
docker exec our-voice_backend_1 uv run pytest --cov=apps --cov-fail-under=80
docker exec our-voice_backend_1 uv run ruff check .
docker exec our-voice_backend_1 uv run ruff format --check .
```

## Test Data Management

### Using Factories vs Fixtures

**Use Factories for:**
- Dynamic test data
- Tests that need many variations
- Complex object relationships

**Use Fixtures for:**
- Static test data
- Expensive setup operations
- Shared test resources

### Database Reset

Each test runs in a transaction that's rolled back, ensuring clean state.

### Test Isolation

- Each test method is isolated
- Database changes are automatically rolled back
- Use `@pytest.mark.django_db` for database tests
- Use separate factories for different test scenarios

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure all apps are in INSTALLED_APPS
2. **Database Errors**: Check that `@pytest.mark.django_db` is used
3. **Authentication Errors**: Use `client.force_authenticate(user=user)`
4. **Factory Errors**: Check for required fields and relationships
5. **Coverage Issues**: Exclude migrations and admin files in config

### Getting Help

- Check existing tests for patterns
- Use pytest's verbose output for debugging
- Review factory definitions for test data creation
- Check Django test documentation for advanced features

## Best Practices

1. **Test Behavior, Not Implementation**: Test what the code does, not how
2. **One Assertion Per Test**: Keep tests focused and specific
3. **Use Descriptive Names**: Test names should explain what they verify
4. **Test Edge Cases**: Include boundary conditions and error scenarios
5. **Keep Tests Fast**: Use factories and avoid complex setup
6. **Test User Stories**: Cover complete user workflows
7. **Mock External Services**: Don't rely on external APIs in tests
8. **Test Security**: Verify authentication and authorization
9. **Document Complex Tests**: Add comments for complex test logic
10. **Review Test Coverage**: Ensure critical paths are covered