-- =====================================================
-- Final Database Schema - Addresses All Risks
-- =====================================================
-- This schema:
-- 1. Uses session_id (no user authentication)
-- 2. Supports all current prompt types
-- 3. Matches current code data structures
-- 4. Includes welcome messages and intro/outro prompts
-- 5. Optimized for current system functionality
-- =====================================================

-- =====================================================
-- 1. PROGRAM STRUCTURE (Content)
-- =====================================================

CREATE TABLE weeks (
    week_id SERIAL PRIMARY KEY,
    week_number INTEGER UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    video_content TEXT,
    exercise_content TEXT,
    welcome_message TEXT, -- Welcome message for the week (e.g., "Nova here! Congrats on wrapping up Week 4...")
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_weeks_number ON weeks(week_number);
CREATE INDEX idx_weeks_active ON weeks(is_active);

-- =====================================================
-- 2. QUESTIONS (Content)
-- =====================================================

CREATE TABLE questions (
    question_id SERIAL PRIMARY KEY,
    week_id INTEGER NOT NULL REFERENCES weeks(week_id) ON DELETE CASCADE,
    question_number INTEGER NOT NULL,
    question_text TEXT NOT NULL,
    question_type VARCHAR(50) DEFAULT 'open_ended',
    requires_followup BOOLEAN DEFAULT FALSE,
    max_iterations INTEGER DEFAULT 2, -- Maximum iterations for this question
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(week_id, question_number)
);

CREATE INDEX idx_questions_week ON questions(week_id);
CREATE INDEX idx_questions_number ON questions(week_id, question_number);

-- =====================================================
-- 3. SYSTEM PROMPTS (Content - THE MAIN GOAL)
-- =====================================================
-- Supports ALL prompt types used in current code:
-- - classifier: Determines scenario (SCENARIO_1, SCENARIO_2, SCENARIO_3)
-- - validation: Validates completeness (optional, can be in questions.validation_prompt)
-- - scenario_1_respond: Response for SCENARIO_1
-- - scenario_2_respond: Response for SCENARIO_2
-- - scenario_3_respond: Response for SCENARIO_3
-- - intro: Canned response before question (optional)
-- - outro: Canned response after question (optional)

CREATE TABLE system_prompts (
    prompt_id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    prompt_type VARCHAR(50) NOT NULL, -- classifier, validation, scenario_1_respond, scenario_2_respond, scenario_3_respond, intro, outro
    prompt_text TEXT NOT NULL,
    scenario_name VARCHAR(100), -- SCENARIO_1, SCENARIO_2, SCENARIO_3 (for scenario response prompts)
    sort_order INTEGER DEFAULT 0,
    metadata JSONB, -- Additional metadata (e.g., conditions, variables used)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_prompts_question ON system_prompts(question_id);
CREATE INDEX idx_prompts_type ON system_prompts(prompt_type);
CREATE INDEX idx_prompts_scenario ON system_prompts(scenario_name);
CREATE INDEX idx_prompts_question_type ON system_prompts(question_id, prompt_type);

-- =====================================================
-- 4. WEEK CONTENT BLOCKS (Content - for dynamic insertion)
-- =====================================================
-- Stores reusable content that gets inserted into prompts
-- e.g., WEEK4_VIDEOS_EXERCISES, WEEK4_EXERCISE1, WEEK4_EXERCISE2

CREATE TABLE week_content_blocks (
    content_id SERIAL PRIMARY KEY,
    week_id INTEGER NOT NULL REFERENCES weeks(week_id) ON DELETE CASCADE,
    block_name VARCHAR(255) NOT NULL, -- e.g., "WEEK4_VIDEOS_EXERCISES", "WEEK4_EXERCISE1"
    content_text TEXT NOT NULL,
    content_type VARCHAR(50) DEFAULT 'text', -- text, video_summary, exercise_description
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(week_id, block_name)
);

CREATE INDEX idx_content_week ON week_content_blocks(week_id);
CREATE INDEX idx_content_name ON week_content_blocks(block_name);

-- =====================================================
-- 5. CONVERSATION STATES (State Management)
-- =====================================================
-- Stores current conversation state per session/week
-- conversation_data JSONB structure matches current code:
-- {
--   "answers": {1: ["answer1", "answer2"], 2: ["answer3"]},
--   "nova_responses": {1: ["response1"], 2: ["response2"]},
--   "iteration_count": {1: 2, 2: 1},
--   "question_completed": {1: true, 2: false},
--   "scenarios": {1: "SCENARIO_1", 2: "SCENARIO_2"},
--   "name": "User Name"
-- }

CREATE TABLE conversation_states (
    state_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL, -- Flask session ID
    week_id INTEGER NOT NULL REFERENCES weeks(week_id) ON DELETE CASCADE,
    current_question_number INTEGER,
    conversation_data JSONB NOT NULL DEFAULT '{}', -- Matches current code structure
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(session_id, week_id)
);

CREATE INDEX idx_states_session ON conversation_states(session_id);
CREATE INDEX idx_states_week ON conversation_states(week_id);
CREATE INDEX idx_states_session_week ON conversation_states(session_id, week_id);
CREATE INDEX idx_states_data ON conversation_states USING GIN (conversation_data); -- For JSONB queries

-- =====================================================
-- 6. USER ANSWERS (Response Storage - CRITICAL)
-- =====================================================
-- Stores user answers so prompts can reference them
-- e.g., "{Answer to question 4}" in prompts
-- Supports multiple iterations per question

CREATE TABLE user_answers (
    answer_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL, -- Flask session ID
    week_id INTEGER NOT NULL REFERENCES weeks(week_id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    answer_text TEXT NOT NULL,
    iteration_number INTEGER DEFAULT 1, -- Which iteration this answer is for (1, 2, etc.)
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_answers_session ON user_answers(session_id);
CREATE INDEX idx_answers_question ON user_answers(question_id);
CREATE INDEX idx_answers_session_question ON user_answers(session_id, question_id, iteration_number);
CREATE INDEX idx_answers_session_week ON user_answers(session_id, week_id);

-- =====================================================
-- 7. QUESTION COMPLETIONS (Completion Tracking - CRITICAL)
-- =====================================================
-- Tracks completion status, iterations, scenarios
-- Used to know when to move to next question
-- Critical for flow control

CREATE TABLE question_completions (
    completion_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL, -- Flask session ID
    week_id INTEGER NOT NULL REFERENCES weeks(week_id) ON DELETE CASCADE,
    question_id INTEGER NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    completed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    iteration_count INTEGER DEFAULT 1, -- Total iterations for this question
    scenario_classification VARCHAR(100), -- SCENARIO_1, SCENARIO_2, SCENARIO_3
    is_complete BOOLEAN DEFAULT TRUE,
    metadata JSONB -- Additional data (e.g., validation results, missing items)
);

CREATE INDEX idx_completions_session ON question_completions(session_id);
CREATE INDEX idx_completions_question ON question_completions(question_id);
CREATE INDEX idx_completions_session_question ON question_completions(session_id, question_id);
CREATE INDEX idx_completions_session_week ON question_completions(session_id, week_id);

-- =====================================================
-- 8. CONVERSATION MESSAGES (Full History)
-- =====================================================
-- Stores all messages for full conversation history
-- Both user and NOVA messages

CREATE TABLE conversation_messages (
    message_id SERIAL PRIMARY KEY,
    session_id VARCHAR(255) NOT NULL, -- Flask session ID
    week_id INTEGER NOT NULL REFERENCES weeks(week_id) ON DELETE CASCADE,
    question_id INTEGER REFERENCES questions(question_id) ON DELETE SET NULL,
    sender VARCHAR(50) NOT NULL, -- 'user' or 'nova'
    message_text TEXT NOT NULL,
    message_type VARCHAR(50) DEFAULT 'text', -- text, voice
    prompt_used_id INTEGER REFERENCES system_prompts(prompt_id) ON DELETE SET NULL,
    scenario_classification VARCHAR(100), -- Which scenario was used
    iteration_number INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_messages_session ON conversation_messages(session_id);
CREATE INDEX idx_messages_week ON conversation_messages(week_id);
CREATE INDEX idx_messages_question ON conversation_messages(question_id);
CREATE INDEX idx_messages_session_week ON conversation_messages(session_id, week_id, created_at);
CREATE INDEX idx_messages_sender ON conversation_messages(sender);

-- =====================================================
-- 9. VALIDATION PROMPTS (Optional - Can be in questions table)
-- =====================================================
-- Some weeks use separate validation prompts
-- Can store here or in questions.validation_prompt field

-- Note: Validation prompts can be stored in system_prompts with prompt_type='validation'
-- OR in questions.validation_prompt field
-- This table is optional but provides more flexibility

CREATE TABLE IF NOT EXISTS validation_prompts (
    validation_id SERIAL PRIMARY KEY,
    question_id INTEGER NOT NULL REFERENCES questions(question_id) ON DELETE CASCADE,
    prompt_text TEXT NOT NULL,
    validation_type VARCHAR(50) DEFAULT 'completeness', -- completeness, quality, etc.
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_validation_question ON validation_prompts(question_id);

-- =====================================================
-- TRIGGERS FOR AUTOMATIC UPDATES
-- =====================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_weeks_updated_at BEFORE UPDATE ON weeks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_questions_updated_at BEFORE UPDATE ON questions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_system_prompts_updated_at BEFORE UPDATE ON system_prompts
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_week_content_blocks_updated_at BEFORE UPDATE ON week_content_blocks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversation_states_updated_at BEFORE UPDATE ON conversation_states
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- =====================================================
-- HELPER FUNCTIONS
-- =====================================================

-- Function to get week_id from week_number (for code compatibility)
CREATE OR REPLACE FUNCTION get_week_id(p_week_number INTEGER)
RETURNS INTEGER AS $$
DECLARE
    v_week_id INTEGER;
BEGIN
    SELECT week_id INTO v_week_id 
    FROM weeks 
    WHERE week_number = p_week_number;
    RETURN v_week_id;
END;
$$ LANGUAGE plpgsql;

-- Function to get question_id from week_number and question_number
CREATE OR REPLACE FUNCTION get_question_id(p_week_number INTEGER, p_question_number INTEGER)
RETURNS INTEGER AS $$
DECLARE
    v_question_id INTEGER;
BEGIN
    SELECT q.question_id INTO v_question_id
    FROM questions q
    JOIN weeks w ON q.week_id = w.week_id
    WHERE w.week_number = p_week_number 
      AND q.question_number = p_question_number;
    RETURN v_question_id;
END;
$$ LANGUAGE plpgsql;

-- =====================================================
-- COMMENTS
-- =====================================================

COMMENT ON TABLE weeks IS 'Program weeks with their content and welcome messages';
COMMENT ON TABLE questions IS 'Questions for each week';
COMMENT ON TABLE system_prompts IS 'ALL LLM prompts: classifiers, validations, scenario responses (SCENARIO_1, SCENARIO_2, SCENARIO_3), intro/outro';
COMMENT ON TABLE week_content_blocks IS 'Reusable content blocks for prompt insertion (e.g., WEEK4_VIDEOS_EXERCISES)';
COMMENT ON TABLE conversation_states IS 'Current conversation state per session/week (JSONB matches code structure)';
COMMENT ON TABLE user_answers IS 'User answers to questions (referenced in prompts via {Answer to question X})';
COMMENT ON TABLE question_completions IS 'Question completion tracking (iterations, scenarios, completion status) - CRITICAL for flow control';
COMMENT ON TABLE conversation_messages IS 'Full conversation history (user and NOVA messages)';


