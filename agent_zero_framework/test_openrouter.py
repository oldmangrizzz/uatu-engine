import os
os.environ["LITELLM_LOG"] = "DEBUG"  # Turn ON logging to see what's happening

from litellm import completion

response = completion(
    model="openrouter/anthropic/claude-3.5-sonnet",
    messages=[{"role": "user", "content":  "Say 'WORKING' if you can read this"}],
    api_key="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",  # PASTE YOUR REAL KEY
    extra_headers={
        "HTTP-Referer": "https://agent-zero.ai",
        "X-Title": "Agent Zero"
    }
)

print("✅ SUCCESS!")
print(response. choices[0].message.content)
