
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
    - Age: {data.get('age')}
    - Weight: {data.get('weight')}
    - Height: {data.get('height')}
    - Waist: {data.get('waist')}
    - Ethnicity: {data.get('ethnicity')}
    - Symptoms: {data.get('symptoms')}
    - Medications: {data.get('medication')}
    - Diet preference: {data.get('diet')}
    - Allergies: {data.get('allergies')}
    - Skincare: {data.get('skincareConcerns')}
    - Activity Preferences: {data.get('activity')}
    - Blood Test Results: {data.get('bloodTests')}

    === PERSONALIZED WELLNESS PLAN ===

    1. Full 7-day meal plan (Saturday to Saturday)
    2. Use all ingredients efficiently (e.g., if 6 eggs, spread them across the week)
    3. Use only natural, anti-inflammatory foods
    4. Tailor meals to medication and ethnicity where relevant
    5. For each meal that requires prep, suggest a recipe link
    6. List daily physical activity per user profile
    7. List 3 tips to improve skin and energy
    8. Generate fun seasonal fact based on current date: {datetime.now().strftime("%B")}
    9. Generate a shopping list organized by category
    """

    try:
        print("Wysyłam prompt do OpenAI...")
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}],
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

        return jsonify({"pdf": f"data:application/pdf;base64,{encoded_pdf}"})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
