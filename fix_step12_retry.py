import re

with open("src/confidence/api/routes.py", "r") as f:
    routes = f.read()

# Instead of direct string replacement, let's insert metrics decorators or manually insert
routes = "import time\nfrom confidence.observability.metrics import DECISION_REQUESTS, DECISION_LATENCY, EVENT_INGESTION\n" + routes

# create_decision is at line ~39
routes = routes.replace(
    "    if idempotency_key:",
    "    start_time = time.time()\n    if idempotency_key:"
)

routes = routes.replace(
    "        # Save to idempotency store\n        if idempotency_key:\n            # We dump the pydantic model to dict, then convert UUIDs/Enums to strings for json\n            resp_dict = json.loads(response.model_dump_json())\n            await idemp_store.save_response(idempotency_key, resp_dict)\n\n        return response\n    except ValidationError as e:",
    "        # Save to idempotency store\n        if idempotency_key:\n            # We dump the pydantic model to dict, then convert UUIDs/Enums to strings for json\n            resp_dict = json.loads(response.model_dump_json())\n            await idemp_store.save_response(idempotency_key, resp_dict)\n\n        DECISION_REQUESTS.labels(status=\"success\").inc()\n        DECISION_LATENCY.observe(time.time() - start_time)\n        return response\n    except ValidationError as e:\n        DECISION_REQUESTS.labels(status=\"error_validation\").inc()\n        DECISION_LATENCY.observe(time.time() - start_time)"
)

routes = routes.replace(
    "            detail={\"error\": \"validation_error\", \"messages\": e.errors()}\n        ) from e\n    except Exception as e:",
    "            detail={\"error\": \"validation_error\", \"messages\": e.errors()}\n        ) from e\n    except Exception as e:\n        DECISION_REQUESTS.labels(status=\"error_internal\").inc()\n        DECISION_LATENCY.observe(time.time() - start_time)"
)

routes = routes.replace(
    "    try:\n        await publisher.publish(event)\n        return {\"status\": \"accepted\"}",
    "    try:\n        await publisher.publish(event)\n        EVENT_INGESTION.labels(event_type=event.event_type.value).inc()\n        return {\"status\": \"accepted\"}"
)

with open("src/confidence/api/routes.py", "w") as f:
    f.write(routes)
