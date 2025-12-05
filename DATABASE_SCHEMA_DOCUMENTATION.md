# DRIVEN Program Database Schema Documentation

## Overview

This database schema is designed to store all prompts, questions, user progress, and conversation data for the NOVA Career Coach system. It replaces the current hardcoded prompts and JSON-based progress tracking with a robust, scalable database solution.

## Core Tables

### 1. **users** - User Management
Stores user accounts and session information.
- `user_id` (UUID): Primary key
- `session_id` (VARCHAR): Flask session ID (unique)
- `name`: User's name
- `email`: Optional email address
- `created_at`, `last_active`: Timestamps
- `metadata` (JSONB): Additional user data

**Use Cases:**
- Link all user activity to a session
- Track user progression across weeks
- Store user preferences/settings

---

### 2. **weeks** - Program Structure
Stores information about each week in the DRIVEN program.
- `week_id`: Primary key
- `week_number`: Week number (1-6)
- `name`: Week name (e.g., "Week 1")
- `title`: Week title (e.g., "Thinking Flexibly and Goal Setting")
- `description`: Week description
- `video_content`: Video/exercise summaries
- `exercise_content`: Exercise descriptions
- `is_active`: Whether week is currently active

**Use Cases:**
- Define program structure
- Store week-level content
- Enable/disable weeks dynamically

---

### 3. **questions** - Question Storage
Stores all questions for each week.
- `question_id`: Primary key
- `week_id`: Foreign key to weeks
- `question_number`: Order within week
- `question_text`: The actual question text
- `question_type`: Type of question (open_ended, yes_no, multiple_choice)
- `requires_followup`: Whether question needs follow-up
- `validation_prompt`: Custom validation logic

**Use Cases:**
- Store all questions centrally
- Easy to update questions without code changes
- Support different question types

---

### 4. **system_prompts** - LLM Prompts
Stores all system prompts for the LLM, including classifiers and scenario responses.
- `prompt_id`: Primary key
- `question_id`: Foreign key to questions
- `prompt_type`: Type of prompt (classifier, scenario_1_respond, scenario_2_respond, etc.)
- `prompt_text`: The actual prompt text
- `scenario_name`: Scenario identifier (SCENARIO_1, SCENARIO_2, etc.)
- `conditions` (JSONB): Conditional logic

**Use Cases:**
- Store all prompts in database
- Easy to update prompts without deployment
- Support complex scenario-based prompts
- A/B testing different prompt versions

**Example Prompt Types:**
- `classifier`: Determines which scenario applies
- `scenario_1_respond`: Response for scenario 1
- `scenario_2_respond`: Response for scenario 2
- `validation`: Validation prompts
- `followup`: Follow-up question prompts

---

### 5. **week_content_blocks** - Reusable Content
Stores reusable content blocks that can be inserted into prompts.
- `content_id`: Primary key
- `week_id`: Foreign key to weeks
- `block_name`: Identifier (e.g., "WEEK4_VIDEOS_EXERCISES")
- `content_text`: The content text
- `content_type`: Type of content

**Use Cases:**
- Store video summaries, exercise descriptions
- Insert into prompts dynamically
- Update content without changing prompts
- Reuse content across multiple prompts

**Example Blocks:**
- `WEEK4_VIDEOS_EXERCISES`: Video content summary
- `WEEK4_EXERCISE1`: Exercise 1 description
- `WEEK4_EXERCISE2`: Exercise 2 description

---

### 6. **user_progress** - Week Progress
Tracks user progress through each week.
- `progress_id`: Primary key
- `user_id`: Foreign key to users
- `week_id`: Foreign key to weeks
- `started_at`: When user started the week
- `completed_at`: When user completed the week
- `is_completed`: Completion status
- `current_question_number`: Current question
- `metadata` (JSONB): Week-specific data (selected_problem, corner_piece, etc.)

**Use Cases:**
- Track which weeks users have completed
- Determine which week user should access
- Store week-specific user choices

---

### 7. **question_completions** - Question Tracking
Tracks which questions users have completed.
- `completion_id`: Primary key
- `user_id`: Foreign key to users
- `question_id`: Foreign key to questions
- `completed_at`: When question was completed
- `iteration_count`: Number of iterations (for multi-iteration questions)
- `scenario_classification`: Which scenario was matched
- `metadata` (JSONB): Additional data

**Use Cases:**
- Track question completion status
- Support multi-iteration questions
- Store scenario classifications

---

### 8. **conversation_states** - State Management
Stores current conversation state for each user/week.
- `state_id`: Primary key
- `user_id`: Foreign key to users
- `week_id`: Foreign key to weeks
- `current_question_number`: Current question
- `conversation_data` (JSONB): All state data
  - answers: {qnum: [list of responses]}
  - nova_responses: {qnum: [list of responses]}
  - iteration_count: {qnum: count}
  - question_completed: {qnum: bool}
  - scenario classifications: {qnum: scenario}

**Use Cases:**
- Persist conversation state between requests
- Support resuming conversations
- Store complex state data

---

### 9. **conversation_messages** - Full History
Stores complete conversation history.
- `message_id`: Primary key
- `user_id`: Foreign key to users
- `week_id`: Foreign key to weeks
- `question_id`: Foreign key to questions
- `sender`: 'user' or 'nova'
- `message_text`: Message content
- `message_type`: 'text' or 'voice'
- `prompt_used_id`: Which prompt was used
- `scenario_classification`: Scenario used
- `iteration_number`: Iteration number
- `created_at`: Timestamp

**Use Cases:**
- Full conversation logging
- Analytics and insights
- Debugging conversation flow
- Generating transcripts

---

### 10. **user_answers** - Answer Storage
Stores all user answers to questions.
- `answer_id`: Primary key
- `user_id`: Foreign key to users
- `question_id`: Foreign key to questions
- `answer_text`: The answer
- `iteration_number`: Iteration number
- `is_complete`: Whether answer is complete
- `created_at`: Timestamp

**Use Cases:**
- Store all user responses
- Support multiple iterations
- Track answer completeness

---

### 11. **nova_responses** - Response Storage
Stores all NOVA responses.
- `response_id`: Primary key
- `user_id`: Foreign key to users
- `question_id`: Foreign key to questions
- `response_text`: The response
- `prompt_used_id`: Which prompt was used
- `scenario_classification`: Scenario used
- `iteration_number`: Iteration number

**Use Cases:**
- Store all NOVA responses
- Link responses to prompts used
- Track scenario classifications

---

### 12. **validation_logs** - Validation Tracking
Logs validation results for debugging.
- `validation_id`: Primary key
- `user_id`: Foreign key to users
- `question_id`: Foreign key to questions
- `validation_result`: 'complete' or 'incomplete'
- `missing_items`: What was missing
- `user_responses`: Summary of responses checked
- `created_at`: Timestamp

**Use Cases:**
- Debug validation issues
- Improve validation prompts
- Track validation patterns

---

### 13. **system_settings** - Configuration
Stores system-wide settings.
- `setting_id`: Primary key
- `setting_key`: Setting name (unique)
- `setting_value`: Setting value
- `setting_type`: Type (string, integer, boolean, json)
- `description`: Setting description

**Use Cases:**
- Store system configuration
- Feature flags
- API keys (encrypted)
- Model settings

---

## Key Relationships

```
users
  ├── user_progress (one-to-many)
  ├── conversation_states (one-to-many)
  ├── conversation_messages (one-to-many)
  ├── question_completions (one-to-many)
  ├── user_answers (one-to-many)
  └── nova_responses (one-to-many)

weeks
  ├── questions (one-to-many)
  ├── week_content_blocks (one-to-many)
  ├── user_progress (one-to-many)
  └── conversation_states (one-to-many)

questions
  ├── system_prompts (one-to-many)
  ├── question_completions (one-to-many)
  ├── user_answers (one-to-many)
  ├── nova_responses (one-to-many)
  └── conversation_messages (one-to-many)
```

## Migration Strategy

### Phase 1: Database Setup
1. Create database and schema
2. Migrate existing prompts from code to database
3. Create data migration scripts

### Phase 2: Content Migration
1. Extract all prompts from week files
2. Extract all questions
3. Extract all content blocks
4. Insert into database

### Phase 3: Code Updates
1. Create database access layer (models/ORM)
2. Update week files to read from database
3. Update progress tracker to use database
4. Test thoroughly

### Phase 4: Deployment
1. Deploy database
2. Migrate existing user progress (if any)
3. Deploy updated code
4. Monitor and fix issues

## Benefits

1. **Centralized Management**: All prompts in one place
2. **Easy Updates**: Change prompts without code deployment
3. **Version Control**: Track prompt changes over time
4. **A/B Testing**: Test different prompt versions
5. **Analytics**: Analyze which prompts work best
6. **Scalability**: Support multiple users efficiently
7. **Data Integrity**: Relational data ensures consistency
8. **Full History**: Complete conversation logging
9. **Debugging**: Easy to trace issues
10. **Flexibility**: Easy to add new weeks/questions

## Recommended Database

**PostgreSQL** is recommended because:
- Excellent JSONB support for flexible metadata
- Robust relational features
- Great performance
- Excellent tooling and ecosystem
- Full-text search capabilities
- Time-series extensions if needed

## Next Steps

1. Review and refine schema
2. Set up PostgreSQL database
3. Create migration scripts
4. Build database access layer (SQLAlchemy recommended)
5. Migrate existing data
6. Update application code
7. Test thoroughly
8. Deploy

