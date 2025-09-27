# Commit Command

Creates standardized git commits in English following conventional commit format.

## Usage

`/commit [message]`

## Format

```text
feat(scope): Brief summary of what was done

Detailed list of changes:
* Item 1 description
* Item 2 description
* Item 3 description
```

## Commit Types

- **feat**: New feature
- **fix**: Bug fix
- **docs**: Documentation changes
- **style**: Code style changes (formatting, no logic changes)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks, dependencies

## Scope Examples

- **frontend**: Frontend-related changes
- **backend**: Backend-related changes
- **api**: API endpoint changes
- **ui**: User interface components
- **auth**: Authentication/authorization
- **db**: Database changes
- **config**: Configuration changes
- **deps**: Dependencies updates

## Examples

```text
feat(frontend): Add user profile component

Implemented new user profile functionality:
* Created ProfileCard component with avatar display
* Added edit profile modal with form validation
* Integrated with user API endpoints
* Added responsive design for mobile devices
```

```text
fix(api): Resolve CORS configuration for frontend requests

Fixed cross-origin request issues:
* Added django-cors-headers dependency
* Configured CORS middleware in Django settings
* Set allowed origins for localhost:3000
* Enabled credentials for authenticated requests
```

```text
refactor(backend): Improve user authentication flow

Enhanced authentication system:
* Moved token validation to middleware
* Added comprehensive error handling
* Implemented user session management
* Updated API documentation
```