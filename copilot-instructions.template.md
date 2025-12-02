# MySingle Service Development Guidelines

**Version:** 2.2.1 | **For:** MySingle Quant Microservices

Core standards for services using mysingle package. Full docs: [mysingle-pack](https://github.com/Br0therDan/mysingle-pack)

---

## 1. Logging Standards

**MUST use structured logging:** Import `get_structured_logger(__name__)` from `mysingle.core.logging`. Never use `print()` or standard `logging` module.

**Log with context:** `logger.info("message", key=value, user_id=user.id)` - include relevant IDs for tracing.

**Request tracing:** Bind correlation_id via `logger.bind(correlation_id=id)` for distributed tracing.

---

## 2. Audit Logging

**Auto-enabled in production:** HTTP requests/responses logged to MongoDB automatically.

**Custom metadata:** Add to `request.state.audit_metadata = {"action": "...", "data": {...}}` for business events.

**Exclusions:** Health/metrics endpoints skipped by default.

---

## 3. Package Updates (CI/CD)

**Submodule sync:** `cd packages/mysingle && git pull origin main`, then commit to service repo.

**Version check:** Run `mysingle version auto` in mysingle directory.

---

## 4. Proto File Changes (gRPC)

### Server-Side (proto owner)
1. Edit proto in `packages/mysingle/protos/services/{service}/v1/*.proto`
2. Validate: `mysingle-proto validate`
3. Generate stubs: `mysingle-proto generate`
4. Submit PR: `mysingle submodule sync` (follow prompts)
5. After merge: Update service submodule reference

### Consumer-Side (need changes to other service's proto)
1. Create GitHub issue in mysingle-pack: `[Proto] Add RPC to {service}_service`
2. OR submit PR directly with proto changes
3. After approval: Update both owner and consumer services

---

## 5. Authentication Patterns

**Standard:** All services use Kong Gateway headers via `Request.state.user`.

**Get user:** `get_current_active_verified_user(request)` raises 401 if unauthenticated.

**User-scoped resources:** ALWAYS check `resource.user_id == user.id` before returning/modifying.

**Optional auth:** Use `get_current_user_optional(request)` - returns None if not authenticated.

**Service-to-Service:** Extend `BaseGrpcClient(service_name, port, user_id=user.id)` - auto-propagates metadata.

---

## 6. Service Types

**NON_IAM_SERVICE:** Standard for all services except IAM - receives Kong headers, no User DB.

**IAM_SERVICE:** Only for iam-service - validates JWT, manages User/OAuthAccount collections.

**Setup:** `create_service_config(service_name="...", service_type=ServiceType.NON_IAM_SERVICE)`

---

## 7. Database Guidelines

**MongoDB:** Extend `BaseTimeDocWithUserId` for user-owned resources. ALWAYS filter by `user_id` in queries: `Model.find(Model.user_id == user.id)`.

**Redis:** Use `get_redis_client(db=N)` - DB allocation: 0=IAM, 1=Market, 2=Indicators, 3=Strategies, 4=Backtests.

**Cache keys:** Format as `{resource}:{user_id}:{resource_id}` for user isolation.

---

## 8. Error Responses

**Use HTTPException:** `raise HTTPException(status_code, detail="message")` for API errors.

**Status codes:** 401=unauthenticated, 403=forbidden, 404=not found, 400=bad request, 500=server error.

**Never expose:** Internal exceptions or stack traces to clients.

---

## 9. Testing

**Auth bypass:** Set `MYSINGLE_AUTH_BYPASS=true` and `ENVIRONMENT=development` in tests only.

**Run tests:** `./run_tests.sh` or `pytest tests/ -v`

**Async tests:** Use `@pytest.mark.asyncio` decorator.

---

## 10. Critical Rules

**NEVER:**
- Use `print()` or standard logging
- Skip `user_id` ownership checks in endpoints
- Hard-code service URLs/ports (use env vars)
- Create User/OAuthAccount models in NON_IAM services
- Query all documents without user filtering
- Use generic Exception for HTTP errors

**ALWAYS:**
- Validate user ownership before data access
- Propagate `user_id` and `correlation_id` in service calls
- Use `BaseGrpcClient` for gRPC communication
- Follow REST conventions: `/api/v1/{resource}/{id}`
- Return appropriate HTTP status codes

---

## Quick Commands

| Task            | Command                                                   |
| --------------- | --------------------------------------------------------- |
| Get logger      | `from mysingle.core.logging import get_structured_logger` |
| Get user        | `user = get_current_active_verified_user(request)`        |
| Update mysingle | `cd packages/mysingle && git pull origin main`            |
| Proto validate  | `mysingle-proto validate`                                 |
| Proto generate  | `mysingle-proto generate`                                 |
| Redis client    | `await get_redis_client(db=N)`                            |
| User filter     | `Model.find(Model.user_id == user.id)`                    |

---

**Full Documentation:** https://github.com/Br0therDan/mysingle-pack
