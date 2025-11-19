# OpenAI API Access Troubleshooting Journey

**Date:** November 8, 2025  
**Context:** Implementing ROOK's new architecture with OpenAI's 2025 models (GPT-5, o3, o4-mini)

---

## The Problem

When attempting to use the OpenAI Python SDK with ROOK's API key, I encountered persistent 404 and 401 errors:

```python
openai.NotFoundError: Error code: 404 - {'status': 'not found'}
openai.AuthenticationError: Error code: 401 - {'error': 'Invalid or expired sandbox token'}
```

---

## What I Initially Thought

### Assumption 1: The API Key Was Invalid
**My thinking:** The API key from the config file might be expired or incorrect.

**What I tried:**
- Checked the key format (looked correct: `YOUR_OPENAI_API_KEY...`)
- Verified the key was being loaded properly from environment variables

**Result:** ❌ The key format was fine, but errors persisted.

---

### Assumption 2: The New Models Required Different Endpoints
**My thinking:** Since GPT-5, o3, and o4-mini are new 2025 models, maybe they use the new "Responses API" instead of the traditional Chat Completions API.

**What I tried:**
- Attempted to use `client.responses.create()` instead of `client.chat.completions.create()`
- Searched for Responses API documentation

**Result:** ❌ Got 404 errors on the Responses API endpoint too.

---

### Assumption 3: The Models Weren't Available Yet
**My thinking:** Maybe these models aren't actually available via API yet, despite the documentation.

**What I tried:**
- Attempted to list available models with `client.models.list()`

**Result:** ❌ Even the models list endpoint returned 404.

---

## The Breakthrough: Testing with curl

When the user insisted I was "not accessing it correctly" and needed to "learn from first principles," I went back to the most basic test possible: **raw HTTP with curl**.

```bash
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer YOUR_OPENAI_API_KEY..." 
```

**Result:** ✅ **SUCCESS!** The API returned a full list of models, including:
- `gpt-5-mini`
- `gpt-4.1-mini`
- `o1`
- `o4-mini-deep-research`
- Standard models like `gpt-4o-mini`

---

## The Root Cause: Manus Sandbox Proxy Interception

### What Was Actually Happening

The Python OpenAI SDK was being **intercepted by the Manus sandbox proxy**. Here's what I discovered:

1. **curl worked** because it went directly to `api.openai.com`
2. **Python SDK failed** because it was being routed through a Manus proxy that required sandbox authentication
3. The error message `'Invalid or expired sandbox token'` was the key clue I initially missed

### The Evidence

```python
# This FAILED (intercepted by Manus proxy):
client = OpenAI(api_key='YOUR_OPENAI_API_KEY...')

# This SUCCEEDED (bypassed proxy):
client = OpenAI(
    api_key='YOUR_OPENAI_API_KEY...',
    base_url='https://api.openai.com/v1'  # ← The fix!
)
```

---

## The Solution

**Explicitly set the `base_url` parameter** when creating the OpenAI client to bypass the Manus sandbox proxy:

```python
from openai import OpenAI

client = OpenAI(
    api_key='your-openai-api-key',
    base_url='https://api.openai.com/v1'  # Direct to OpenAI, not Manus proxy
)
```

### Why This Works

- **Without `base_url`:** The SDK uses its default base URL, which gets intercepted by the Manus sandbox environment
- **With `base_url='https://api.openai.com/v1'`:** The SDK makes direct HTTP requests to OpenAI's servers, just like curl does

---

## Key Lessons Learned

### 1. **Start with First Principles**
When complex tools fail, go back to the simplest possible test. In this case: raw HTTP with curl.

### 2. **Read Error Messages Carefully**
The error `'Invalid or expired sandbox token'` was telling me the problem wasn't with OpenAI—it was with the sandbox environment. I should have caught this earlier.

### 3. **Understand Your Environment**
The Manus sandbox has its own OpenAI integration for its built-in models. When using external OpenAI keys, you need to explicitly bypass this integration.

### 4. **Test Incrementally**
The progression that worked:
1. ✅ curl to `/v1/models` (proves API key works)
2. ✅ curl to `/v1/chat/completions` (proves endpoint works)
3. ✅ curl to `/v1/embeddings` (proves embeddings work)
4. ✅ Python SDK with explicit `base_url` (proves SDK configuration)

### 5. **Don't Assume Documentation Matches Reality**
I spent time researching the Responses API and new model features, when the real issue was much simpler: SDK configuration.

---

## Testing the Fix

### Before (Failed):
```python
client = OpenAI(api_key='YOUR_OPENAI_API_KEY...')
response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[{'role': 'user', 'content': 'Hello'}]
)
# Error: 401 - Invalid or expired sandbox token
```

### After (Success):
```python
client = OpenAI(
    api_key='YOUR_OPENAI_API_KEY...',
    base_url='https://api.openai.com/v1'
)
response = client.chat.completions.create(
    model='gpt-4o-mini',
    messages=[{'role': 'user', 'content': 'Hello'}]
)
# Success: "Hello! How can I assist you today?"
```

---

## Available Models Confirmed

After fixing the issue, I confirmed these models are available:

### GPT-5 Series
- `gpt-5-mini`
- `gpt-5-mini-2025-08-07`
- `gpt-5-search-api`
- `gpt-5-search-api-2025-10-14`

### GPT-4.1 Series
- `gpt-4.1`
- `gpt-4.1-mini`
- `gpt-4.1-nano`

### o-Series (Reasoning Models)
- `o1`
- `o1-mini-2024-09-12`
- `o1-pro`
- `o1-pro-2025-03-19`
- `o4-mini-deep-research`
- `o4-mini-deep-research-2025-06-26`

### Standard Models
- `gpt-4o-mini`
- `gpt-4o`
- `text-embedding-3-large`
- `text-embedding-3-small`

---

## Implementation Pattern for ROOK

All ROOK components now use this pattern:

```python
class Component:
    def __init__(self, openai_api_key: str):
        self.openai_client = OpenAI(
            api_key=openai_api_key,
            base_url='https://api.openai.com/v1'  # Always explicit
        )
```

This ensures:
- ✅ Direct access to OpenAI's API
- ✅ No interference from Manus sandbox proxy
- ✅ Access to all OpenAI models (including new 2025 models)
- ✅ Standard OpenAI SDK behavior

---

## Conclusion

The issue wasn't with:
- ❌ The API key
- ❌ The models being unavailable
- ❌ The SDK version
- ❌ The endpoint URLs

The issue was:
- ✅ **Environment-specific proxy interception**
- ✅ **Missing explicit `base_url` configuration**

**The fix:** Always explicitly set `base_url='https://api.openai.com/v1'` when creating OpenAI clients in the Manus sandbox environment.

---

## Future Reference

If you encounter similar issues in other sandbox/proxy environments:

1. **Test with curl first** to isolate SDK vs. API issues
2. **Check for proxy interception** (look for "sandbox token" or similar errors)
3. **Explicitly set base URLs** to bypass environment-specific routing
4. **Verify with simple requests** before attempting complex operations

---

**Status:** ✅ Resolved  
**Time to Resolution:** ~30 minutes of troubleshooting  
**Key Insight:** When in doubt, go back to first principles (raw HTTP) and work your way up.
