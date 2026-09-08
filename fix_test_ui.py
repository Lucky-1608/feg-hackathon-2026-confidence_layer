with open("test_ui_api.py", "r") as f:
    test = f.read()

test = test.replace(
    "    response = await client.post('/v1/decisions', json=payload)",
    "    response = await client.post('/v1/decisions', json=payload, headers={'Authorization': 'Bearer demo-token'})"
)

with open("test_ui_api.py", "w") as f:
    f.write(test)
