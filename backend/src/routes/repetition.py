from flask import request, Blueprint
from util.response import  convert_to_json_resp
from config.openai_connector import init_openai_config
import os

# Check if MongoDB is available
MONGODB_AVAILABLE = os.getenv('MONGO_URI') is not None

if MONGODB_AVAILABLE:
    try:
        from database.models import InterviewAnnotation
    except Exception:
        MONGODB_AVAILABLE = False

repetition_bp = Blueprint('repetitions', __name__)


@repetition_bp.route('/repetition/feedbacks', methods=['POST'])
def get_():
    if not MONGODB_AVAILABLE:
        return convert_to_json_resp({'error': 'Database not configured', 'response': 'Cannot retrieve past interview data without database'}), 503
    data = request.json

    sessionIDs = data['sessionIDs']
    question = data['question']

    concatenated_interview_data = ""
    for i, session_id in enumerate(sessionIDs):
        concatenated_interview_data += f"Interview {i+1}: ```"
        annotations = InterviewAnnotation.objects(sessionID=session_id)
        for annotation in annotations:
            concatenated_interview_data += f"- user annotation: {annotation.annotation}; generated feedback: {annotation.feedback}\n"
        concatenated_interview_data += "```\n"

    
    prompt = f"""Your task is to answer a question based on a these past interviews data. Each interview data is numbered and separated by ```. Each interview data consisted of series of user annotations and generated feedbacks.  
                Question: ```{question}```
                Interview Data: ```{concatenated_interview_data}```"""

    print(prompt)

    openai = init_openai_config()

    response = openai.ChatCompletion.create(
    model="gpt-4o-mini",
    messages=[
        {
        "role": "user",
        "content": prompt
        },
    ],
    )

    response = response["choices"][0]["message"]["content"]
    return convert_to_json_resp(response)