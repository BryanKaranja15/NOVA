-- =====================================================
-- Clear All Tables - Preserves Schema, Removes All Data
-- =====================================================
-- This script truncates all tables and resets sequences
-- Use this before reloading data to ensure clean state
-- =====================================================

-- Disable foreign key checks temporarily (PostgreSQL doesn't need this, but included for clarity)
-- PostgreSQL handles CASCADE automatically

-- Clear all tables in dependency order (children first, then parents)
-- Using CASCADE to handle foreign key constraints

TRUNCATE TABLE conversation_messages CASCADE;
TRUNCATE TABLE user_answers CASCADE;
TRUNCATE TABLE question_completions CASCADE;
TRUNCATE TABLE conversation_states CASCADE;
TRUNCATE TABLE system_prompts CASCADE;
TRUNCATE TABLE validation_prompts CASCADE;
TRUNCATE TABLE week_content_blocks CASCADE;
TRUNCATE TABLE questions CASCADE;
TRUNCATE TABLE weeks CASCADE;

-- Reset all sequences to start from 1
ALTER SEQUENCE weeks_week_id_seq RESTART WITH 1;
ALTER SEQUENCE questions_question_id_seq RESTART WITH 1;
ALTER SEQUENCE system_prompts_prompt_id_seq RESTART WITH 1;
ALTER SEQUENCE week_content_blocks_content_id_seq RESTART WITH 1;
ALTER SEQUENCE conversation_states_state_id_seq RESTART WITH 1;
ALTER SEQUENCE user_answers_answer_id_seq RESTART WITH 1;
ALTER SEQUENCE question_completions_completion_id_seq RESTART WITH 1;
ALTER SEQUENCE conversation_messages_message_id_seq RESTART WITH 1;
ALTER SEQUENCE validation_prompts_validation_id_seq RESTART WITH 1;

-- Verify tables are empty
SELECT 
    'weeks' as table_name, COUNT(*) as row_count FROM weeks
UNION ALL
SELECT 'questions', COUNT(*) FROM questions
UNION ALL
SELECT 'system_prompts', COUNT(*) FROM system_prompts
UNION ALL
SELECT 'week_content_blocks', COUNT(*) FROM week_content_blocks
UNION ALL
SELECT 'conversation_states', COUNT(*) FROM conversation_states
UNION ALL
SELECT 'user_answers', COUNT(*) FROM user_answers
UNION ALL
SELECT 'question_completions', COUNT(*) FROM question_completions
UNION ALL
SELECT 'conversation_messages', COUNT(*) FROM conversation_messages
UNION ALL
SELECT 'validation_prompts', COUNT(*) FROM validation_prompts;


