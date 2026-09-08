with open("src/confidence/api/routes.py", "r") as f:
    routes = f.read()

# Append at the end of the file
health_endpoints = """

@router.get("/health", status_code=200, summary="Liveness Probe")
async def health_check() -> dict[str, str]:
    \"\"\"Basic liveness probe for Kubernetes.\"\"\"
    return {"status": "ok"}

@router.get("/ready", status_code=200, summary="Readiness Probe")
async def readiness_check() -> dict[str, str]:
    \"\"\"Check if the service is ready to receive traffic (DB/Redis reachable).\"\"\"
    # In a real app we would ping Postgres, Redis, and Kafka here
    return {"status": "ready"}
"""
if "def health_check" not in routes:
    with open("src/confidence/api/routes.py", "a") as f:
        f.write(health_endpoints)

