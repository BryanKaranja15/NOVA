-- =====================================================
-- Clear All Data from Supabase Database
-- =====================================================
-- This script clears all data from all tables
-- Tables are kept, only data is deleted
-- =====================================================

-- =====================================================
-- OPTION 1: TRUNCATE CASCADE (FASTEST - RECOMMENDED)
-- =====================================================
-- This is the fastest way to clear all data
-- CASCADE automatically handles foreign key dependencies
-- =====================================================

TRUNCATE TABLE 
    validation_logs,
    nova_responses,
    user_answers,
    conversation_messages,
    conversation_states,
    question_completions,
    user_progress,
    prompt_variables,
    system_prompts,
    questions,
    week_content_blocks,
    weeks,
    users,
    system_settings
CASCADE;

-- Reset sequences (auto-increment counters)
ALTER SEQUENCE IF EXISTS weeks_week_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS questions_question_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS system_prompts_prompt_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS prompt_variables_variable_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS week_content_blocks_content_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS user_progress_progress_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS question_completions_completion_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS conversation_states_state_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS conversation_messages_message_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS user_answers_answer_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS nova_responses_response_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS validation_logs_validation_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS system_settings_setting_id_seq RESTART WITH 1;

-- =====================================================
-- OPTION 2: DELETE (Slower but more explicit)
-- =====================================================
-- Uncomment below if you prefer DELETE over TRUNCATE
-- Delete in order to respect foreign key constraints
-- =====================================================

/*
-- Delete from child tables first (order matters due to foreign keys)
DELETE FROM validation_logs;
DELETE FROM nova_responses;
DELETE FROM user_answers;
DELETE FROM conversation_messages;
DELETE FROM conversation_states;
DELETE FROM question_completions;
DELETE FROM user_progress;
DELETE FROM prompt_variables;
DELETE FROM system_prompts;
DELETE FROM questions;
DELETE FROM week_content_blocks;
DELETE FROM weeks;
DELETE FROM users;
DELETE FROM system_settings;

-- Reset sequences
ALTER SEQUENCE IF EXISTS weeks_week_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS questions_question_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS system_prompts_prompt_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS prompt_variables_variable_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS week_content_blocks_content_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS user_progress_progress_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS question_completions_completion_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS conversation_states_state_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS conversation_messages_message_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS user_answers_answer_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS nova_responses_response_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS validation_logs_validation_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS system_settings_setting_id_seq RESTART WITH 1;
*/

-- =====================================================
-- OPTION 3: Clear Only User Data (Keep Content)
-- =====================================================
-- Uncomment to clear only user data, keeping weeks/questions/prompts
-- =====================================================

/*
TRUNCATE TABLE 
    validation_logs,
    nova_responses,
    user_answers,
    conversation_messages,
    conversation_states,
    question_completions,
    user_progress,
    users
CASCADE;

-- Reset user-related sequences
ALTER SEQUENCE IF EXISTS user_progress_progress_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS question_completions_completion_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS conversation_states_state_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS conversation_messages_message_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS user_answers_answer_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS nova_responses_response_id_seq RESTART WITH 1;
ALTER SEQUENCE IF EXISTS validation_logs_validation_id_seq RESTART WITH 1;
*/

-- =====================================================
-- Verification Query
-- =====================================================
-- Run this after clearing to verify all tables are empty

SELECT 
    'users' as table_name, COUNT(*) as row_count FROM users
UNION ALL
SELECT 'weeks', COUNT(*) FROM weeks
UNION ALL
SELECT 'questions', COUNT(*) FROM questions
UNION ALL
SELECT 'system_prompts', COUNT(*) FROM system_prompts
UNION ALL
SELECT 'week_content_blocks', COUNT(*) FROM week_content_blocks
UNION ALL
SELECT 'user_progress', COUNT(*) FROM user_progress
UNION ALL
SELECT 'question_completions', COUNT(*) FROM question_completions
UNION ALL
SELECT 'conversation_states', COUNT(*) FROM conversation_states
UNION ALL
SELECT 'conversation_messages', COUNT(*) FROM conversation_messages
UNION ALL
SELECT 'user_answers', COUNT(*) FROM user_answers
UNION ALL
SELECT 'nova_responses', COUNT(*) FROM nova_responses
UNION ALL
SELECT 'validation_logs', COUNT(*) FROM validation_logs
UNION ALL
SELECT 'system_settings', COUNT(*) FROM system_settings
ORDER BY table_name;


