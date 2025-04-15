import openai
from config import OPENAI_KEY

openai.api_key = OPENAI_KEY

def generate_gpt_summary(claim, verdict, confidence):
    prompt = (
        f"A claim was analyzed and found to be {verdict} with confidence {confidence:.2f}.\n\n"
        f"Claim: {claim}\n\n"
        "Write a short summary (1-2 sentences) explaining why."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You summarize fact-checking results."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=100,
            temperature=0.7,
        )
        return response['choices'][0]['message']['content'].strip()

    except Exception as e:
        print(f"❌ GPT summary generation failed: {e}")
        return "Summary could not be generated."
