from flask import request, Blueprint, Response, send_from_directory, url_for
from util.response import  convert_to_json_resp
import subprocess
import tempfile
import os
import json
import uuid


audio_processor_bp = Blueprint('audio_processor', __name__)

# Create uploads directory if it doesn't exist
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'static', 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@audio_processor_bp.route('/audio/merge', methods=['POST'])
def merge_audio():
    try:
        # Get the uploaded audio file from the request
        user_audio = request.files['user_audio']

        print("user_audio.filename", user_audio.filename)

        # Check if the audio file is present
        if not user_audio:
            return convert_to_json_resp({"error": "user_audio file is required."}), 400

        # Save the uploaded audio file to the server
        user_audio_filename = 'user_audio.webm'
        user_audio.save(user_audio_filename)

        # Define the output audio filename
        output_filename = 'output.mp3'

        # Create a temporary directory to store the audio files
        temp_dir = tempfile.mkdtemp()

        # Get the start times from the JSON data
        start_times = json.loads(request.form.get('start_times'))

        # Merge audio with the video based on start times
        filter_complex_str = ''
        audio_inputs = ''
        for i, audio_file in enumerate(request.files.getlist('audio')):
            audio_filename = os.path.join(temp_dir, f'audio_{i}.opus')
            audio_file.save(audio_filename)

            print(audio_filename)

            start_time = start_times[i]
            
            # Delay the audio based on start time
            filter_complex_str += f'[{i+1}:a]adelay={int(start_time*1000)}|{int(start_time*1000)}[a{i+1}];'

            audio_inputs += f'-i {audio_filename} '

        filter_complex_str += '[0:a]' + ''.join([f'[a{i+1}]' for i in range(len(request.files.getlist('audio')))])
        filter_complex = f'{filter_complex_str}amix=inputs={len(request.files.getlist("audio")) + 1}:duration=first[aout]'

        cmd = [
            'ffmpeg',
            '-i', user_audio_filename,
            *audio_inputs.split(),
            '-filter_complex', filter_complex,
            '-map', '[aout]',
            '-c:v', 'copy', 
            '-y',
            output_filename
        ]

        print(cmd)
        subprocess.run(cmd, check=True)

        # Clean up temporary files and directory
        for i in range(len(request.files.getlist('audio'))):
            os.remove(os.path.join(temp_dir, f'audio_{i}.opus'))
        os.rmdir(temp_dir)

        # Save merged audio to static uploads folder
        unique_filename = f"{uuid.uuid4()}.mp3"
        destination_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        os.rename(output_filename, destination_path)
        
        # Generate URL for the uploaded file
        merged_audio_url = f"/static/uploads/{unique_filename}"
        print(merged_audio_url)

        os.remove(user_audio_filename)

        return convert_to_json_resp({'url': merged_audio_url})


    except Exception as e:
        print(e)
        return convert_to_json_resp({"error": str(e)}), 500