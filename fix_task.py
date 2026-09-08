with open("/home/netha/.gemini/antigravity/brain/913ae8bb-5ad9-4623-9702-d5da15403f37/task.md", "r") as f:
    task = f.read()

# Fix the duplicate/misplaced Step 11 and adjust numbers
task = task.replace("## Step 11: Observability (OpenTelemetry + Prometheus)", "## Step 12: Observability (OpenTelemetry + Prometheus)")
task = task.replace("## Step 12: Health & Readiness", "## Step 13: Health & Readiness")
task = task.replace("## Step 13: Configuration Hardening", "## Step 14: Configuration Hardening")
task = task.replace("## Step 14: Authentication & Security Boundary", "## Step 15: Authentication & Security Boundary")
task = task.replace("## Step 15: Demo Provider Isolation", "## Step 16: Demo Provider Isolation")
task = task.replace("## Step 16: Database Hardening", "## Step 17: Database Hardening")
task = task.replace("## Step 17: Testing Pyramid", "## Step 18: Testing Pyramid")
task = task.replace("## Step 18: Graceful Shutdown, Backpressure & Replay", "## Step 19: Graceful Shutdown, Backpressure & Replay")
task = task.replace("## Step 19: Evaluation & Model Registry Boundaries", "## Step 20: Evaluation & Model Registry Boundaries")
task = task.replace("## Step 20: CI/CD, Deployment, Load Testing & Documentation", "## Step 21: CI/CD, Deployment, Load Testing & Documentation")

with open("/home/netha/.gemini/antigravity/brain/913ae8bb-5ad9-4623-9702-d5da15403f37/task.md", "w") as f:
    f.write(task)
