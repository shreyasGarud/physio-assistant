import requests

try:
    r = requests.post(
        "http://localhost:11434/api/chat",
        json={
            "model": "gemma3:1b",
            "messages": [{"role": "user", "content": "Reply with the single word: ready"}],
            "stream": False,
        },
        timeout=180,
    )
    r.raise_for_status()
    print("Ollama says:", r.json()["message"]["content"])
except Exception as e:
    print("Problem:", e)
