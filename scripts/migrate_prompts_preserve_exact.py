"""
Prompt Migration Script - EXACT PRESERVATION

This script extracts prompts from current code and migrates them to database
with ZERO modifications. Every character must be preserved exactly.

CRITICAL: Do not modify, reformat, or "improve" any prompts during migration.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path to import week modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_config import init_db, get_database_url
from flask import Flask
from sqlalchemy import text
import json

# Import week modules to access their prompts
# NOTE: We import but don't execute - just to access constants
import importlib.util

def extract_prompts_from_week_file(week_file_path, week_number):
    """
    Extract prompts from a week file by parsing the file directly.
    This avoids issues with Flask app initialization.
    
    Returns:
        dict with keys: 'questions', 'system_prompts', 'welcome_message', 
                       'final_response', 'content_blocks'
    """
    print(f"\n{'='*60}")
    print(f"Extracting prompts from Week {week_number}")
    print(f"File: {week_file_path}")
    print(f"{'='*60}")
    
    extracted = {
        'questions': {},
        'system_prompts': {},
        'welcome_message': None,
        'final_response': None,
        'content_blocks': {}
    }
    
    # Read file and parse Python code
    try:
        with open(week_file_path, 'r', encoding='utf-8') as f:
            code = f.read()
        
        # Use ast to safely parse and extract constants
        import ast
        
        # Parse the file
        tree = ast.parse(code)
        
        # Find assignments to QUESTIONS, SYSTEM_PROMPTS, etc.
        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        var_name = target.id
                        
                        # Extract QUESTIONS dict
                        if var_name == 'QUESTIONS' and isinstance(node.value, ast.Dict):
                            for key, value in zip(node.value.keys, node.value.values):
                                if isinstance(key, ast.Constant) and isinstance(value, ast.Constant):
                                    extracted['questions'][key.value] = value.value
                        
                        # Extract SYSTEM_PROMPTS dict (complex nested structure)
                        elif var_name == 'SYSTEM_PROMPTS' and isinstance(node.value, ast.Dict):
                            # This is complex - we'll need to handle nested dicts
                            # For now, let's use eval in a safe way for this specific case
                            pass  # Will handle below with safer method
                        
                        # Extract WELCOME_MESSAGE
                        elif var_name == 'WELCOME_MESSAGE' and isinstance(node.value, ast.Constant):
                            extracted['welcome_message'] = node.value.value
                        
                        # Extract FINAL_RESPONSE
                        elif var_name == 'FINAL_RESPONSE' and isinstance(node.value, ast.Constant):
                            extracted['final_response'] = node.value.value
                        
                        # Extract content blocks (WEEK*_VIDEOS_EXERCISES, etc.)
                        elif var_name.startswith('WEEK') or var_name.startswith('HOMEWORK') or \
                             var_name.startswith('THINKING_FLEXIBLY') or var_name.startswith('GOAL') or \
                             var_name.startswith('CLARIFYING') or var_name.startswith('NEW_WEEK'):
                            if isinstance(node.value, ast.Constant):
                                extracted['content_blocks'][var_name] = node.value.value
        
        # For SYSTEM_PROMPTS, use a safer extraction method
        # Find the SYSTEM_PROMPTS = {...} block and extract it
        import re
        system_prompts_match = re.search(r'SYSTEM_PROMPTS\s*=\s*\{', code)
        if system_prompts_match:
            # Extract the dict by finding matching braces
            start_pos = system_prompts_match.end() - 1
            brace_count = 0
            in_string = False
            string_char = None
            end_pos = start_pos
            
            for i, char in enumerate(code[start_pos:], start_pos):
                if not in_string:
                    if char in ('"', "'"):
                        in_string = True
                        string_char = char
                    elif char == '{':
                        brace_count += 1
                    elif char == '}':
                        brace_count -= 1
                        if brace_count == 0:
                            end_pos = i + 1
                            break
                else:
                    if char == string_char and code[i-1] != '\\':
                        in_string = False
            
            # Extract and safely evaluate the dict
            system_prompts_code = code[system_prompts_match.start():end_pos]
            # Create a safe namespace for eval
            safe_dict = {}
            try:
                # Execute in isolated namespace
                exec(system_prompts_code, {'__builtins__': {}}, safe_dict)
                if 'SYSTEM_PROMPTS' in safe_dict:
                    extracted['system_prompts'] = safe_dict['SYSTEM_PROMPTS']
            except Exception as e:
                print(f"  ⚠️  Could not extract SYSTEM_PROMPTS via parsing: {e}")
                print(f"     Will try module import method...")
                
                # Fallback: try importing the module
                try:
                    spec = importlib.util.spec_from_file_location(f"week{week_number}_module", week_file_path)
                    module = importlib.util.module_from_spec(spec)
                    # Suppress Flask app creation
                    import sys
                    old_argv = sys.argv
                    sys.argv = ['']  # Fake command line
                    spec.loader.exec_module(module)
                    sys.argv = old_argv
                    
                    if hasattr(module, 'SYSTEM_PROMPTS'):
                        extracted['system_prompts'] = getattr(module, 'SYSTEM_PROMPTS')
                except Exception as import_error:
                    print(f"  ❌ Module import also failed: {import_error}")
        
    except Exception as e:
        print(f"ERROR extracting from file: {e}")
        import traceback
        traceback.print_exc()
        return None
    
    extracted = {
        'questions': {},
        'system_prompts': {},
        'welcome_message': None,
        'final_response': None,
        'content_blocks': {}
    }
    
    # Extract QUESTIONS dict
    if hasattr(module, 'QUESTIONS'):
        questions = getattr(module, 'QUESTIONS')
        if isinstance(questions, dict):
            extracted['questions'] = questions.copy()
            print(f"  ✓ Extracted {len(questions)} questions")
        else:
            print(f"  ⚠ QUESTIONS is not a dict: {type(questions)}")
    
    # Extract SYSTEM_PROMPTS dict
    if hasattr(module, 'SYSTEM_PROMPTS'):
        system_prompts = getattr(module, 'SYSTEM_PROMPTS')
        if isinstance(system_prompts, dict):
            extracted['system_prompts'] = system_prompts.copy()
            print(f"  ✓ Extracted system prompts for {len(system_prompts)} questions")
        else:
            print(f"  ⚠ SYSTEM_PROMPTS is not a dict: {type(system_prompts)}")
    
    # Extract WELCOME_MESSAGE
    if hasattr(module, 'WELCOME_MESSAGE'):
        extracted['welcome_message'] = getattr(module, 'WELCOME_MESSAGE')
        print(f"  ✓ Extracted welcome message ({len(extracted['welcome_message'])} chars)")
    
    # Extract FINAL_RESPONSE
    if hasattr(module, 'FINAL_RESPONSE'):
        extracted['final_response'] = getattr(module, 'FINAL_RESPONSE')
        print(f"  ✓ Extracted final response ({len(extracted['final_response'])} chars)")
    
    # Extract content blocks (WEEK*_VIDEOS_EXERCISES, WEEK*_EXERCISE*, etc.)
    content_block_prefixes = [
        f'WEEK{week_number}_VIDEOS_EXERCISES',
        f'WEEK{week_number}_EXERCISE',
        'HOMEWORK_QUESTIONS',
        'THINKING_FLEXIBLY',
        'GOAL_CATEGORIES',
        'CLARIFYING_QUESTIONS',
        'NEW_WEEK1_SECTION_INTRO'
    ]
    
    for attr_name in dir(module):
        # Check if it's a content block constant
        for prefix in content_block_prefixes:
            if attr_name.startswith(prefix):
                value = getattr(module, attr_name)
                if isinstance(value, str):
                    extracted['content_blocks'][attr_name] = value
                    print(f"  ✓ Extracted content block: {attr_name} ({len(value)} chars)")
    
    return extracted


def verify_exact_match(original_text, database_text):
    """
    Verify that database text matches original exactly.
    Returns (is_match, differences)
    """
    if original_text == database_text:
        return True, None
    
    # Find differences
    differences = []
    min_len = min(len(original_text), len(database_text))
    
    for i in range(min_len):
        if original_text[i] != database_text[i]:
            start = max(0, i - 20)
            end = min(len(original_text), i + 20)
            differences.append({
                'position': i,
                'original': original_text[start:end],
                'database': database_text[start:end] if i < len(database_text) else ''
            })
            if len(differences) >= 5:  # Limit to first 5 differences
                break
    
    return False, differences


def insert_week_data(conn, week_number, extracted_data):
    """
    Insert week data into database with exact preservation.
    """
    print(f"\n{'='*60}")
    print(f"Inserting Week {week_number} data into database")
    print(f"{'='*60}")
    
    # 1. Insert or get week
    week_result = conn.execute(
        text("""
            INSERT INTO weeks (week_number, name, title, description, welcome_message, is_active)
            VALUES (:week_number, :name, :title, :description, :welcome_message, TRUE)
            ON CONFLICT (week_number) 
            DO UPDATE SET 
                welcome_message = EXCLUDED.welcome_message,
                updated_at = CURRENT_TIMESTAMP
            RETURNING week_id
        """),
        {
            'week_number': week_number,
            'name': f'Week {week_number}',
            'title': f'Week {week_number} Title',  # TODO: Get from actual data
            'description': None,  # TODO: Get from actual data
            'welcome_message': extracted_data.get('welcome_message')
        }
    )
    week_id = week_result.fetchone()[0]
    print(f"  ✓ Week {week_number} (week_id: {week_id})")
    
    # 2. Insert questions
    for qnum, question_text in extracted_data['questions'].items():
        conn.execute(
            text("""
                INSERT INTO questions (week_id, question_number, question_text)
                VALUES (:week_id, :question_number, :question_text)
                ON CONFLICT (week_id, question_number)
                DO UPDATE SET question_text = EXCLUDED.question_text
            """),
            {
                'week_id': week_id,
                'question_number': qnum,
                'question_text': question_text  # EXACT text, no modifications
            }
        )
        print(f"  ✓ Question {qnum}")
    
    # 3. Insert system prompts
    for qnum, prompts in extracted_data['system_prompts'].items():
        # Get question_id
        question_result = conn.execute(
            text("SELECT question_id FROM questions WHERE week_id = :week_id AND question_number = :qnum"),
            {'week_id': week_id, 'qnum': qnum}
        )
        question_row = question_result.fetchone()
        if not question_row:
            print(f"  ⚠ Question {qnum} not found, skipping prompts")
            continue
        
        question_id = question_row[0]
        
        # Handle different prompt structures
        if isinstance(prompts, dict):
            # Modern structure: {"classifier": "...", "scenario_1_respond": "..."}
            for prompt_type, prompt_text in prompts.items():
                if prompt_type.startswith('scenario_'):
                    # Extract scenario name (e.g., "scenario_1_respond" -> "SCENARIO_1")
                    scenario_name = prompt_type.replace('scenario_', '').replace('_respond', '').replace('_ask', '').replace('_prompt', '').replace('_congratulate', '').replace('_assist', '').replace('_reinforce', '').replace('_followup', '').upper()
                    if not scenario_name.startswith('SCENARIO'):
                        scenario_name = f'SCENARIO_{scenario_name}'
                else:
                    scenario_name = None
                
                conn.execute(
                    text("""
                        INSERT INTO system_prompts (question_id, prompt_type, prompt_text, scenario_name)
                        VALUES (:question_id, :prompt_type, :prompt_text, :scenario_name)
                        ON CONFLICT DO NOTHING
                    """),
                    {
                        'question_id': question_id,
                        'prompt_type': prompt_type,
                        'prompt_text': prompt_text,  # EXACT text
                        'scenario_name': scenario_name
                    }
                )
                print(f"  ✓ Prompt for Q{qnum}: {prompt_type}")
        elif isinstance(prompts, str):
            # Old structure: single string prompt
            conn.execute(
                text("""
                    INSERT INTO system_prompts (question_id, prompt_type, prompt_text)
                    VALUES (:question_id, 'default', :prompt_text)
                    ON CONFLICT DO NOTHING
                """),
                {
                    'question_id': question_id,
                    'prompt_text': prompts  # EXACT text
                }
            )
            print(f"  ✓ Single prompt for Q{qnum}")
    
    # 4. Insert content blocks
    for block_name, block_content in extracted_data['content_blocks'].items():
        conn.execute(
            text("""
                INSERT INTO week_content_blocks (week_id, block_name, content_text)
                VALUES (:week_id, :block_name, :content_text)
                ON CONFLICT (week_id, block_name)
                DO UPDATE SET content_text = EXCLUDED.content_text
            """),
            {
                'week_id': week_id,
                'block_name': block_name,
                'content_text': block_content  # EXACT text
            }
        )
        print(f"  ✓ Content block: {block_name}")
    
    conn.commit()
    print(f"\n✓ Week {week_number} data inserted successfully")


def main():
    """
    Main migration function.
    """
    print("="*60)
    print("PROMPT MIGRATION - EXACT PRESERVATION")
    print("="*60)
    print("\n⚠️  CRITICAL: This script preserves prompts EXACTLY as-is")
    print("   No modifications, no reformatting, no improvements")
    print("="*60)
    
    # Initialize Flask app and database
    app = Flask(__name__)
    db = init_db(app)
    
    # Week files to process
    week_files = {
        1: 'temporary_main.py',
        2: 'temporary_week2_main.py',
        3: 'temporary_main_q16_22.py',
        4: 'week4_main.py',
        5: 'week5_main.py'
    }
    
    with app.app_context():
        with db.engine.connect() as conn:
            for week_num, filename in week_files.items():
                filepath = Path(__file__).parent.parent / filename
                
                if not filepath.exists():
                    print(f"\n⚠️  File not found: {filepath}")
                    continue
                
                # Extract prompts
                extracted = extract_prompts_from_week_file(str(filepath), week_num)
                
                if not extracted:
                    print(f"  ⚠️  Failed to extract data for Week {week_num}")
                    continue
                
                # Insert into database
                insert_week_data(conn, week_num, extracted)
                
                # TODO: Add verification step to compare database vs original
    
    print("\n" + "="*60)
    print("MIGRATION COMPLETE")
    print("="*60)
    print("\n⚠️  NEXT STEPS:")
    print("1. Verify all prompts in database match originals exactly")
    print("2. Test variable substitution")
    print("3. Test flow logic")
    print("4. Compare outputs side-by-side")


if __name__ == '__main__':
    main()

