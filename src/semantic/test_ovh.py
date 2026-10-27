import os
from openai import OpenAI

client = OpenAI(base_url="https://oai.endpoints.kepler.ai.cloud.ovh.net/v1",
                api_key=os.environ["OVH_AI_ENDPOINTS_ACCESS_TOKEN"])

response = client.chat.completions.create(model="mistral@latest",
                                          messages=[{"role": "user",
                                                     "content": ("Classify this conference intervention as technical_explanation, question, answer, moderation, introduction, closing or other. Return only the category. \n\n Text: We trained the model using a dataset containing technical talks.")}],
                                                     temperature=0, max_completion_tokens=30)

print("modelo utilizado:", response.model)
print("Resultado:", response.choices[0].message.content)