# Conversate: Interactive AI-based Interview Training Tool

[![ArXiv Paper](https://img.shields.io/badge/arXiv-2410.05570-b31b1b.svg)](https://arxiv.org/abs/2410.05570)
[![Conference Paper](https://img.shields.io/badge/Paper-ACM%20GROUP%202025-blue)](https://dl.acm.org/doi/pdf/10.1145/3701188)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)

**Conversate** is a web-based application that supports reflective learning in job interview practice by leveraging Large Language Models (LLMs) for interactive interview simulations and dialogic feedback. This tool was developed as part of research published at **ACM GROUP 2025**.

![Overall System Illustration](public/readme_images/Overall%20Illustration.png)

## 🎯 Overview

Job interviews play a critical role in shaping one's career, yet practicing interview skills can be challenging, especially without access to human coaches or peers for feedback. Conversate addresses this challenge by providing:

- **Interactive Interview Simulations**: AI-powered behavioral interview practice sessions
- **Real-time Transcript Generation**: Automatic speech-to-text conversion during interviews
- **Self-reflection Tools**: Annotation capabilities for user introspection
- **Dialogic Feedback**: Two-way interactive feedback discussions with AI

## ✨ Key Features

### 1. Interview Simulation
![Interview Simulation Feature](public/readme_images/Feature%201_Simulation.png)

- Start practice sessions by providing a job title (e.g., "entry-level software engineer")
- AI interviewer asks contextually relevant behavioral interview questions
- Real-time speech recognition and response processing
- Adaptive follow-up questions based on user responses

### 2. Interactive Annotation System
![Annotation Feature](public/readme_images/Feature%202_Annotation.png)

- Review complete interview transcripts
- Highlight and annotate specific sections for self-reflection
- Add personal notes and observations about performance
- Track areas for improvement across multiple sessions

### 3. Dialogic Feedback
![Feedback Feature](public/readme_images/Feature%203_Feedback.png)

- Engage in two-way conversations with AI about your performance
- Receive detailed feedback on interview responses
- Ask questions and get clarifications about improvement areas
- Iteratively refine answers based on AI guidance

## 🚀 Getting Started

### Prerequisites

- Node.js 18+ and npm
- Python 3.8+
- OpenAI API key
- MongoDB connection string (**optional** - app works without it, data persists in-memory only)

### Frontend Setup

```bash
# Clone the repository
git clone https://github.com/your-username/conversate-interview-tool.git
cd conversate-interview-tool

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env
# Edit .env with your backend URL (default: http://127.0.0.1:5000)

# Start development server
npm run dev
```

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Set up environment variables
cd src
cp .env.example .env
# Edit .env with your OpenAI API key (REQUIRED)
# Optionally add MongoDB URI if you want to persist interview data
# Add JWT secret key for authentication

# Run the Flask server
flask --app app run
```

The server will start on `http://127.0.0.1:5000`. The app works fully without MongoDB - interview data will be stored in browser localStorage instead.

## 🏗️ Architecture

### Frontend (Vue.js + TypeScript)
- **Framework**: Vue 3 with TypeScript
- **UI**: Bootstrap 5 for responsive design
- **State Management**: Vuex for application state
- **HTTP Client**: Axios for API communication
- **Build Tool**: Vite for fast development and building

### Backend (Flask + Python)
- **Framework**: Flask with CORS support
- **AI Integration**: OpenAI GPT-4o-mini for interview simulation and feedback
- **Speech Processing**: Whisper API for speech-to-text conversion
- **Database**: MongoDB for data persistence (**optional** - app works without it)
- **File Storage**: Local file system (backend/src/static/uploads/) for audio files
- **Authentication**: JWT-based user authentication

### Key Components

```
frontend/
├── src/
│   ├── components/          # Vue components
│   ├── views/              # Page-level components
│   ├── services/           # API service layer
│   ├── router/             # Vue Router configuration
│   └── assets/             # Static assets
└── public/
    └── readme_images/      # Documentation images

backend/
├── src/
│   ├── routes/             # API endpoints
│   ├── config/             # Configuration files
│   ├── database/           # Database models and connection
│   └── util/               # Utility functions
```

## 🎨 Development

### Available Scripts

```bash
# Frontend
npm run dev          # Start development server
npm run build        # Build for production
npm run preview      # Preview production build
npm run type-check   # TypeScript type checking

# Backend
flask --app src/app.py run    # Start Flask development server
python -m pytest             # Run tests (if available)
```

### Code Structure

**Frontend:**
- Main Vue application: `src/App.vue`
- Individual components: `src/components/`
- Page routing: `src/router/`
- API services: `src/services/`

**Backend:**
- Main Flask application: `src/app.py`
- API route implementations: `src/routes/`
- Database models: `src/database/models.py`
- OpenAI configuration: `src/config/openai_connector.py`

## 📄 License & Usage

This software is released under the **Apache License 2.0** to encourage open research and collaboration while ensuring proper attribution.

### Academic Usage Requirements

If you use this software in your research, please cite our paper:

```bibtex
@article{daryanto2025conversate,
  title={Conversate: Supporting Reflective Learning in Interview Practice Through Interactive Simulation and Dialogic Feedback},
  author={Daryanto, Taufiq and Ding, Xiaohan and Wilhelm, Lance T and Stil, Sophia and Knutsen, Kirk McInnis and Rho, Eugenia H},
  journal={Proceedings of the ACM on Human-Computer Interaction},
  volume={9},
  number={1},
  pages={1--32},
  year={2025},
  publisher={ACM New York, NY, USA}
}
```

## 📞 Contact

For questions about the research, technical implementation, or licensing:

- **Taufiq Daryanto** - taufiqhd@vt.edu
- **Research Paper** - [https://arxiv.org/abs/2410.05570]
- **ACM Digital Library** - [https://dl.acm.org/doi/pdf/10.1145/3701188]

---

