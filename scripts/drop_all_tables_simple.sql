-- Quick SQL to drop all tables - Copy and paste into Supabase SQL Editor
-- After running this, run: python3 scripts/create_all_tables.py --confirm

DROP TABLE IF EXISTS conversation_messages CASCADE;
DROP TABLE IF EXISTS user_answers CASCADE;
DROP TABLE IF EXISTS question_completions CASCADE;
DROP TABLE IF EXISTS conversation_states CASCADE;
DROP TABLE IF EXISTS system_prompts CASCADE;
DROP TABLE IF EXISTS validation_prompts CASCADE;
DROP TABLE IF EXISTS week_content_blocks CASCADE;
DROP TABLE IF EXISTS questions CASCADE;
DROP TABLE IF EXISTS weeks CASCADE;

DROP SEQUENCE IF EXISTS weeks_week_id_seq CASCADE;
DROP SEQUENCE IF EXISTS questions_question_id_seq CASCADE;
DROP SEQUENCE IF EXISTS system_prompts_prompt_id_seq CASCADE;
DROP SEQUENCE IF EXISTS week_content_blocks_content_id_seq CASCADE;
DROP SEQUENCE IF EXISTS conversation_states_state_id_seq CASCADE;
DROP SEQUENCE IF EXISTS user_answers_answer_id_seq CASCADE;
DROP SEQUENCE IF EXISTS question_completions_completion_id_seq CASCADE;
DROP SEQUENCE IF EXISTS conversation_messages_message_id_seq CASCADE;
DROP SEQUENCE IF EXISTS validation_prompts_validation_id_seq CASCADE;

DROP FUNCTION IF EXISTS update_updated_at_column() CASCADE;
DROP FUNCTION IF EXISTS get_week_id(INTEGER) CASCADE;
DROP FUNCTION IF EXISTS get_question_id(INTEGER, INTEGER) CASCADE;


