# Firebase to Local Storage Migration

## Overview
This project has been refactored to remove Firebase dependency and use local file storage instead. All audio files, videos, and transcripts are now stored in the backend's static folder.

## Changes Made

### Backend Changes

1. **New File Upload Routes** (`backend/src/routes/file_upload.py`)
   - `POST /upload/video` - Upload video files
   - `POST /upload/transcript` - Upload transcript JSON
   - `GET /transcript/<session_id>` - Retrieve transcript by session ID

2. **Updated Video Processor** (`backend/src/routes/videoProcessor.py`)
   - Removed Firebase storage integration
   - Merged audio files now saved to `backend/src/static/uploads/`
   - Returns relative URL path instead of Firebase signed URL

3. **Updated App Configuration** (`backend/src/app.py`)
   - Removed Firebase Admin SDK initialization
   - Added static file serving route: `/static/uploads/<filename>`
   - Registered new file upload blueprint

4. **Dependencies** (`backend/requirements.txt`)
   - Removed `firebase_admin`

5. **Environment Variables** (`backend/src/.env`)
   - Removed `FIREBASE_EMAIL`, `FIREBASE_PASSWORD`, `FIREBASE_BUCKET`

### Frontend Changes

1. **VideoUploader Component** (`src/components/VideoUploader.vue`)
   - Replaced Firebase Storage with direct backend API calls
   - Uses XMLHttpRequest for video uploads with progress tracking
   - Uploads transcripts via REST API instead of Firebase

2. **Main Application** (`src/main.ts`)
   - Removed Firebase initialization
   - Removed Firebase imports

3. **Dependencies** (`package.json`)
   - Removed `firebase` package

4. **Environment Variables** (`.env`)
   - Removed all `VITE_FIREBASE_*` variables

## File Storage Structure

```
backend/src/static/uploads/
├── videos/          # Uploaded video files
├── transcripts/     # Transcript JSON files
└── {uuid}.mp3       # Merged audio files
```

## Installation & Setup

### Backend

1. Install dependencies (Firebase is no longer required):
```bash
cd backend
pip install -r requirements.txt
```

2. The upload directories will be created automatically on first run

3. Start the backend server:
```bash
cd src
python app.py
```

### Frontend

1. Remove old Firebase dependency:
```bash
npm uninstall firebase
```

2. Install dependencies:
```bash
npm install
```

3. Update `.env` to ensure `VITE_BACKEND_URL` is set correctly

4. Start the development server:
```bash
npm run dev
```

## API Endpoints

### Upload Video
```
POST /upload/video
Content-Type: multipart/form-data

Body: 
  video: <file>

Response:
  {
    "url": "/static/uploads/videos/{uuid}.{ext}"
  }
```

### Upload Transcript
```
POST /upload/transcript
Content-Type: application/json

Body:
  {
    "transcript": [...],
    "sessionID": "string"
  }

Response:
  {
    "message": "Transcript uploaded successfully"
  }
```

### Get Transcript
```
GET /transcript/{session_id}

Response:
  [transcript data]
```

### Serve Static Files
```
GET /static/uploads/{path}

Returns the requested file
```

## Notes

- All files are stored locally in `backend/src/static/uploads/`
- File paths are relative and served through the Flask backend
- The uploads folder is gitignored to avoid committing large files
- For production deployment, consider using a proper file storage solution or CDN
- Video URLs now include the backend URL prefix (e.g., `http://localhost:5000/static/uploads/videos/...`)

## Migration Checklist

- [x] Remove Firebase Admin SDK from backend
- [x] Create local file storage system
- [x] Add file upload endpoints
- [x] Update video processor to use local storage
- [x] Remove Firebase from frontend
- [x] Update VideoUploader component
- [x] Remove Firebase dependencies
- [x] Clean up environment variables
- [x] Add uploads folder to .gitignore
- [ ] Test video upload functionality
- [ ] Test transcript upload/retrieval
- [ ] Test merged audio functionality

## Potential Improvements

1. Add file size limits and validation
2. Implement file cleanup for old uploads
3. Add authentication/authorization for file access
4. Consider using object storage (S3, MinIO) for production
5. Add file compression for videos
6. Implement streaming for large video files
