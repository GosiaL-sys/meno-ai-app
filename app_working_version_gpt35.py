from flask import Flask, request, jsonify
from flask_cors import CORS
from openai import OpenAI
import traceback
import os
import io
import base64
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from datetime import datetime

app = Flask(__name__)
CORS(app)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

@app.route('/')
def home():
    return "✅ Backend is live and ready!"

@app.route('/generate-plan', methods=['POST'])
def generate_plan():
    data = request.get_json()
    print("DOSTAŁEM DANE:", data)

    prompt = f"""
You are a clinical-grade AI wellness coach for menopausal women.

User profile:
- Age: {{data.get('age')}}
- Weight: {{data.get('weight')}}
- Height: {{data.get('height')}}
- Waist: {{data.get('waist')}}
- Ethnicity: {{data.get('ethnicity')}}
- Symptoms: {{data.get('symptoms')}}
- Medications: {{data.get('medication')}}
- Diet preference: {{data.get('diet')}}
- Allergies: {{data.get('allergies')}}
- Skincare concerns: {{data.get('skincareConcerns')}}
- Activity preferences: {{data.get('activity')}}
- Blood test results: {{data.get('bloodTests')}}

Your task:
1. Create a full 7-day meal plan (Saturday to Friday), including breakfast, lunch, and dinner each day.
2. Do not generate the grocery list until after the full meal plan is complete.
3. Ensure ingredient efficiency (e.g., if 6 eggs are needed, spread them across meals).
4. Include only natural, anti-inflammatory foods tailored to the user's profile (including medication or ethnicity-based needs).
5. For each cooked meal, include a brief prep instruction or a link to a recipe.
6. List daily physical activity based on user’s preferences and age.
7. Provide 3 lifestyle tips to boost skin, mood, and energy.
8. Add one fun seasonal nutrition fact related to {datetime.now().strftime("%B")}.
9. Finally, generate a categorized shopping list containing only the ingredients needed for the week.
"""

    try:
        print("Wysyłam prompt do OpenAI...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{{"role": "user", "content": prompt}}],
            max_tokens=1800
        )
        plan = response.choices[0].message.content

        buffer = io.BytesIO()
        p = canvas.Canvas(buffer, pagesize=letter)
        text = p.beginText(40, 750)
        for line in plan.split('\n'):
            text.textLine(line[:90])
        p.drawText(text)
        p.showPage()
        p.save()

        pdf_data = buffer.getvalue()
        encoded_pdf = base64.b64encode(pdf_data).decode('utf-8')
        buffer.close()

        return jsonify({{"pdf": f"data:application/pdf;base64,{{encoded_pdf}}"}})

    except Exception as e:
        traceback.print_exc()
        return jsonify({{"error": str(e)}}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
