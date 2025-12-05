-- =====================================================
-- DROP ALL TABLES from Supabase Database
-- =====================================================
-- WARNING: This will DELETE ALL TABLES and ALL DATA
-- Use this if you want to completely start fresh
-- =====================================================

-- Drop all tables (CASCADE handles dependencies automatically)
DROP TABLE IF EXISTS validation_logs CASCADE;
DROP TABLE IF EXISTS nova_responses CASCADE;
DROP TABLE IF EXISTS user_answers CASCADE;
DROP TABLE IF EXISTS conversation_messages CASCADE;
DROP TABLE IF EXISTS conversation_states CASCADE;
DROP TABLE IF EXISTS question_completions CASCADE;
DROP TABLE IF EXISTS user_progress CASCADE;
DROP TABLE IF EXISTS prompt_variables CASCADE;
DROP TABLE IF EXISTS system_prompts CASCADE;
DROP TABLE IF EXISTS questions CASCADE;
DROP TABLE IF EXISTS week_content_blocks CASCADE;
DROP TABLE IF EXISTS weeks CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS system_settings CASCADE;

-- Drop views
DROP VIEW IF EXISTS user_progress_summary CASCADE;
DROP VIEW IF EXISTS conversation_flow CASCADE;

-- Drop functions
DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS get_or_create_user(VARCHAR, VARCHAR) CASCADE;

-- Note: Sequences are automatically dropped when tables are dropped
-- Triggers are automatically dropped when tables are dropped


