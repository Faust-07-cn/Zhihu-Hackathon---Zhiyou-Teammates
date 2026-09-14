# Debug Session: Zhihu login state

Status: [OPEN]
Session ID: zhihu-login-state

## Symptom
After logging in with a Zhihu account, the application still displays the user as not logged in.

## Hypotheses
1. OAuth callback succeeds but token/session is not persisted or returned to the frontend.
2. Frontend persistence succeeds but subsequent requests omit credentials, or cookie policy/CORS blocks them.
3. Login-state checking uses the wrong endpoint, host, or environment configuration.
4. User-info validation returns unauthorized and overwrites the authenticated state.
5. Production frontend/backend deployments or OAuth redirect configuration are inconsistent.

## Evidence
Pending runtime reproduction and instrumentation.

## Changes
No business logic changed before evidence collection.
