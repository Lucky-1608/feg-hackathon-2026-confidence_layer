with open("src/confidence/ui/index.html", "r") as f:
    html = f.read()

# Add header to the fetch call
html = html.replace(
    """                const response = await fetch('/v1/decisions', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify(payload)
                });""",
    """                const response = await fetch('/v1/decisions', {
                    method: 'POST',
                    headers: { 
                        'Content-Type': 'application/json',
                        'Authorization': 'Bearer demo-token'
                    },
                    body: JSON.stringify(payload)
                });"""
)

with open("src/confidence/ui/index.html", "w") as f:
    f.write(html)
