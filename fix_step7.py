import re
from pathlib import Path

# 1. Update routes.py to add idempotency
with open("src/confidence/api/routes.py", "r") as f:
    routes = f.read()

# Add Idempotency-Key header to create_decision
if "idempotency_key: str | None = Header(None, alias=\"Idempotency-Key\")" not in routes:
    routes = routes.replace(
        "    request: CreateDecisionRequest,",
        "    request: CreateDecisionRequest,\n    idempotency_key: str | None = Header(None, alias=\"Idempotency-Key\"),"
    )
    routes = routes.replace(
        "from fastapi import APIRouter, Depends, HTTPException, Request, status",
        "from fastapi import APIRouter, Depends, Header, HTTPException, Request, status"
    )
    
    # We will just inject it into the function body, but wait, it's easier to just rewrite routes.py.
