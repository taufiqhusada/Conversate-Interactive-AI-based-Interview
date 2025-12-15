from flask import request, Blueprint
from util.response import convert_to_json_resp
import os
import uuid
from werkzeug.utils import secure_filename

file_upload_bp = Blueprint('file_upload', __name__)

# Create uploads directories if they don't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
VIDEO_FOLDER = os.path.join(UPLOAD_FOLDER, 'videos')
TRANSCRIPT_FOLDER = os.path.join(UPLOAD_FOLDER, 'transcripts')

os.makedirs(VIDEO_FOLDER, exist_ok=True)
os.makedirs(TRANSCRIPT_FOLDER, exist_ok=True)

ALLOWED_VIDEO_EXTENSIONS = {'mp4', 'avi', 'mov', 'webm', 'mkv'}
ALLOWED_AUDIO_EXTENSIONS = {'mp3', 'wav', 'ogg', 'webm'}

def allowed_file(filename, allowed_extensions):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

@file_upload_bp.route('/upload/video', methods=['POST'])
def upload_video():
    try:
        if 'video' not in request.files:
            return convert_to_json_resp({"error": "No video file provided"}), 400
        
        file = request.files['video']
        
        if file.filename == '':
            return convert_to_json_resp({"error": "No selected file"}), 400
        
        if file and allowed_file(file.filename, ALLOWED_VIDEO_EXTENSIONS):
            # Generate unique filename
            file_extension = file.filename.rsplit('.', 1)[1].lower()
            unique_filename = f"{uuid.uuid4()}.{file_extension}"
            file_path = os.path.join(VIDEO_FOLDER, unique_filename)
            
            file.save(file_path)
            
            # Return URL path
            video_url = f"/static/uploads/videos/{unique_filename}"
            return convert_to_json_resp({"url": video_url}), 200
        else:
            return convert_to_json_resp({"error": "Invalid file type"}), 400
            
    except Exception as e:
        print(f"Error uploading video: {e}")
        return convert_to_json_resp({"error": str(e)}), 500

@file_upload_bp.route('/upload/transcript', methods=['POST'])
def upload_transcript():
    try:
        data = request.get_json()
        
        if not data or 'transcript' not in data or 'sessionID' not in data:
            return convert_to_json_resp({"error": "Missing transcript or sessionID"}), 400
        
        transcript = data['transcript']
        session_id = data['sessionID']
        
        # Save transcript as JSON file
        filename = f"{session_id}.json"
        file_path = os.path.join(TRANSCRIPT_FOLDER, filename)
        
        import json
        with open(file_path, 'w') as f:
            json.dump(transcript, f)
        
        return convert_to_json_resp({"message": "Transcript uploaded successfully"}), 200
        
    except Exception as e:
        print(f"Error uploading transcript: {e}")
        return convert_to_json_resp({"error": str(e)}), 500

@file_upload_bp.route('/transcript/<session_id>', methods=['GET'])
def get_transcript(session_id):
    try:
        filename = f"{session_id}.json"
        file_path = os.path.join(TRANSCRIPT_FOLDER, filename)
        
        if not os.path.exists(file_path):
            return convert_to_json_resp({"error": "Transcript not found"}), 404
        
        import json
        with open(file_path, 'r') as f:
            transcript = json.load(f)
        
        return convert_to_json_resp(transcript), 200
        
    except Exception as e:
        print(f"Error retrieving transcript: {e}")
        return convert_to_json_resp({"error": str(e)}), 500
