import ollama

def ask_llm(user_query):
    try:
        response = ollama.chat(
            model="phi3:mini",
            messages=[
                {
                    "role": "system",
                    "content": """
You are an Anti-Doping Compliance AI Assistant.

Respond in STRICT structured format.

Substance: <name>
Status: <BANNED / MONITORED / SAFE>
Category: <category>
Risk Level: <High / Medium / Low>
Confidence: <percentage>
Explanation: <2-3 short lines only>

Keep answers short.
No extra paragraphs.
No storytelling.
"""
                },
                {
                    "role": "user",
                    "content": user_query
                }
            ]
        )

        return response["message"]["content"]

    except Exception as e:
        return f"LLM Error: {str(e)}"
