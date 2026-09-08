with open("src/confidence/api/routes.py", "r") as f:
    routes = f.read()

if routes.startswith("from confidence.infrastructure.auth import verify_token\n"):
    routes = routes.replace("from confidence.infrastructure.auth import verify_token\n", "", 1)
    # Insert it after __future__ import
    routes = routes.replace(
        "from __future__ import annotations\n",
        "from __future__ import annotations\nfrom confidence.infrastructure.auth import verify_token\n"
    )

with open("src/confidence/api/routes.py", "w") as f:
    f.write(routes)
