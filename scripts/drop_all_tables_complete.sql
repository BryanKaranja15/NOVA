-- =====================================================
-- Drop All Tables, Views, Functions, and Triggers
-- =====================================================
-- This script completely removes all database objects
-- Run this, then run create_all_tables.py to recreate everything
-- =====================================================

-- Drop tables in dependency order (children first, then parents)
-- CASCADE ensures dependent objects are also dropped

DROP TABLE IF EXISTS conversation_messages CASCADE;
DROP TABLE IF EXISTS user_answers CASCADE;
DROP TABLE IF EXISTS question_completions CASCADE;
DROP TABLE IF EXISTS conversation_states CASCADE;
DROP TABLE IF EXISTS system_prompts CASCADE;
DROP TABLE IF EXISTS validation_prompts CASCADE;
DROP TABLE IF EXISTS week_content_blocks CASCADE;
DROP TABLE IF EXISTS questions CASCADE;
DROP TABLE IF EXISTS weeks CASCADE;

-- Drop sequences (they may be auto-dropped with tables, but explicit is safer)
DROP SEQUENCE IF EXISTS weeks_week_id_seq CASCADE;
DROP SEQUENCE IF EXISTS questions_question_id_seq CASCADE;
DROP SEQUENCE IF EXISTS system_prompts_prompt_id_seq CASCADE;
DROP SEQUENCE IF EXISTS week_content_blocks_content_id_seq CASCADE;
DROP SEQUENCE IF EXISTS conversation_states_state_id_seq CASCADE;
DROP SEQUENCE IF EXISTS user_answers_answer_id_seq CASCADE;
DROP SEQUENCE IF EXISTS question_completions_completion_id_seq CASCADE;
DROP SEQUENCE IF EXISTS conversation_messages_message_id_seq CASCADE;
DROP SEQUENCE IF EXISTS validation_prompts_validation_id_seq CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS get_week_id(INTEGER) CASCADE;
DROP FUNCTION IF EXISTS get_question_id(INTEGER, INTEGER) CASCADE;

-- Drop triggers (they should be auto-dropped with tables, but explicit is safer)
-- Note: Triggers are automatically dropped when tables are dropped

-- Verify everything is dropped
SELECT 
    'Tables remaining' as check_type,
    COUNT(*) as count
FROM information_schema.tables 
WHERE table_schema = 'public' 
  AND table_type = 'BASE TABLE';


