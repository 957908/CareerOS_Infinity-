# CareerOS Infinity - Security Architecture & Threat Model

## 1. Zero Trust Principles & Strategy

**CareerOS Infinity** enforces a Zero Trust architecture. No request is implicitly trusted, regardless of whether it originates within the local cluster network or from an external interface.
*   **Verification:** Every API request must pass through an authentication middleware to validate the JWT.
*   **Least Privilege:** Users only have access to resources associated with their own `user_id` record.
*   **Explicit Approvals:** Actions that synchronize external accounts or execute remote writes (e.g. calendar syncs) must present a visible authorization confirmation dialog to the user before executing.

---

## 2. Authentication & Authorization Structure

### 2.1 Passwordless Passkeys (WebAuthn) & OAuth2
The system utilizes two primary entry points:
1.  **OAuth2 Integration:** Google/Microsoft login returns authorization tokens which compile into a standard backend-managed JWT.
2.  **WebAuthn Passkeys:** Allows passwordless biometrics and hardware keys verification, eliminating password leaks.

### 2.2 JWT Management & Token Revocation
*   **Access Token:** Signed via HS256 algorithm with a lifetime of 1 hour.
*   **Refresh Token:** Lifetime of 30 days, stored in an HttpOnly, secure, SameSite=Strict cookie.
*   **Revocation:** On user logout, the token signature is published to a Redis blacklist database key matching the remaining TTL. The authentication middleware verifies the incoming token against the Redis blacklist before passing control to the endpoint handler.

### 2.3 Role-Based Access Control (RBAC)

```
+--------------------+      Inherits     +--------------------+
|     User Role      | ----------------> |     Admin Role     |
+--------------------+                   +--------------------+
```

*   **Role: User**
    *   Permissions: `user:profile:read`, `user:profile:write`, `document:read`, `document:write`, `document:delete`, `interview:conduct`.
*   **Role: Administrator**
    *   Permissions: (All User permissions) + `system:metrics:read`, `system:rate-limit:write`, `user:profile:delete`.

---

## 3. Cryptographic and Encryption Standards

```
+-----------------------+------------------------------------------+
| Data State            | Encryption Standard                      |
+-----------------------+------------------------------------------+
| Data in Transit       | TLS 1.3 enforced, HSTS enabled           |
| Files at Rest (Vault) | AES-256 (AES-GCM mode)                   |
| Secrets in Database   | Fernet Symmetric Keys (rotated monthly)  |
| Database Passwords    | Argon2id (work factor 3, memory 64MB)    |
+-----------------------+------------------------------------------+
```

### 3.1 Encryption at Rest (Career Document Vault)
All document files are stored in a dedicated local or cloud storage directory. Prior to saving, the backend generates an initialization vector (IV) and encrypts the file stream using AES-GCM. The decryption key is fetched securely from environment configuration keys.

---

## 4. Threat Matrix & OWASP Top 10 Mitigations

### 4.1 Broken Object Level Authorization (BOLA)
*   **Threat:** A user modifies the query request ID to access another user's parsed resume metadata (e.g. `/api/v1/resumes/other_user_id`).
*   **Mitigation:** The database query interface joins every select command with the active `user_id` payload parsed from the JWT authentication header.

### 4.2 API Rate Limiting (DoS/Brute Force)
*   **Threat:** Botnets flooding the login or resume upload APIs.
*   **Mitigation:** A FastAPI middleware monitors incoming request IPs using a **Redis Token Bucket algorithm**. The configuration limits login attempts to 5 per minute and general API requests to 100 per minute per IP.
