
from flask import Flask, request, send_from_directory
from flask_cors import CORS
import os
from routes.interview_annotations import annotations_bp
from routes.interviews import interviews_bp
from routes.feedbacks import feedbacks_bp
from routes.repetition import repetition_bp
from routes.videoProcessor import audio_processor_bp
from routes.simulation import simulation_bp
from routes.moment_identification import identification_bp
from routes.retrieve_data import retrieve_data_bp
from routes.file_upload import file_upload_bp

from database.db import initialize_db
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)
CORS(app)
initialize_db(app)

# Static file serving for uploads
STATIC_FOLDER = os.path.join(os.path.dirname(__file__), 'static', 'uploads')
os.makedirs(STATIC_FOLDER, exist_ok=True)

@app.route("/")
def hello_world():
    return  "hello world"

@app.route("/static/uploads/<path:filename>")
def serve_static_file(filename):
    return send_from_directory(STATIC_FOLDER, filename)

app.register_blueprint(interviews_bp)
app.register_blueprint(annotations_bp)
app.register_blueprint(feedbacks_bp)
app.register_blueprint(repetition_bp)
app.register_blueprint(audio_processor_bp)
app.register_blueprint(simulation_bp)
app.register_blueprint(identification_bp)
app.register_blueprint(retrieve_data_bp)
app.register_blueprint(file_upload_bp)


