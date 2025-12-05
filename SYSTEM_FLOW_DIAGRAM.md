# System Flow with Database Integration

## Visual Data Flow

```
┌─────────────────────────────────────────────────────────────────────┐
│                         USER INTERACTION                            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ User types or speaks
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                          FRONTEND (index.html)                      │
│  • Captures voice/text input                                        │
│  • Sends to backend API                                             │
│  • Displays responses                                               │
│  • Handles TTS/STT                                                  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP Request
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    FLASK APP (app.py)                               │
│  • Routes requests to appropriate week module                       │
│  • Handles TTS/STT endpoints                                        │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Routes to /week4/api/process_response
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  WEEK MODULE (week4_main.py)                        │
│  • Processes user response                                          │
│  • Manages conversation flow                                        │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Needs: Question, Prompts, State
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SERVICE LAYER                                    │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ ContentService                                                │  │
│  │  • get_week_by_number() → Week from DB                       │  │
│  │  • get_questions_for_week() → Questions from DB              │  │
│  │  • get_content_blocks() → Content blocks from DB             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ PromptService                                                 │  │
│  │  • get_prompt_for_question() → Prompt from DB                │  │
│  │  • build_prompt() → Insert content blocks                    │  │
│  │  • Replace variables ({name}, {WEEK4_CONTENT}, etc.)         │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ ConversationService                                           │  │
│  │  • get_conversation_state() → State from DB                  │  │
│  │  • update_conversation_state() → Save to DB                  │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ ProgressService                                               │  │
│  │  • update_question_completion() → Save to DB                 │  │
│  │  • complete_week() → Mark week complete in DB                │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ SQL Queries
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    POSTGRESQL DATABASE                              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ CONTENT TABLES                                                │  │
│  │  • weeks                                                      │  │
│  │  • questions                                                  │  │
│  │  • system_prompts                                             │  │
│  │  • week_content_blocks                                        │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ USER TABLES                                                   │  │
│  │  • users                                                      │  │
│  │  • user_progress                                              │  │
│  │  • question_completions                                       │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                              │                                      │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │ CONVERSATION TABLES                                           │  │
│  │  • conversation_states                                        │  │
│  │  • conversation_messages                                      │  │
│  │  • user_answers                                               │  │
│  │  • nova_responses                                             │  │
│  └──────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Data returned
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  PROCESSING WITH LLM                                │
│  • Build prompt from database content                               │
│  • Call OpenAI API                                                  │
│  • Get NOVA response                                                │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Save everything
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    SAVE TO DATABASE                                 │
│  • Save user message → conversation_messages                        │
│  • Save NOVA response → conversation_messages                       │
│  • Update conversation state → conversation_states                  │
│  • Update progress → question_completions, user_progress            │
└─────────────────────────────────────────────────────────────────────┘
                              │
                              │ Return response
                              ▼
┌─────────────────────────────────────────────────────────────────────┐
│                    RESPONSE TO USER                                 │
│  • Display NOVA response                                            │
│  • Play audio (TTS)                                                 │
│  • Continue conversation                                            │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Example: User Answers Question 1 in Week 4

### Step-by-Step Flow:

```
1. USER ACTION
   User says: "I learned about asking for help"
   └─> Frontend captures audio
   └─> Converts to text (ElevenLabs STT)
   └─> Auto-submits message

2. FRONTEND → BACKEND
   POST /week4/api/process_response
   {
     "message": "I learned about asking for help",
     "question_number": 1
   }

3. WEEK MODULE RECEIVES REQUEST
   └─> Gets session_id from Flask session
   └─> Gets user_id from database (users table)

4. LOAD CONVERSATION STATE
   └─> Query: SELECT * FROM conversation_states 
           WHERE user_id = ? AND week_id = ?
   └─> Get current question, answers, iterations

5. LOAD QUESTION FROM DATABASE
   └─> Query: SELECT * FROM questions 
           WHERE week_id = ? AND question_number = 1
   └─> Question text: "What was one main idea you took away?"

6. LOAD PROMPTS FROM DATABASE
   └─> Query: SELECT * FROM system_prompts 
           WHERE question_id = ?
   └─> Get: classifier, scenario_1_respond, scenario_2_respond, scenario_3_respond

7. BUILD CLASSIFIER PROMPT
   └─> Get classifier prompt text
   └─> Insert content blocks from week_content_blocks table
   └─> Replace {name} with user's name
   └─> Final prompt ready

8. CALL OPENAI (CLASSIFIER)
   └─> Input: Classifier prompt + user message
   └─> Output: "SCENARIO_1"

9. LOAD SCENARIO RESPONSE PROMPT
   └─> Query: SELECT * FROM system_prompts 
           WHERE question_id = ? AND scenario_name = 'SCENARIO_1'
   └─> Get scenario_1_respond prompt

10. BUILD RESPONSE PROMPT
    └─> Get scenario_1_respond prompt text
    └─> Insert content blocks (WEEK4_VIDEOS_EXERCISES, etc.)
    └─> Replace {name} with user's name
    └─> Final prompt ready

11. CALL OPENAI (RESPONSE GENERATION)
    └─> Input: Scenario prompt + user message
    └─> Output: "Great! Asking for help is an important skill..."

12. SAVE USER MESSAGE TO DATABASE
    INSERT INTO conversation_messages (
        user_id, week_id, question_id, sender, message_text, message_type
    ) VALUES (?, ?, ?, 'user', 'I learned about asking for help', 'voice')

13. SAVE NOVA RESPONSE TO DATABASE
    INSERT INTO conversation_messages (
        user_id, week_id, question_id, sender, message_text, 
        prompt_used_id, scenario_classification
    ) VALUES (?, ?, ?, 'nova', 'Great! Asking for help...', ?, 'SCENARIO_1')

14. UPDATE CONVERSATION STATE
    UPDATE conversation_states SET
        conversation_data = JSONB_SET(conversation_data, 
            '{answers,1}', '["I learned about asking for help"]'),
        conversation_data = JSONB_SET(conversation_data,
            '{nova_responses,1}', '["Great! Asking for help..."]'),
        updated_at = NOW()
    WHERE user_id = ? AND week_id = ?

15. UPDATE PROGRESS (if question complete)
    INSERT INTO question_completions (
        user_id, question_id, scenario_classification
    ) VALUES (?, ?, 'SCENARIO_1')

16. RETURN RESPONSE TO FRONTEND
    {
        "success": true,
        "response": "Great! Asking for help is an important skill...",
        "move_to_next": false
    }

17. FRONTEND DISPLAYS
    └─> Shows NOVA response in chat
    └─> Plays audio via TTS (ElevenLabs)
    └─> User sees message labeled as "Voice" input
```

---

## Database Query Patterns

### Loading Content for a Week

```sql
-- Get week
SELECT * FROM weeks WHERE week_number = 4;

-- Get all questions for week
SELECT * FROM questions 
WHERE week_id = (SELECT week_id FROM weeks WHERE week_number = 4)
ORDER BY question_number;

-- Get all prompts for question 1
SELECT * FROM system_prompts
WHERE question_id = (
    SELECT question_id FROM questions 
    WHERE week_id = (SELECT week_id FROM weeks WHERE week_number = 4)
    AND question_number = 1
);

-- Get all content blocks for week
SELECT * FROM week_content_blocks
WHERE week_id = (SELECT week_id FROM weeks WHERE week_number = 4);
```

### Tracking User Progress

```sql
-- Get user's progress for all weeks
SELECT 
    w.week_number,
    w.name as week_name,
    up.is_completed,
    up.current_question_number,
    COUNT(qc.completion_id) as questions_completed
FROM weeks w
LEFT JOIN user_progress up ON w.week_id = up.week_id AND up.user_id = ?
LEFT JOIN question_completions qc ON qc.user_id = ? 
    AND qc.question_id IN (
        SELECT question_id FROM questions WHERE week_id = w.week_id
    )
GROUP BY w.week_id, w.week_number, w.name, up.is_completed, up.current_question_number
ORDER BY w.week_number;
```

### Retrieving Conversation History

```sql
-- Get full conversation for a user/week
SELECT 
    cm.created_at,
    cm.sender,
    cm.message_text,
    cm.message_type,
    q.question_number,
    cm.scenario_classification
FROM conversation_messages cm
LEFT JOIN questions q ON cm.question_id = q.question_id
WHERE cm.user_id = ? AND cm.week_id = ?
ORDER BY cm.created_at ASC;
```

---

## Key Advantages of This Architecture

### 1. **Separation of Concerns**
- Content (prompts) separate from code
- Business logic separate from data access
- Clear service layer boundaries

### 2. **Easy Content Updates**
```sql
-- Update a prompt without touching code
UPDATE system_prompts 
SET prompt_text = 'New improved prompt text...'
WHERE prompt_id = 123;
```

### 3. **Full Audit Trail**
- Every message stored
- Every prompt used tracked
- Complete conversation history
- Easy to debug issues

### 4. **Scalability**
- Multiple app servers can share database
- Load balancing possible
- Horizontal scaling

### 5. **Analytics Ready**
```sql
-- Which prompts work best?
SELECT 
    sp.prompt_type,
    COUNT(*) as usage_count,
    AVG(LENGTH(cm.message_text)) as avg_response_length
FROM conversation_messages cm
JOIN system_prompts sp ON cm.prompt_used_id = sp.prompt_id
WHERE cm.sender = 'nova'
GROUP BY sp.prompt_type;
```

---

## Migration Steps

1. **Setup Database**
   - Create PostgreSQL database
   - Run schema creation script
   - Set up connection

2. **Migrate Content**
   - Extract prompts from week files
   - Load into database
   - Verify all content

3. **Build Service Layer**
   - Create database models
   - Create service classes
   - Add caching if needed

4. **Update Week Modules**
   - Replace hardcoded data with database calls
   - Update to use services
   - Test thoroughly

5. **Deploy**
   - Migrate existing progress (if any)
   - Deploy new code
   - Monitor performance

---

This architecture makes the system production-ready, scalable, and maintainable!

