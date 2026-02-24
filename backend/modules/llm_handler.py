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
    

def extract_medicines_from_prescription(text):

    prompt = f"""
You are a strict information extraction system.

IMPORTANT RULES:
1. ONLY extract medicine names that appear EXACTLY in the text.
2. DO NOT guess.
3. DO NOT add medicines that are not present.
4. If no medicine is found, return: NONE
5. Return output as comma separated values only.
6. No explanation.

Prescription Text:
{text}
"""

    response = ask_llm(prompt)
    return response.strip()
