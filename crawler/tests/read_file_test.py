import os

file_path = "/Users/jankahnt/Documents/ai/crackmes-dev-environment/crawler/tests/html_samples/sample_provided.html"
try:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        print(f"Content length: {len(content)}")
        print(f"Content starts with: {content[:50]}")
except Exception as e:
    print(f"Error reading file: {e}")
