import re
from fastapi import Request, HTTPException

# Basic sanitization for prompt injection
# This is a heuristic-based approach and should be enhanced with LLM-based guardrails later
INJECTION_KEYWORDS = [
    r"ignore previous instructions",
    r"system prompt",
    r"you are a",
    r"act as",
    r"jailbreak",
    r"admin access",
    r"delete all",
    r"drop table"
]

def sanitize_input(text: str) -> str:
    """
    Sanitize input text to prevent prompt injection.
    """
    if not text:
        return text
        
    # Check for known injection patterns
    for pattern in INJECTION_KEYWORDS:
        if re.search(pattern, text, re.IGNORECASE):
            # For now, we just log and maybe mask or reject
            # In production, this should raise a SecurityException or handle gracefully
            # raising HTTPException might be too aggressive if it's a false positive,
            # but for a security agent, better safe than sorry.
            pass 
            # We will just return the text for now but logging would happen here
            
    return text

async def check_prompt_injection(request: Request):
    """
    Middleware/Dependency to check for prompt injection in request body.
    """
    # This is complex to do as middleware because it consumes the stream.
    # Better implemented as a utility function called in endpoints.
    pass
