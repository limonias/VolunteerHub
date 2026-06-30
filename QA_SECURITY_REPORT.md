# QA and Security Test Report

## Scope
This review covered the Django backend, the Node.js verification-service code, and the static frontend pages under [frontend_src](frontend_src).

## Test Methods
- Static code review of the backend and frontend request flow.
- Syntax verification:
  - Ran `python -m compileall .` in the backend folder successfully.
  - Ran `python manage.py check` successfully with no Django issues reported.
  - Ran `python manage.py test`; no tests are present, so the suite reported `0 tests`.
- Reviewed the main security-sensitive handlers in [backend/api/views.py](backend/api/views.py), [backend/volunteerhub/settings.py](backend/volunteerhub/settings.py), and the registration/verification frontend pages in [frontend_src/register-employee.html](frontend_src/register-employee.html), [frontend_src/register-charity.html](frontend_src/register-charity.html), [frontend_src/verify.html](frontend_src/verify.html), and [frontend_src/profile.html](frontend_src/profile.html).

## Overall Assessment
The project is functional at a basic level, but it is not production-ready from a security standpoint. The most serious issues are missing authentication/authorization controls and client-side trust of sensitive data.

## Findings Summary

| Severity | Finding | Evidence |
| --- | --- | --- |
| Critical | No real authentication or authorization is implemented. Any caller can read or update another user’s profile by supplying another `userId`. | [backend/api/views.py](backend/api/views.py) |
| High | Verification codes are exposed to the client and stored in browser storage, increasing the chance of account takeover and replay. | [backend/api/views.py](backend/api/views.py), [frontend_src/verify.html](frontend_src/verify.html) |
| High | The frontend inserts API-provided values into `innerHTML`, creating a potential XSS vector. | [frontend_src/dashboard.html](frontend_src/dashboard.html) |
| High | The backend allows all origins and disables CSRF protections on sensitive endpoints. | [backend/volunteerhub/settings.py](backend/volunteerhub/settings.py), [backend/api/views.py](backend/api/views.py) |
| Medium | The Django settings use a hard-coded secret key and `DEBUG=True` with `ALLOWED_HOSTS=['*']`. | [backend/volunteerhub/settings.py](backend/volunteerhub/settings.py) |
| Medium | No rate limiting or abuse protections are present for registration, verification, and resend flows. | [backend/api/views.py](backend/api/views.py) |
| Medium | The project has no automated test coverage for the API or UI workflows. | Backend test run reported `0 tests` |

## Detailed Findings

### 1) Critical: Missing authentication and authorization
The API currently trusts the `userId` sent by the client in several places:
- Profile lookup uses `GET /api/profile/<user_id>` and returns data for whatever ID is requested.
- Profile update accepts `userId` from the form data and updates that account without checking who is logged in.
- Verification and resend endpoints depend on `userId` and do not verify ownership.

Impact:
- A user can view or alter another user’s profile and verification state.
- This is a direct authorization bypass.

Recommended fix:
- Introduce server-side authentication (session or JWT).
- Replace client-supplied `userId` with the authenticated identity from the request.
- Enforce role-based access for volunteer, charity, and admin flows.

### 2) High: Verification codes are exposed to the client
The backend returns `devCode` in registration and resend responses, and the frontend stores it in local storage and displays it in the verification page.

Impact:
- Anyone with access to the browser or a browser script can obtain the code.
- The code may be replayed or leaked through logs, extensions, or XSS.

Recommended fix:
- Stop returning verification codes to the frontend in production.
- Send a generic success message instead.
- Use email delivery or a secure token flow rather than exposing codes in the UI.

### 3) High: Cross-site scripting risk in dashboard rendering
The dashboard page builds HTML from user-controlled data:
- Interests are rendered with `innerHTML` in [frontend_src/dashboard.html](frontend_src/dashboard.html).

Impact:
- If an interest contains HTML or JavaScript, it can execute in the browser.
- This is a realistic XSS issue when profile data is user entered.

Recommended fix:
- Use `textContent` or DOM creation instead of building HTML from untrusted values.
- Sanitize any data that may be displayed in the UI.

### 4) High: Broad CORS and disabled CSRF protection
The backend enables `CORS_ALLOW_ALL_ORIGINS = True` and uses `@csrf_exempt` on the API endpoints.

Impact:
- The API is easier to abuse from untrusted origins.
- It weakens the default browser protections against cross-site request attacks.

Recommended fix:
- Restrict CORS to trusted origins.
- Re-enable CSRF protection for browser-based forms or move to a secure authenticated API pattern.

### 5) Medium: Hard-coded secret and debug mode
The Django settings contain:
- A hard-coded `SECRET_KEY`
- `DEBUG = True`
- `ALLOWED_HOSTS = ['*']`

Impact:
- This is not suitable for production and increases the chance of credential exposure and environment misconfiguration.

Recommended fix:
- Load secrets from environment variables.
- Set `DEBUG=False` in production.
- Restrict hosts to known domains.

### 6) Medium: No rate limiting or abuse controls
The registration, verification, and resend flows do not appear to have throttling or lockout mechanisms.

Impact:
- Attackers can automate account creation and code guessing attempts.

Recommended fix:
- Add request throttling and retry limits.
- Add lockout or temporary blocking after repeated failures.

### 7) Medium: Test coverage is absent
No backend tests were found, and the test run reported zero tests.

Impact:
- Regression bugs and security issues may go unnoticed.

Recommended fix:
- Add unit and integration tests for registration, verification, profile update, and authorization behavior.

## Recommended Priority Order
1. Implement authentication and authorization.
2. Remove client exposure of verification codes.
3. Fix XSS rendering in the dashboard.
4. Tighten CORS and CSRF handling.
5. Move secrets out of source control and disable debug mode for production.
6. Add automated tests and abuse controls.

## Conclusion
The application currently works as a prototype, but it should not be treated as secure or production-ready. The most urgent actions are to secure the API with real authentication and to stop exposing verification data to the client.
