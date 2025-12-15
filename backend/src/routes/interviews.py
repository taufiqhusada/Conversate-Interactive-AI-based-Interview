
from flask import Blueprint, request, jsonify
from util.response import  convert_to_json_resp
from util.jwt import generate_jwt_token
import os

# Check if MongoDB is available
MONGODB_AVAILABLE = os.getenv('MONGO_URI') is not None

if MONGODB_AVAILABLE:
    try:
        from database.models import Interview, InterviewTranscript
    except Exception as e:
        print(f"Warning: Could not import database models: {e}")
        MONGODB_AVAILABLE = False

interviews_bp = Blueprint('interviews', __name__)

@interviews_bp.route('/interviews', methods=['GET'])
def get_interviews():
    if not MONGODB_AVAILABLE:
        return convert_to_json_resp({'interviews': [], 'warning': 'Database not configured'})
    interviews = Interview.objects.all()
    return convert_to_json_resp({'interviews': interviews})

@interviews_bp.route('/interviews/<id>', methods=['GET'])
def get_interview(id):
    if not MONGODB_AVAILABLE:
        return convert_to_json_resp({'error': 'Database not configured'}), 503
    interview = Interview.objects.get_or_404(id=id)
    return convert_to_json_resp({'interview': interview})

@interviews_bp.route('/interviews', methods=['POST'])
def create_interview():
    data = request.json
    
    if not MONGODB_AVAILABLE:
        # Generate token without saving to database
        token = generate_jwt_token({
            'sessionID': data.get('sessionID', 'temp_session')
        }, 10080)
        return convert_to_json_resp({
            'message': 'Interview created (not persisted - database not configured)',
            'token': token,
            'data': {'token': token}
        })
    
    interview = Interview(**data)
    interview.save()

    token = generate_jwt_token({
        'sessionID': interview.sessionID
    }, 10080)
    return convert_to_json_resp({'message': 'Interview created', 'token': token, 'data': {'token': token}})
    
@interviews_bp.route('/interviews/<id>', methods=['PUT'])
def update_interview(id):
    if not MONGODB_AVAILABLE:
        return convert_to_json_resp({'message': 'Interview updated (not persisted - database not configured)'})
    data = request.json
    interview = Interview.objects.get_or_404(id=id)
    interview.update(**data)
    return convert_to_json_resp({'message': 'Interview updated'})

@interviews_bp.route('/interviews/<id>', methods=['DELETE'])
def delete_interview(id):
    if not MONGODB_AVAILABLE:
        return convert_to_json_resp({'message': 'Interview deleted (not persisted - database not configured)'})
    interview = Interview.objects.get_or_404(id=id)
    interview.delete()
    return convert_to_json_resp({'message': 'Interview deleted'})

@interviews_bp.route('/interviews/transcript', methods=['POST'])
def create_interview_transcript():
    if not MONGODB_AVAILABLE:
        return convert_to_json_resp({'message': 'Interview transcript created (not persisted - database not configured)'})
    data = request.json
    interview = InterviewTranscript(**data)
    interview.save()
    return convert_to_json_resp({'message': 'Interview transcript created'})