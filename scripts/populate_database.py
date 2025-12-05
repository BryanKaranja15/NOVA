"""
Populate Database with Prompts and Questions from Week Files

This script extracts prompts/questions from current code files and inserts them
into the database with EXACT preservation of all text.
"""

import sys
import os
from pathlib import Path
from flask import Flask
from sqlalchemy import text
import re

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_config import init_db, get_database_url


def extract_dict_from_code(code: str, var_name: str) -> dict:
    """
    Extract a Python dict from code string by finding the assignment
    and safely evaluating it.
    """
    # Find the dict assignment
    pattern = rf'{var_name}\s*=\s*\{{'
    match = re.search(pattern, code)
    if not match:
        return {}
    
    # Find matching braces
    start_pos = match.end() - 1
    brace_count = 0
    in_string = False
    string_char = None
    end_pos = start_pos
    
    for i, char in enumerate(code[start_pos:], start_pos):
        if not in_string:
            if char in ('"', "'"):
                # Check if it's a triple quote
                if i + 2 < len(code) and code[i:i+3] in ('"""', "'''"):
                    in_string = True
                    string_char = code[i:i+3]
                    i += 2  # Skip next 2 chars
                    continue
                elif char in ('"', "'"):
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
            if char == string_char:
                if string_char in ('"""', "'''"):
                    if i + 2 < len(code) and code[i:i+3] == string_char:
                        in_string = False
                        i += 2
                elif code[i-1] != '\\':
                    in_string = False
    
    # Extract the dict code
    dict_code = code[match.start():end_pos]
    
    # Create safe namespace for eval
    safe_dict = {}
    try:
        # Execute in isolated namespace with minimal builtins
        exec(dict_code, {'__builtins__': {}}, safe_dict)
        return safe_dict.get(var_name, {})
    except Exception as e:
        print(f"  ⚠️  Error extracting {var_name}: {e}")
        return {}


def extract_string_constant(code: str, var_name: str) -> str:
    """Extract a string constant from code."""
    pattern = rf'{var_name}\s*=\s*("""|'''|"|')(.*?)(?<!\\)\1'
    match = re.search(pattern, code, re.DOTALL)
    if match:
        return match.group(2)
    return None


def populate_week4(app: Flask):
    """Populate Week 4 data."""
    print("\n" + "="*60)
    print("POPULATING WEEK 4")
    print("="*60)
    
    filepath = Path(__file__).parent.parent / "week4_main.py"
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Extract constants
    questions = extract_dict_from_code(code, 'QUESTIONS')
    system_prompts = extract_dict_from_code(code, 'SYSTEM_PROMPTS')
    welcome_message = extract_string_constant(code, 'WELCOME_MESSAGE')
    final_response = extract_string_constant(code, 'FINAL_RESPONSE')
    week4_videos = extract_string_constant(code, 'WEEK4_VIDEOS_EXERCISES')
    week4_ex1 = extract_string_constant(code, 'WEEK4_EXERCISE1')
    week4_ex2 = extract_string_constant(code, 'WEEK4_EXERCISE2')
    
    print(f"  ✓ Extracted {len(questions)} questions")
    print(f"  ✓ Extracted system prompts for {len(system_prompts)} questions")
    print(f"  ✓ Extracted welcome message")
    print(f"  ✓ Extracted final response")
    print(f"  ✓ Extracted content blocks")
    
    with app.app_context():
        with app.extensions['sqlalchemy'].engine.connect() as conn:
            # Insert week
            week_result = conn.execute(
                text("""
                    INSERT INTO weeks (week_number, name, title, welcome_message, is_active)
                    VALUES (4, 'Week 4', 'Asking for Help', :welcome, TRUE)
                    ON CONFLICT (week_number) 
                    DO UPDATE SET welcome_message = EXCLUDED.welcome_message
                    RETURNING week_id
                """),
                {'welcome': welcome_message}
            )
            week_id = week_result.fetchone()[0]
            print(f"  ✓ Week 4 (week_id: {week_id})")
            
            # Insert questions
            for qnum, qtext in questions.items():
                conn.execute(
                    text("""
                        INSERT INTO questions (week_id, question_number, question_text)
                        VALUES (:week_id, :qnum, :qtext)
                        ON CONFLICT (week_id, question_number)
                        DO UPDATE SET question_text = EXCLUDED.question_text
                    """),
                    {'week_id': week_id, 'qnum': qnum, 'qtext': qtext}
                )
            print(f"  ✓ Inserted {len(questions)} questions")
            
            # Insert system prompts
            for qnum, prompts in system_prompts.items():
                # Get question_id
                q_result = conn.execute(
                    text("SELECT question_id FROM questions WHERE week_id = :week_id AND question_number = :qnum"),
                    {'week_id': week_id, 'qnum': qnum}
                )
                q_row = q_result.fetchone()
                if not q_row:
                    print(f"  ⚠️  Question {qnum} not found, skipping prompts")
                    continue
                
                question_id = q_row[0]
                
                # Insert each prompt type
                for prompt_type, prompt_text in prompts.items():
                    # Determine scenario_name
                    scenario_name = None
                    if prompt_type.startswith('scenario_'):
                        scenario_num = prompt_type.replace('scenario_', '').split('_')[0]
                        scenario_name = f'SCENARIO_{scenario_num}'
                    
                    conn.execute(
                        text("""
                            INSERT INTO system_prompts (question_id, prompt_type, prompt_text, scenario_name)
                            VALUES (:qid, :ptype, :ptext, :scenario)
                            ON CONFLICT DO NOTHING
                        """),
                        {
                            'qid': question_id,
                            'ptype': prompt_type,
                            'ptext': prompt_text,
                            'scenario': scenario_name
                        }
                    )
            print(f"  ✓ Inserted system prompts")
            
            # Insert content blocks
            content_blocks = {
                'WEEK4_VIDEOS_EXERCISES': week4_videos,
                'WEEK4_EXERCISE1': week4_ex1,
                'WEEK4_EXERCISE2': week4_ex2,
                'FINAL_RESPONSE': final_response
            }
            
            for block_name, block_content in content_blocks.items():
                if block_content:
                    conn.execute(
                        text("""
                            INSERT INTO week_content_blocks (week_id, block_name, content_text)
                            VALUES (:week_id, :name, :content)
                            ON CONFLICT (week_id, block_name)
                            DO UPDATE SET content_text = EXCLUDED.content_text
                        """),
                        {'week_id': week_id, 'name': block_name, 'content': block_content}
                    )
            print(f"  ✓ Inserted {len([c for c in content_blocks.values() if c])} content blocks")
            
            conn.commit()
    
    print("  ✅ Week 4 populated successfully!")


def main():
    """Main function."""
    print("="*60)
    print("POPULATE DATABASE WITH WEEK DATA")
    print("="*60)
    
    app = Flask(__name__)
    db = init_db(app)
    
    # Populate each week
    populate_week4(app)
    
    # TODO: Add populate_week1, populate_week2, populate_week3, populate_week5
    
    print("\n" + "="*60)
    print("✅ DATABASE POPULATION COMPLETE")
    print("="*60)


if __name__ == '__main__':
    main()


