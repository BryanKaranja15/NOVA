"""
Populate Week 4 data from the current week4_main.py file
This extracts the hardcoded data before it's removed and populates the database
"""

import sys
import re
from pathlib import Path
from flask import Flask
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_config import init_db

app = Flask(__name__)
db = init_db(app)

def extract_dict_from_code(code: str, var_name: str) -> dict:
    """Extract a Python dict from code string."""
    pattern = rf'{var_name}\s*=\s*\{{'
    match = re.search(pattern, code)
    if not match:
        return {}
    
    start_pos = match.end() - 1
    brace_count = 0
    in_string = False
    string_char = None
    end_pos = start_pos
    
    for i, char in enumerate(code[start_pos:], start_pos):
        if not in_string:
            if char in ('"', "'"):
                if i + 2 < len(code) and code[i:i+3] in ('"""', "'''"):
                    in_string = True
                    string_char = code[i:i+3]
                    i += 2
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
    
    dict_code = code[match.start():end_pos]
    safe_dict = {}
    try:
        exec(dict_code, {'__builtins__': {}}, safe_dict)
        return safe_dict.get(var_name, {})
    except Exception as e:
        print(f"  ⚠️  Error extracting {var_name}: {e}")
        return {}

def extract_string_constant(code: str, var_name: str) -> str:
    """Extract a string constant from code."""
    # Try triple quotes first
    pattern1 = rf'{var_name}\s*=\s*"""(.*?)"""'
    match1 = re.search(pattern1, code, re.DOTALL)
    if match1:
        return match1.group(1)
    # Try single triple quotes
    pattern2 = rf"{var_name}\s*=\s*'''(.*?)'''"
    match2 = re.search(pattern2, code, re.DOTALL)
    if match2:
        return match2.group(1)
    # Try double quotes
    pattern3 = rf'{var_name}\s*=\s*"(.*?)"'
    match3 = re.search(pattern3, code, re.DOTALL)
    if match3:
        return match3.group(1)
    # Try single quotes
    pattern4 = rf"{var_name}\s*=\s*'(.*?)'"
    match4 = re.search(pattern4, code, re.DOTALL)
    if match4:
        return match4.group(1)
    return ""

def main():
    """Populate Week 4 data from week4_main.py file."""
    print("="*60)
    print("POPULATING WEEK 4 FROM week4_main.py")
    print("="*60)
    
    filepath = Path(__file__).parent.parent / "week4_main.py"
    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()
    
    # Extract constants - try to get from the original hardcoded values
    # Since the file might have been modified, we'll read it as-is
    # and extract what we can find
    
    # First, try to find the hardcoded values before they were removed
    # Look for QUESTIONS = { ... }
    questions = extract_dict_from_code(code, 'QUESTIONS')
    system_prompts = extract_dict_from_code(code, 'SYSTEM_PROMPTS')
    welcome_message = extract_string_constant(code, 'WELCOME_MESSAGE')
    final_response = extract_string_constant(code, 'FINAL_RESPONSE')
    week4_videos = extract_string_constant(code, 'WEEK4_VIDEOS_EXERCISES')
    week4_ex1 = extract_string_constant(code, 'WEEK4_EXERCISE1')
    week4_ex2 = extract_string_constant(code, 'WEEK4_EXERCISE2')
    
    # If extraction failed, try importing the module directly
    if not questions or not system_prompts:
        print("  ⚠️  Could not extract from file, trying direct import...")
        try:
            import week4_main
            # Temporarily disable database loading
            if hasattr(week4_main, '_ensure_data_loaded'):
                # Try to get original values before database loading
                questions = getattr(week4_main, 'QUESTIONS', {})
                system_prompts = getattr(week4_main, 'SYSTEM_PROMPTS', {})
                welcome_message = getattr(week4_main, 'WELCOME_MESSAGE', '')
                final_response = getattr(week4_main, 'FINAL_RESPONSE', '')
                week4_videos = getattr(week4_main, 'WEEK4_VIDEOS_EXERCISES', '')
                week4_ex1 = getattr(week4_main, 'WEEK4_EXERCISE1', '')
                week4_ex2 = getattr(week4_main, 'WEEK4_EXERCISE2', '')
        except Exception as e:
            print(f"  ❌ Error importing module: {e}")
            return
    
    print(f"  ✓ Extracted {len(questions)} questions")
    print(f"  ✓ Extracted system prompts for {len(system_prompts)} questions")
    print(f"  ✓ Extracted welcome message ({len(welcome_message)} chars)")
    print(f"  ✓ Extracted final response ({len(final_response)} chars)")
    print(f"  ✓ Extracted content blocks")
    
    if not questions:
        print("  ❌ No questions found! Week 4 data may have already been removed from file.")
        print("     You may need to restore the original week4_main.py or populate manually.")
        return
    
    with app.app_context():
        with db.engine.connect() as conn:
            # Insert week
            week_result = conn.execute(
                text("""
                    INSERT INTO weeks (week_number, name, title, welcome_message, is_active)
                    VALUES (4, 'Week 4', 'Asking for Help', :welcome, TRUE)
                    ON CONFLICT (week_number) 
                    DO UPDATE SET 
                        welcome_message = EXCLUDED.welcome_message,
                        name = EXCLUDED.name,
                        title = EXCLUDED.title
                    RETURNING week_id
                """),
                {'welcome': welcome_message}
            )
            week_id = week_result.fetchone()[0]
            print(f"  ✓ Week 4 (week_id: {week_id})")
            
            # Verify week_id matches week_number
            if week_id != 4:
                print(f"  ⚠️  WARNING: week_id={week_id} does not match week_number=4")
            else:
                print(f"  ✅ week_id={week_id} correctly matches week_number=4")
            
            # Delete existing questions for Week 4 to avoid conflicts
            conn.execute(
                text("DELETE FROM questions WHERE week_id = :week_id"),
                {'week_id': week_id}
            )
            
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
            
            # Delete existing system prompts for Week 4
            conn.execute(
                text("""
                    DELETE FROM system_prompts 
                    WHERE question_id IN (SELECT question_id FROM questions WHERE week_id = :week_id)
                """),
                {'week_id': week_id}
            )
            
            # Insert system prompts
            prompt_count = 0
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
                
                # Handle different prompt structures
                if isinstance(prompts, dict):
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
                        prompt_count += 1
                elif isinstance(prompts, str):
                    # Single string prompt (old format)
                    conn.execute(
                        text("""
                            INSERT INTO system_prompts (question_id, prompt_type, prompt_text)
                            VALUES (:qid, 'default', :ptext)
                            ON CONFLICT DO NOTHING
                        """),
                        {'qid': question_id, 'ptext': prompts}
                    )
                    prompt_count += 1
            
            print(f"  ✓ Inserted {prompt_count} system prompts")
            
            # Insert content blocks
            content_blocks = {
                'WEEK4_VIDEOS_EXERCISES': week4_videos,
                'WEEK4_EXERCISE1': week4_ex1,
                'WEEK4_EXERCISE2': week4_ex2,
            }
            
            if final_response:
                content_blocks['FINAL_RESPONSE'] = final_response
            
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
    
    print("\n✅ Week 4 populated successfully!")

if __name__ == '__main__':
    main()


