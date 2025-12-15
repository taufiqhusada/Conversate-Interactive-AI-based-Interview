from flask import request, Blueprint
from util.response import  convert_to_json_resp
import os

# Check if MongoDB is available
MONGODB_AVAILABLE = os.getenv('MONGO_URI') is not None

if MONGODB_AVAILABLE:
    try:
        from database.models import InterviewAnnotation
    except Exception:
        MONGODB_AVAILABLE = False

annotations_bp = Blueprint('annotations', __name__)

# Routes for CRUD operations on InterviewAnnotation
@annotations_bp.route('/interviews/<sessionID>/annotations', methods=['GET'])
def get_annotations(sessionID):
    if not MONGODB_AVAILABLE:
        return convert_to_json_resp({'annotations': [], 'warning': 'Database not configured'})
    annotations = InterviewAnnotation.objects(sessionID=sessionID)
    return convert_to_json_resp({'annotations': [annotation.to_json() for annotation in annotations]})

@annotations_bp.route('/interviews/<sessionID>/annotations', methods=['POST'])
def create_annotation(sessionID):
    if not MONGODB_AVAILABLE:
        return convert_to_json_resp({'message': 'Annotation created (not persisted - database not configured)', 'id': 'temp_id'})
    data = request.json
    data['sessionID'] = sessionID
    annotation = InterviewAnnotation(**data)
    annotation.save()
    return convert_to_json_resp({'message': 'Annotation created', 'id': str(annotation.id)})

@annotations_bp.route('/interviews/<sessionID>/annotations/<annotation_id>', methods=['GET'])
def get_annotation(sessionID, annotation_id):
    annotation = InterviewAnnotation.objects.get_or_404(id=annotation_id, sessionID=sessionID)
    return convert_to_json_resp({'annotation': annotation})

@annotations_bp.route('/interviews/<sessionID>/annotations/<annotation_id>', methods=['PUT'])
def update_annotation(sessionID, annotation_id):
    annotation = InterviewAnnotation.objects.get_or_404(id=annotation_id, sessionID=sessionID)
    data = request.json
    annotation.update(**data)
    return convert_to_json_resp({'message': 'Annotation updated'})

@annotations_bp.route('/interviews/<sessionID>/annotations/<annotation_id>', methods=['DELETE'])
def delete_annotation(sessionID, annotation_id):
    annotation = InterviewAnnotation.objects.get_or_404(id=annotation_id, sessionID=sessionID)
    annotation.delete()
    return convert_to_json_resp({'message': 'Annotation deleted'})