# NOVA - DRIVEN Program Application

A Flask-based web application for the DRIVEN program, featuring conversational AI interactions across multiple weeks of content.

## Features

- Week-by-week conversational interface
- Database-driven content management (Supabase/PostgreSQL)
- Text-to-speech and speech-to-text integration (ElevenLabs)
- OpenAI GPT integration for dynamic responses
- Progress tracking

## Setup

### 1. Prerequisites

- Python 3.11+
- PostgreSQL database (Supabase recommended)
- OpenAI API key
- ElevenLabs API key (optional, for TTS/STT)

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file in the project root:

```bash
# Flask
FLASK_SECRET_KEY=your-secret-key-here

# OpenAI
OPENAI_API_KEY=your-openai-api-key
OPENAI_MODEL=gpt-4o-mini

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

# Database Connection
DATABASE_URL=postgresql://postgres:your-password@db.your-project.supabase.co:5432/postgres

# ElevenLabs (optional)
ELEVENLABS_API_KEY=your-elevenlabs-api-key
```

### 4. Database Setup

1. Create tables using the schema:
```bash
python scripts/create_all_tables.py
```

Or manually run `database_schema_final.sql` in your Supabase SQL editor.

2. Populate initial data:
```bash
python scripts/populate_all_weeks.py
```

### 5. Run the Application

```bash
python app.py
```

The application will be available at `http://localhost:5000`

## Project Structure

```
.
├── app.py                      # Main Flask application
├── index.html                  # Frontend interface
├── progress_tracker.py         # Progress tracking module
├── database/
│   ├── db_config.py           # Database configuration
│   └── db_models.py           # Database models
├── temporary_main.py           # Week 1 module
├── temporary_week2_main.py     # Week 2 module
├── temporary_main_q16_22.py    # Week 3 module
├── week4_main.py              # Week 4 module
├── week5_main.py              # Week 5 module
├── database_schema_final.sql   # Database schema
└── scripts/
    └── create_all_tables.py    # Table creation script
```

## API Endpoints

- `GET /` - Main application page
- `POST /api/initialize` - Initialize conversation
- `POST /api/send_message` - Send user message
- `POST /api/get_next_message` - Get next question/message
- `POST /api/process_response` - Process user response
- `POST /api/text-to-speech` - Convert text to speech (ElevenLabs)
- `POST /api/speech-to-text` - Convert speech to text (ElevenLabs)

## Week Modules

Each week module (`temporary_main.py`, `temporary_week2_main.py`, etc.) handles:
- Week-specific questions and prompts
- Conversation flow logic
- Validation and completion tracking
- Database integration for content loading

## License

[Your License Here]

