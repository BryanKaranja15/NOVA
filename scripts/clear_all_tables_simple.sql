-- Quick SQL to clear all tables and reset sequences
-- Copy and paste this into Supabase SQL Editor

TRUNCATE TABLE conversation_messages CASCADE;
TRUNCATE TABLE user_answers CASCADE;
TRUNCATE TABLE question_completions CASCADE;
TRUNCATE TABLE conversation_states CASCADE;
TRUNCATE TABLE system_prompts CASCADE;
TRUNCATE TABLE validation_prompts CASCADE;
TRUNCATE TABLE week_content_blocks CASCADE;
TRUNCATE TABLE questions CASCADE;
TRUNCATE TABLE weeks CASCADE;

ALTER SEQUENCE weeks_week_id_seq RESTART WITH 1;
ALTER SEQUENCE questions_question_id_seq RESTART WITH 1;
ALTER SEQUENCE system_prompts_prompt_id_seq RESTART WITH 1;
ALTER SEQUENCE week_content_blocks_content_id_seq RESTART WITH 1;
ALTER SEQUENCE conversation_states_state_id_seq RESTART WITH 1;
ALTER SEQUENCE user_answers_answer_id_seq RESTART WITH 1;
ALTER SEQUENCE question_completions_completion_id_seq RESTART WITH 1;
ALTER SEQUENCE conversation_messages_message_id_seq RESTART WITH 1;
ALTER SEQUENCE validation_prompts_validation_id_seq RESTART WITH 1;


