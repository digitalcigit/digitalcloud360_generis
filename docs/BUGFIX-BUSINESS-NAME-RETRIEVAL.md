---
title: "Bug Fix: Business Name Retrieval in Onboarding Flow"
date: "2025-12-26"
status: "fixed"
tags: ["bug-fix", "onboarding", "session-management", "business-name"]
---

# Bug Fix: Business Name Not Retrieved During E2E Tests

## Problem Statement

During E2E tests, the `business_name` entered during onboarding was not being correctly retrieved during site generation, despite previous fixes. The issue manifested as:

- User enters business name in onboarding (e.g., "TICCI 360")
- Onboarding saves correctly with `business_name`
- When coaching starts, a **new session is created** instead of using the onboarding session
- Site generation uses fallback name "Projet Sans Nom" instead of the entered name

## Root Cause Analysis

### Issue 1: Frontend useEffect Race Condition

**File:** `@/genesis/genesis-frontend/src/components/coaching/CoachingInterface.tsx:72-76`

The `useEffect` hook that starts the coaching session had a dependency array that did NOT include `urlSessionId`:

```typescript
// BEFORE (BROKEN)
useEffect(() => {
    if (token && !coachingState) {
        startSession();
    }
}, [token, coachingState]); // ❌ Missing urlSessionId
```

**Why this caused the bug:**
1. Frontend redirects from onboarding with URL: `/coaching?session_id=abc123`
2. Component mounts and `useEffect` fires BEFORE `useSearchParams()` resolves
3. `urlSessionId` is still `null` at this point
4. `startSession()` is called without `session_id`
5. Backend creates a NEW session instead of using the onboarding session
6. Onboarding data (including `business_name`) is lost

### Issue 2: Backend Not Handling Null session_id

**File:** `@/genesis/app/api/v1/coaching.py:138-141`

The backend tried to query Redis with a `None` session_id:

```python
# BEFORE (BROKEN)
session_data_json = await redis_client.get(f"session:{session_id}")
# If session_id is None, this queries "session:None" → always returns None
```

### Issue 3: session_id Lost During Auth Redirects (callbackUrl encoding)

Even after fixing the initial race condition, the `session_id` can still be lost if the user is redirected to `/login` during the flow:

- `/coaching` server redirect previously used a fixed `callbackUrl=/coaching` and dropped `?session_id=...`
- `CoachingInterface` client redirect previously pushed `/login` without preserving the current URL
- `/login` receives `callbackUrl` URL-encoded (because it is passed as a query param), but it previously redirected with `router.push(callbackUrl)` **without decoding**.

Net effect: user lands on an URL like `/coaching%3Fsession_id%3D...` (no actual query string), so `useSearchParams()` returns `null`, and `/coaching/start` is called with `session_id=None`.

### Issue 4: Next.js searchParams can be string[] (session_id dropped)

Even after fixing `callbackUrl` preservation/decoding, `session_id` can still be dropped on the **server-side redirect** if `searchParams.session_id` is not a string.

In Next.js, query params can be provided as `string[]` (e.g., when the param is repeated). If the code only accepts `typeof === 'string'`, it will treat the value as missing and build `callbackUrl=/coaching` without the `session_id`.

### Issue 5: Next.js 15 searchParams is a Promise (CRITICAL)

**File:** `@/genesis/genesis-frontend/src/app/coaching/page.tsx`

In Next.js 15, `searchParams` in server components is a **Promise** that must be awaited:

```typescript
// BEFORE (BROKEN - Next.js 15)
export default async function CoachingPage({
    searchParams,
}: {
    searchParams?: Record<string, string | string[] | undefined>;
}) {
    const sessionIdRaw = searchParams?.session_id; // ❌ searchParams is a Promise, not an object!
    // sessionIdRaw is always undefined because we're accessing a property on a Promise
}
```

**Why this caused the bug:**
1. User navigates to `/coaching?session_id=abc123`
2. Server component receives `searchParams` as a **Promise**
3. Code tries to access `searchParams.session_id` without awaiting
4. `sessionIdRaw` is `undefined` (Promise has no `session_id` property)
5. `callbackUrl` is built as `/coaching` without `session_id`
6. After login redirect, user lands on `/coaching` without `session_id`
7. `CoachingInterface` calls `/coaching/start` with `session_id=None`
8. Backend creates NEW session → onboarding data lost

## Solution

### Fix 1: Add urlSessionId to useEffect Dependencies

**File:** `@/genesis/genesis-frontend/src/components/coaching/CoachingInterface.tsx`

```typescript
// AFTER (FIXED)
useEffect(() => {
    // GEN-WO-008 FIX: Wait for searchParams to be fully resolved before starting
    // This prevents creating a new session before urlSessionId is available
    if (token && !coachingState && !isLoading) {
        console.log('[CoachingInterface] Starting session with urlSessionId:', urlSessionId);
        startSession();
    }
}, [token, coachingState, urlSessionId]); // ✅ Added urlSessionId
```

**Why this works:**
- Now the effect waits for `urlSessionId` to be resolved by Next.js `useSearchParams()`
- When `urlSessionId` changes from `null` to the actual session ID, the effect re-runs
- `startSession()` is called with the correct session ID from the URL

### Fix 2: Add Null Check and Debug Logging

**File:** `@/genesis/app/api/v1/coaching.py`

```python
# AFTER (FIXED)
session_id = request.session_id

# GEN-WO-008 DEBUG: Log incoming session_id
logger.info("coaching_start_request", received_session_id=session_id, user_id=current_user.id)

# Récupérer ou créer la session (GEN-WO-006: préserver onboarding)
session_data_json = await redis_client.get(f"session:{session_id}") if session_id else None
```

### Fix 3: Preserve and Decode callbackUrl During Auth Redirects

**Files:**

- `genesis-frontend/src/app/coaching/page.tsx`
  - Preserves `session_id` when redirecting unauthenticated users to `/login` by including it in `callbackUrl`.
  - Handles `searchParams.session_id` when it is a `string[]`.

- `genesis-frontend/src/components/coaching/CoachingInterface.tsx`
  - Redirects to `/login?callbackUrl=<current path + query>` to preserve `session_id`.

- `genesis-frontend/src/app/login/page.tsx`
  - Decodes `callbackUrl` before redirecting:

```tsx
const rawCallbackUrl = searchParams.get('callbackUrl') || '/coaching';
let callbackUrl = rawCallbackUrl;
try {
  callbackUrl = decodeURIComponent(rawCallbackUrl);
} catch {
  callbackUrl = rawCallbackUrl;
}
router.push(callbackUrl);
```

**Why this works:**
- Prevents querying Redis with `None` as key
- Logs the received `session_id` for debugging
- If `session_id` is `None`, the code falls through to create a new session (expected behavior)

## Data Flow After Fix

```
1. User fills onboarding form
   └─ business_name = "TICCI 360"
   └─ sector = "tech"

2. POST /api/v1/coaching/onboarding
   └─ Saves to Redis: session:{uuid} + onboarding:{uuid}
   └─ Returns: { session_id: uuid, onboarding: {...} }

3. Frontend redirects: /coaching?session_id=uuid
   └─ useSearchParams() resolves urlSessionId = uuid
   └─ useEffect triggers (because urlSessionId changed)

4. POST /api/v1/coaching/start with { session_id: uuid }
   └─ Backend finds existing session in Redis
   └─ Loads onboarding data from onboarding:{uuid}
   └─ Returns same session_id (preserved!)

5. POST /api/v1/coaching/step (5 times)
   └─ All steps saved with same session_id
   └─ Onboarding data preserved in session_data

6. Final step triggers site generation
   └─ _build_brief_from_coaching_steps() loads onboarding
   └─ business_name = "TICCI 360" ✅
   └─ Site generated with correct name
```

## Files Modified

1. **Frontend:**
   - `@/genesis/genesis-frontend/src/components/coaching/CoachingInterface.tsx` (lines 71-79)
     - Added `urlSessionId` to useEffect dependencies
     - Added console logging for debugging
   - `@/genesis/genesis-frontend/src/components/coaching/CoachingInterface.tsx` (redirect to login)
     - Preserve current URL (path + query) in `callbackUrl`.
   - `@/genesis/genesis-frontend/src/app/coaching/page.tsx`
     - **Fix 4 (CRITICAL):** Await `searchParams` Promise before accessing properties (Next.js 15)
     - Preserve `session_id` in `callbackUrl` on server redirect.
     - Accept `searchParams.session_id` as `string[]` by taking the first element.
   - `@/genesis/genesis-frontend/src/app/login/page.tsx`
     - Decode `callbackUrl` before navigation.

2. **Backend:**
   - `@/genesis/app/api/v1/coaching.py` (lines 137-141)
     - Added null check for `session_id`
     - Added debug logging for incoming `session_id`

## Testing

### Manual Test Steps

1. Navigate to `/coaching/onboarding`
2. Enter business name: "TestBusiness_XYZ"
3. Select sector: "tech"
4. Click "Continuer"
5. Verify in logs:
   ```
   onboarding_saved business_name='TestBusiness_XYZ' session_id=abc123
   coaching_start_request received_session_id=abc123
   business_brief_constructed business_name='TestBusiness_XYZ'
   ```

### E2E Evidence (Validated)

Backend logs show the onboarding name is preserved into brief construction:

```
onboarding_saved business_name='TICCI 360' sector=restaurant session_id=b49082f1-8f25-4055-ad44-1b75c32f5fe2
coaching_start_request received_session_id=b49082f1-8f25-4055-ad44-1b75c32f5fe2 user_id=1
business_brief_constructed business_name='TICCI 360' has_onboarding=True onboarding_name='TICCI 360'
```

The preview page confirms the generated website uses the correct name:

`/preview/b49082f1-8f25-4055-ad44-1b75c32f5fe2` → header: "Bienvenue chez TICCI 360"

### Expected Behavior

- Same `session_id` throughout the flow
- `business_name` preserved from onboarding to site generation
- No "Projet Sans Nom" fallback (unless user didn't enter a name)

## Deployment

- **Containers rebuilt:** `docker-compose up -d --build genesis-api frontend`
- **Date:** 2025-12-26
- **Status:** ✅ Deployed and ready for testing

## Related Issues

- GEN-WO-006: Onboarding preservation
- GEN-WO-008: Business name retrieval bug
- Previous fix: Session data preservation in Redis

## Notes for Future Developers

1. **useSearchParams() is async:** Always include URL params in useEffect dependencies
2. **Session ID is critical:** Log it at every step for debugging
3. **Redis keys matter:** Never query with `None` values
4. **Test E2E flows:** Always verify data flows end-to-end, not just individual endpoints
5. **Next.js 15 Breaking Change:** `searchParams` in server components is a **Promise** - always await it before accessing properties
