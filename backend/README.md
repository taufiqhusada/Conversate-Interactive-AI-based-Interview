## How to Setup

1. Install Python 3.8 or higher

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up environment variables:
   ```bash
   cd src
   cp .env.example .env
   ```

4. Edit `.env` file with your credentials:
   - `OPENAI_API_KEY`: Your OpenAI API key (**REQUIRED**)
   - `OPENAI_GPT_MODEL`: Model to use (default: gpt-4o-mini)
   - `JWT_SECRET_KEY`: Random secret key for JWT authentication
   - `MONGO_URI`: Your MongoDB connection string (**OPTIONAL** - app works without it, interview data will be stored in localStorage only)

## How to Run

```bash
cd src
flask --app app run
```

The server will run on `http://127.0.0.1:5000` by default.

## Code Structure

- **Main Application**: `src/app.py`
- **API Routes**: `src/routes/`
  - `interviews.py`: Interview CRUD operations
  - `videoProcessor.py`: Audio merging
  - `simulation.py`: AI interview simulation with GPT-4o-mini
  - `feedbacks.py`: AI feedback generation
  - `moment_identification.py`: Identifying improvement moments
  - `interview_annotations.py`: User annotations
  - `repetition.py`: Feedback analysis across sessions
  - `retrieve_data.py`: Data retrieval endpoints
- **Database**: `src/database/`
  - `db.py`: MongoDB connection
  - `models.py`: Data models
- **Configuration**: `src/config/`
  - `openai_connector.py`: OpenAI API setup
- **Utilities**: `src/util/`
  - `jwt.py`: JWT authentication
  - `response.py`: Response formatting
- **Static Files**: `src/static/uploads/`
  - Stores merged audio files locally

## API Endpoints

### Interviews
- `GET /interviews` - List all interviews
- `POST /interviews` - Create new interview
- `GET /interviews/<id>` - Get specific interview
- `PUT /interviews/<id>` - Update interview
- `DELETE /interviews/<id>` - Delete interview

### Audio Processing
- `POST /audio/merge` - Merge multiple audio tracks with timing

### Simulation
- `POST /simulation/transcript` - Get transcript from Whisper
- `POST /simulation/response` - Generate AI interviewer response

### Feedback
- `POST /feedbacks/conversation` - Get AI feedback on performance

### Static Files
- `GET /static/uploads/<filename>` - Serve uploaded audio files

## Technologies

- **Flask**: Web framework
- **MongoDB**: Database (via mongoengine) - **OPTIONAL** for persistence
- **OpenAI GPT-4o-mini**: AI model for interview simulation and feedback
- **localStorage**: Frontend storage for interview data when MongoDB is not configured
- **FFmpeg**: Audio processing (required for audio merging)
- **PyJWT**: JWT authentication
