# NOVA Career Coach System Architecture

## Executive Summary

The NOVA Career Coach is an AI-powered conversational system designed to support the DRIVEN program, a multi-week career development curriculum. The system provides personalized coaching through natural language conversations, supporting both text and voice interactions.

**Current State:**
- ✅ Fully functional system with in-memory state management
- ✅ Hardcoded prompts and questions in Python files
- ✅ Database schema designed and ready for integration
- ⚠️ Database exists but code does not yet use it
- ⚠️ Migration from hardcoded to database pending

**Key Features:**
- Multi-week program support (Weeks 1-6)
- Voice and text input/output
- Real-time AI-powered responses
- Session-based conversation management
- Progress tracking (currently JSON-based)

---

## 1. System Overview

### 1.1 Purpose

The NOVA Career Coach system serves as an intelligent tutoring system (ITS) that guides users through the DRIVEN program. Each week focuses on different career development topics, with NOVA (the AI coach) providing personalized feedback, asking clarifying questions, and adapting responses based on user input using scenario-based classification.

### 1.2 Core Capabilities

- **Conversational Interface**: Natural language dialogue with context awareness
- **Multi-Modal Input**: Text and voice input support (ElevenLabs STT/TTS)
- **Adaptive Responses**: Scenario-based response generation using LLM classification
- **Progress Tracking**: JSON-based progress tracking (migrating to database)
- **Session Management**: Flask session-based user identification
- **Content Organization**: Prompts organized for easy client handoff (database ready)

---

## 2. Current System Architecture

### 2.1 High-Level Architecture (Current State)

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENT LAYER                              │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Frontend (index.html)                                    │  │
│  │  • Vanilla JavaScript UI                                 │  │
│  │  • Voice capture (Web Audio API)                         │  │
│  │  • Text input handling                                    │  │
│  │  • Real-time chat interface                              │  │
│  │  • TTS audio playback (ElevenLabs)                        │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTPS/REST API
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      API GATEWAY LAYER                          │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Root Flask App (app.py)                                  │  │
│  │  • Request routing to week modules                        │  │
│  │  • TTS/STT endpoints (/api/tts, /api/stt)                 │  │
│  │  • Static file serving                                    │  │
│  │  • CORS configuration                                     │  │
│  │  • Health check endpoints                                 │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ Routes to /week{N}/api/*
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    BUSINESS LOGIC LAYER                         │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Week Modules (week{N}_main.py)                           │  │
│  │  • Conversation flow management                           │  │
│  │  • Question sequencing                                    │  │
│  │  • Response processing                                    │  │
│  │  • State management (IN-MEMORY)                           │  │
│  │  • Hardcoded QUESTIONS dict                               │  │
│  │  • Hardcoded SYSTEM_PROMPTS dict                           │  │
│  │  • Hardcoded content blocks                               │  │
│  └───────────────────────────────────────────────────────────┘  │
│                              │                                   │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  Progress Tracker (progress_tracker.py)                   │  │
│  │  • JSON file-based progress tracking                      │  │
│  │  • Multi-week coordination                                │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ LLM API Calls
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    EXTERNAL SERVICES LAYER                      │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │  OpenAI API  │  │ ElevenLabs  │                            │
│  │  (GPT-4o-mini│  │  TTS/STT     │                            │
│  │  LLM)        │  │  API         │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ (Database exists but not used)
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                    DATABASE LAYER (Ready, Not Integrated)       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  PostgreSQL Database (Supabase)                           │  │
│  │  • Schema created                                         │  │
│  │  • Tables ready                                          │  │
│  │  • Connection configured                                 │  │
│  │  • ⚠️  Not yet populated with data                       │  │
│  │  • ⚠️  Code does not use it                              │  │
│  └───────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

### 2.2 Current Data Flow

**User Submits Response:**
```
1. Frontend → POST /week4/api/process_response
   { message: "I learned about asking for help", question_number: 1 }

2. Week Module (week4_main.py):
   - Gets session_id from Flask session
   - Retrieves state from in-memory dict: conversation_states[session_id]
   - Loads hardcoded QUESTIONS[1] and SYSTEM_PROMPTS[1]
   - Processes with LLM
   - Updates in-memory state
   - Saves to JSON file (progress_tracker)

3. Returns response to frontend
```

**Current State Storage:**
- ✅ In-memory: `conversation_states = {}` (lost on restart)
- ✅ JSON file: `user_progress.json` (persists)
- ⚠️ Database: Schema ready but unused

---

## 3. Database Architecture (Ready for Integration)

### 3.1 Database Schema Overview

The database schema is designed to match current code functionality while using `session_id` instead of user authentication.

#### Content Tables

**`weeks`** - Program structure
- Week metadata (number, name, title, description)
- Video and exercise content summaries
- Welcome messages
- Active/inactive status

**`questions`** - All questions for each week
- Question text and ordering
- Question types (open-ended, yes/no, multiple choice)
- Max iterations per question
- Validation requirements

**`system_prompts`** - ALL LLM prompts
- **Prompt Types Supported:**
  - `classifier` - Determines scenario (SCENARIO_1, SCENARIO_2, SCENARIO_3)
  - `validation` - Validates completeness
  - `scenario_1_respond` - Response for SCENARIO_1
  - `scenario_2_respond` - Response for SCENARIO_2
  - `scenario_3_respond` - Response for SCENARIO_3
  - `intro` - Canned responses before questions
  - `outro` - Canned responses after questions
- Linked to specific questions
- Supports scenario-based responses

**`week_content_blocks`** - Reusable content snippets
- Video summaries (e.g., `WEEK4_VIDEOS_EXERCISES`)
- Exercise descriptions (e.g., `WEEK4_EXERCISE1`, `WEEK4_EXERCISE2`)
- Dynamically inserted into prompts via `{BLOCK_NAME}`

#### Response & State Tables

**`conversation_states`** - Current conversation state
- Uses `session_id` (no user authentication)
- JSONB storage matching current code structure:
  ```json
  {
    "answers": {1: ["answer1", "answer2"], 2: ["answer3"]},
    "nova_responses": {1: ["response1"], 2: ["response2"]},
    "iteration_count": {1: 2, 2: 1},
    "question_completed": {1: true, 2: false},
    "scenarios": {1: "SCENARIO_1", 2: "SCENARIO_2"},
    "name": "User Name"
  }
  ```
- Current question number
- Persists across server restarts

**`user_answers`** - User responses (CRITICAL)
- Stores all user answers per question
- Supports multiple iterations
- **Used for prompt variable substitution**: `{Answer to question 4}`
- Uses `session_id` (no user table needed)

**`question_completions`** - Completion tracking (CRITICAL)
- Tracks completion status (when to move to next question)
- Iteration counts
- Scenario classifications (SCENARIO_1, SCENARIO_2, SCENARIO_3)
- **Used for flow control**

**`conversation_messages`** - Full message history
- All user messages and NOVA responses
- Message types (text/voice)
- Prompt tracking
- Timestamps for analytics

### 3.2 Database Connection

**Configuration:**
- **Database**: PostgreSQL (Supabase)
- **Connection**: Via `DATABASE_URL` or Supabase credentials
- **ORM**: Flask-SQLAlchemy (ready, not yet integrated)
- **Connection Pooling**: Configured for performance

**Current Status:**
- ✅ Connection verified and working
- ✅ Schema created in Supabase
- ⚠️ Tables exist but are empty
- ⚠️ Code does not use database yet

---

## 4. Technology Stack

### 4.1 Backend

- **Python 3.13**: Core programming language
- **Flask**: Web framework and API server
- **Flask-SQLAlchemy**: ORM (configured, not yet used)
- **SQLAlchemy**: Database abstraction layer
- **PostgreSQL**: Relational database (Supabase)
- **psycopg2**: PostgreSQL adapter

### 4.2 Frontend

- **HTML5/CSS3**: Structure and styling
- **JavaScript (ES6+)**: Client-side logic
- **Web Audio API**: Voice capture and playback
- **Fetch API**: HTTP requests to backend

### 4.3 External Services

- **OpenAI API**: Large Language Model (GPT-4o-mini)
  - Response generation
  - Scenario classification
  - Content validation

- **ElevenLabs API**: Voice services
  - Text-to-Speech (TTS)
  - Speech-to-Text (STT)

- **Supabase**: Database hosting
  - PostgreSQL database
  - Connection pooling
  - API keys management

### 4.4 Development Tools

- **python-dotenv**: Environment variable management
- **Flask-CORS**: Cross-origin resource sharing
- **Werkzeug**: WSGI utilities

---

## 5. Current Data Structures

### 5.1 In-Memory State Structure

**Current Code:**
```python
conversation_states = {
    "session_id_123": ConversationState(
        name="John",
        current_question=1,
        answers={1: ["answer1", "answer2"], 2: ["answer3"]},
        nova_responses={1: ["response1"], 2: ["response2"]},
        iteration_count={1: 2, 2: 1},
        question_completed={1: True, 2: False},
        q1_scenario="SCENARIO_1",
        q2_scenario="SCENARIO_2"
    )
}
```

**Database Equivalent:**
- `conversation_states.conversation_data` (JSONB) - Stores all state
- `user_answers` - Separate rows per answer
- `question_completions` - Completion tracking
- `conversation_messages` - Full history

### 5.2 Hardcoded Content Structure

**Current Code:**
```python
QUESTIONS = {
    1: "What was one main idea you took away?",
    2: "How was your experience...",
    # Hardcoded in Python
}

SYSTEM_PROMPTS = {
    1: {
        "classifier": "...",
        "scenario_1_respond": "...",
        "scenario_2_respond": "...",
        # Hardcoded in Python
    }
}

WEEK4_VIDEOS_EXERCISES = "..."  # Hardcoded constant
```

**Database Equivalent:**
- `questions` table - Question text
- `system_prompts` table - All prompt types
- `week_content_blocks` table - Content blocks

---

## 6. Key Components

### 6.1 Root Application (`app.py`)

**Responsibilities:**
- Serves static frontend files
- Routes requests to week modules
- Handles TTS/STT endpoints
- Manages CORS configuration
- Provides health check endpoints

**Key Endpoints:**
- `GET /` - Serve index.html
- `POST /api/tts` - Text-to-speech conversion
- `POST /api/stt` - Speech-to-text conversion
- `GET /health` - Health check

### 6.2 Week Modules (`week{N}_main.py`)

**Current Implementation:**
- Week 1: `temporary_main.py`
- Week 2: `temporary_week2_main.py`
- Week 3: `temporary_main_q16_22.py`
- Week 4: `week4_main.py`
- Week 5: `week5_main.py`

**Responsibilities:**
- Manage conversation flow for specific week
- Process user responses
- Generate NOVA responses via LLM
- Track question completion
- Handle multi-iteration questions

**Current State:**
- Uses in-memory `conversation_states` dict
- Hardcoded `QUESTIONS` and `SYSTEM_PROMPTS` dicts
- Hardcoded content blocks (e.g., `WEEK4_VIDEOS_EXERCISES`)

**Key Endpoints (per week):**
- `POST /week{N}/api/initialize` - Initialize week session
- `POST /week{N}/api/get_next_message` - Get next question/message
- `POST /week{N}/api/process_response` - Process user response
- `GET /week{N}/api/progress/status` - Get progress status

### 6.3 Progress Tracker (`progress_tracker.py`)

**Current Implementation:**
- JSON file-based progress tracking (`user_progress.json`)
- Multi-week progress coordination
- Session-based user tracking

**Future Migration:**
- Will use `question_completions` table
- Will use `conversation_states` table

### 6.4 Database Configuration (`database/db_config.py`)

**Status:** ✅ Created and configured

**Responsibilities:**
- Initialize database connection
- Manage Supabase credentials
- Provide database utility functions
- Handle connection pooling

**Key Functions:**
- `init_db(app)` - Initialize database for Flask app
- `get_database_url()` - Get connection string from environment
- `get_supabase_keys()` - Retrieve Supabase API keys
- `reset_database(app)` - Clear and recreate all tables

### 6.5 Database Models (`database/db_models.py`)

**Status:** ⚠️ **NOT YET CREATED** - Critical missing component

**Needed:**
- SQLAlchemy models for all tables
- Query helper methods
- Data transformation utilities

---

## 7. API Endpoints

### 7.1 Root Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Serve frontend HTML |
| `/api/tts` | POST | Convert text to speech |
| `/api/stt` | POST | Convert speech to text |
| `/api/elevenlabs/test` | GET | Test ElevenLabs API key |
| `/health` | GET | Health check |

### 7.2 Week-Specific Endpoints

Each week module exposes the following endpoints under `/week{N}/api/`:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/initialize` | POST | Initialize week session |
| `/get_next_message` | POST | Get next question/message |
| `/process_response` | POST | Process user response |
| `/progress/status` | GET | Get user progress |

### 7.3 Request/Response Examples

**Initialize Week:**
```json
POST /week4/api/initialize
{
  "name": "John Doe"
}

Response:
{
  "success": true,
  "message": "Welcome to Week 4, John!...",
  "week": 4
}
```

**Process Response:**
```json
POST /week4/api/process_response
{
  "message": "I learned about asking for help",
  "question_number": 1
}

Response:
{
  "success": true,
  "response": "Great! Asking for help is an important skill...",
  "move_to_next": false,
  "iteration": 1
}
```

---

## 8. Database Integration Status

### 8.1 What's Complete

✅ **Database Schema:**
- All tables designed and created
- Indexes optimized
- Foreign keys configured
- Triggers for auto-updates
- Helper functions created

✅ **Database Connection:**
- Supabase credentials configured
- Connection verified and working
- Connection pooling configured

✅ **Documentation:**
- Schema documentation complete
- Setup guides created
- Risk analysis completed

### 8.2 What's Missing (Critical for Integration)

⚠️ **Database Models:**
- `database/db_models.py` does not exist
- No SQLAlchemy models defined
- Cannot query database from Python

⚠️ **Data Migration:**
- No script to extract prompts from code
- Database tables are empty
- No way to populate content

⚠️ **Code Integration:**
- Week modules don't import database
- Still use hardcoded prompts
- Still use in-memory state
- No caching layer

⚠️ **Error Handling:**
- No fallback if database unavailable
- No retry logic
- No connection error handling

---

## 9. Current System Flow

### 9.1 Request Flow: User Submits Response

```
1. USER INPUT
   └─> User types or speaks response
   └─> Frontend captures input (text or voice via STT)

2. FRONTEND → API GATEWAY
   └─> POST /week{N}/api/process_response
   └─> Payload: { message: "...", question_number: N }

3. API GATEWAY → WEEK MODULE
   └─> Routes to appropriate week module
   └─> Extracts session_id from Flask session

4. WEEK MODULE PROCESSING
   └─> Gets state from in-memory: conversation_states[session_id]
   └─> Loads hardcoded QUESTIONS[question_number]
   └─> Loads hardcoded SYSTEM_PROMPTS[question_number]
   └─> Loads hardcoded content blocks (e.g., WEEK4_VIDEOS_EXERCISES)

5. PROMPT BUILDING
   └─> Gets classifier prompt from SYSTEM_PROMPTS
   └─> Replaces {name} with user name
   └─> Replaces {WEEK4_CONTENT} with content blocks
   └─> Replaces {Answer to question X} with previous answers

6. LLM CLASSIFICATION
   └─> Call OpenAI API with classifier prompt
   └─> Determine scenario (SCENARIO_1, SCENARIO_2, SCENARIO_3)

7. RESPONSE GENERATION
   └─> Get scenario-specific prompt from SYSTEM_PROMPTS
   └─> Build final prompt with content blocks
   └─> Call OpenAI API for NOVA response

8. STATE UPDATES (IN-MEMORY)
   └─> Update state.answers[question_number]
   └─> Update state.nova_responses[question_number]
   └─> Update state.iteration_count[question_number]
   └─> Update state.question_completed[question_number]
   └─> Update state.q{N}_scenario

9. PROGRESS TRACKING (JSON FILE)
   └─> Save to user_progress.json via progress_tracker
   └─> Update question completion status

10. RESPONSE TO USER
    └─> Return JSON: { success: true, response: "..." }
    └─> Frontend displays response
    └─> Frontend calls TTS API for audio playback
```

### 9.2 Database Integration Flow (Future)

When database is integrated, the flow will be:

```
4. WEEK MODULE PROCESSING
   └─> Query: Get state from conversation_states table
   └─> Query: Get question from questions table
   └─> Query: Get prompts from system_prompts table
   └─> Query: Get content blocks from week_content_blocks table

5. PROMPT BUILDING
   └─> Get classifier prompt from database
   └─> Query: Get previous answers from user_answers table
   └─> Replace variables with database data

8. STATE UPDATES (DATABASE)
   └─> INSERT: user_answers
   └─> INSERT: conversation_messages (user)
   └─> INSERT: conversation_messages (nova)
   └─> UPDATE: conversation_states
   └─> INSERT/UPDATE: question_completions
```

---

## 10. Database Schema Details

### 10.1 Core Tables

| Table | Purpose | Key Fields | Status |
|-------|---------|------------|--------|
| `weeks` | Week information | week_id, week_number, name, title, welcome_message | ✅ Created |
| `questions` | Questions per week | question_id, week_id, question_number, question_text | ✅ Created |
| `system_prompts` | All LLM prompts | prompt_id, question_id, prompt_type, prompt_text | ✅ Created |
| `week_content_blocks` | Reusable content | content_id, week_id, block_name, content_text | ✅ Created |
| `conversation_states` | Current state | state_id, session_id, week_id, conversation_data (JSONB) | ✅ Created |
| `user_answers` | User responses | answer_id, session_id, question_id, answer_text | ✅ Created |
| `question_completions` | Completion tracking | completion_id, session_id, question_id, scenario_classification | ✅ Created |
| `conversation_messages` | Full history | message_id, session_id, sender, message_text | ✅ Created |

### 10.2 Key Design Decisions

1. **No User Authentication**
   - Uses `session_id` from Flask session directly
   - No `users` table needed
   - Simpler for rapid testing

2. **JSONB for Flexible State**
   - `conversation_states.conversation_data` stores complex nested structure
   - Matches current code's dict structure
   - Easy to query and update

3. **Separate Tables for Answers**
   - `user_answers` table for prompt references
   - Supports multiple iterations
   - Easy to query: "What did user say to question 4?"

4. **Completion Tracking**
   - `question_completions` table for flow control
   - Tracks iterations and scenarios
   - Critical for knowing when to move to next question

5. **Full Message History**
   - `conversation_messages` stores everything
   - Both user and NOVA messages
   - Complete audit trail

---

## 11. Risks and Mitigation

### 11.1 Critical Risks

**Risk 1: Code Doesn't Use Database**
- **Current**: Code uses in-memory state, database is orphaned
- **Mitigation**: Create database models and service layer
- **Priority**: High

**Risk 2: Database Empty**
- **Current**: Tables exist but have no data
- **Mitigation**: Create migration script to populate from code
- **Priority**: High

**Risk 3: Performance Degradation**
- **Risk**: Database queries slower than in-memory
- **Mitigation**: Add caching layer for prompts/content
- **Priority**: Medium

**Risk 4: Database Connection Failures**
- **Risk**: System breaks if Supabase is down
- **Mitigation**: Add error handling and fallback to in-memory
- **Priority**: High

### 11.2 Data Structure Compatibility

**Current Code Structure:**
```python
state.answers = {1: ["a1", "a2"], 2: ["a3"]}  # Dict of lists
```

**Database Structure:**
```sql
-- Separate rows in user_answers table
-- Need to convert: rows → dict of lists
```

**Solution:**
- Use `conversation_states.conversation_data` (JSONB) for compatibility
- Or create helper functions to convert between formats
- Cache converted data in memory

---

## 12. Migration Path

### Phase 1: Database Setup (✅ Complete)
- [x] Create database schema
- [x] Configure Supabase connection
- [x] Verify connection works

### Phase 2: Data Migration (⚠️ Needed)
- [ ] Create `database/db_models.py` (SQLAlchemy models)
- [ ] Create migration script to extract prompts from code
- [ ] Populate database with existing prompts/questions
- [ ] Verify all data migrated correctly

### Phase 3: Code Integration (⚠️ Needed)
- [ ] Create service layer (content_service.py, prompt_service.py)
- [ ] Add caching layer for prompts
- [ ] Update one week module as test
- [ ] Add error handling and fallback
- [ ] Update all week modules
- [ ] Update progress_tracker to use database

### Phase 4: Testing & Deployment (⚠️ Needed)
- [ ] Test thoroughly with database
- [ ] Performance testing
- [ ] Error scenario testing
- [ ] Deploy and monitor

---

## 13. Current Limitations

### 13.1 State Persistence
- **Current**: In-memory state lost on server restart
- **Impact**: Users lose conversation progress if server restarts
- **Solution**: Database integration (schema ready)

### 13.2 Content Management
- **Current**: Prompts hardcoded in Python files
- **Impact**: Requires code deployment to update prompts
- **Solution**: Database storage (schema ready, needs migration)

### 13.3 Scalability
- **Current**: Single server instance, in-memory state
- **Impact**: Cannot scale horizontally
- **Solution**: Database-backed state (schema ready)

### 13.4 Progress Tracking
- **Current**: JSON file-based
- **Impact**: File locking issues, not scalable
- **Solution**: Database tables (schema ready)

---

## 14. Future Enhancements

### 14.1 Immediate (For Database Integration)
1. Create database models (`db_models.py`)
2. Create data migration scripts
3. Create service layer for database access
4. Add caching for performance
5. Add error handling and fallback

### 14.2 Short-term
1. Admin interface for prompt management
2. Analytics dashboard
3. A/B testing for prompts
4. Performance monitoring

### 14.3 Long-term
1. User authentication (if needed)
2. Multi-language support
3. Mobile app
4. Real-time collaboration features

---

## 15. Architecture Principles

1. **Separation of Concerns**: Clear boundaries between layers
2. **Modularity**: Week modules are independent
3. **Session-Based**: No authentication complexity
4. **Database-Ready**: Schema designed for future integration
5. **Backward Compatible**: Current system continues to work
6. **Gradual Migration**: Can integrate database incrementally

---

## 16. Summary

### Current State
- ✅ System fully functional with in-memory state
- ✅ Database schema designed and created
- ✅ Database connection verified
- ⚠️ Database not yet integrated into code
- ⚠️ Prompts still hardcoded in Python files

### Next Steps
1. Create database models (`database/db_models.py`)
2. Create migration script to populate database
3. Create service layer for database access
4. Integrate database into week modules (gradually)
5. Add caching and error handling

### Key Benefits of Database (When Integrated)
- ✅ Prompts editable without code deployment
- ✅ State persists across server restarts
- ✅ Complete conversation history
- ✅ Scalable architecture
- ✅ Easy client handoff

---

**Document Version**: 2.0  
**Last Updated**: December 2024  
**Status**: Current system functional, database ready for integration
