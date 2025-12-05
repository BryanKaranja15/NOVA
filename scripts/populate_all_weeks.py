"""
Populate all weeks (1-5) in order so week_id matches week_number
"""

import sys
import re
from pathlib import Path
from flask import Flask
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_config import init_db

# Import week modules
import temporary_main as week1
import temporary_week2_main as week2
import temporary_main_q16_22 as week3
import week4_main as week4
import week5_main as week5

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

def populate_week(week_number, week_module, week_name, week_title, week_file_path=None):
    """Populate a week's data from its module."""
    print(f"\n{'='*60}")
    print(f"POPULATING WEEK {week_number}: {week_name}")
    print(f"{'='*60}")
    
    with app.app_context():
        with db.engine.connect() as conn:
            # For Week 4, try to extract from file if module has empty dicts
            if week_number == 4:
                questions = getattr(week_module, 'QUESTIONS', {})
                system_prompts = getattr(week_module, 'SYSTEM_PROMPTS', {})
                
                # If empty, try to extract from file
                if not questions or not system_prompts:
                    if week_file_path and Path(week_file_path).exists():
                        print(f"  ⚠️  Week 4 module has empty data, extracting from file...")
                        with open(week_file_path, 'r', encoding='utf-8') as f:
                            code = f.read()
                        questions = extract_dict_from_code(code, 'QUESTIONS')
                        system_prompts = extract_dict_from_code(code, 'SYSTEM_PROMPTS')
                        if questions or system_prompts:
                            print(f"  ✓ Extracted from file: {len(questions)} questions, {len(system_prompts)} prompt sets")
                    else:
                        print(f"  ⚠️  Week 4 data not available - skipping (may need manual population)")
                        return
                else:
                    questions = getattr(week_module, 'QUESTIONS', {})
                    system_prompts = getattr(week_module, 'SYSTEM_PROMPTS', {})
            else:
                # For other weeks, use direct attribute access
                questions = getattr(week_module, 'QUESTIONS', {})
                system_prompts = getattr(week_module, 'SYSTEM_PROMPTS', {})
            
            welcome_message = getattr(week_module, 'WELCOME_MESSAGE', '')
            final_response = getattr(week_module, 'FINAL_RESPONSE', '')
            
            # Get content blocks (WEEK*_VIDEOS_EXERCISES, etc.)
            content_blocks = {}
            for attr_name in dir(week_module):
                if attr_name.startswith(f'WEEK{week_number}_') or \
                   attr_name.startswith('HOMEWORK_') or \
                   attr_name.startswith('THINKING_FLEXIBLY') or \
                   attr_name.startswith('GOAL_') or \
                   attr_name.startswith('CLARIFYING_') or \
                   attr_name.startswith('NEW_WEEK') or \
                   attr_name.startswith('CORNER_PIECE'):
                    value = getattr(week_module, attr_name)
                    if isinstance(value, str):
                        content_blocks[attr_name] = value
            
            print(f"  ✓ Extracted {len(questions)} questions")
            print(f"  ✓ Extracted system prompts for {len(system_prompts)} questions")
            print(f"  ✓ Extracted {len(content_blocks)} content blocks")
            
            # Insert week
            week_result = conn.execute(
                text("""
                    INSERT INTO weeks (week_number, name, title, welcome_message, is_active)
                    VALUES (:week_num, :name, :title, :welcome, TRUE)
                    ON CONFLICT (week_number) 
                    DO UPDATE SET 
                        welcome_message = EXCLUDED.welcome_message,
                        name = EXCLUDED.name,
                        title = EXCLUDED.title
                    RETURNING week_id
                """),
                {
                    'week_num': week_number,
                    'name': week_name,
                    'title': week_title,
                    'welcome': welcome_message
                }
            )
            week_id = week_result.fetchone()[0]
            print(f"  ✓ Week {week_number} (week_id: {week_id})")
            
            # Verify week_id matches week_number
            if week_id != week_number:
                print(f"  ⚠️  WARNING: week_id={week_id} does not match week_number={week_number}")
            else:
                print(f"  ✅ week_id={week_id} correctly matches week_number={week_number}")
            
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
    
    print(f"  ✅ Week {week_number} populated successfully!")


def main():
    """Main function to populate all weeks in order."""
    print("="*60)
    print("POPULATE ALL WEEKS (1-5) IN ORDER")
    print("="*60)
    print("\n⚠️  This will ensure week_id matches week_number")
    print("   Week 1 → week_id=1, Week 2 → week_id=2, etc.\n")
    
    # Clear all existing week data first
    with app.app_context():
        with db.engine.connect() as conn:
            print("Clearing all existing week data...")
            conn.execute(text("DELETE FROM conversation_messages"))
            conn.execute(text("DELETE FROM user_answers"))
            conn.execute(text("DELETE FROM question_completions"))
            conn.execute(text("DELETE FROM conversation_states"))
            conn.execute(text("DELETE FROM system_prompts"))
            conn.execute(text("DELETE FROM validation_prompts"))
            conn.execute(text("DELETE FROM week_content_blocks"))
            conn.execute(text("DELETE FROM questions"))
            conn.execute(text("DELETE FROM weeks"))
            conn.commit()
            print("✅ All existing data cleared\n")
    
    # Reset sequence to start at 1
    with app.app_context():
        with db.engine.connect() as conn:
            print("Resetting sequence to start at 1...")
            conn.execute(text("ALTER SEQUENCE weeks_week_id_seq RESTART WITH 1"))
            conn.commit()
            print("✅ Sequence reset\n")
    
    # Populate weeks in order
    weeks = [
        (1, week1, "Week 1", "Thinking Flexibly and Goal Setting", None),
        (2, week2, "Week 2", "Building Resilience", None),
        (3, week3, "Week 3", "Career Exploration", None),
        (4, week4, "Week 4", "Asking for Help", Path(__file__).parent.parent / "week4_main.py"),
        (5, week5, "Week 5", "Networking and Interviewing", None),
    ]
    
    for week_num, week_module, week_name, week_title, week_file in weeks:
        try:
            populate_week(week_num, week_module, week_name, week_title, week_file)
        except Exception as e:
            print(f"\n❌ Error populating Week {week_num}: {e}")
            import traceback
            traceback.print_exc()
            continue
    
    print("\n" + "="*60)
    print("✅ ALL WEEKS POPULATED")
    print("="*60)
    
    # Verify week_id matches week_number
    with app.app_context():
        with db.engine.connect() as conn:
            print("\nVerifying week_id matches week_number:")
            result = conn.execute(text("SELECT week_id, week_number, name FROM weeks ORDER BY week_number"))
            all_match = True
            for row in result:
                if row[0] == row[1]:
                    print(f"  ✅ Week {row[1]}: week_id={row[0]} ✓")
                else:
                    print(f"  ❌ Week {row[1]}: week_id={row[0]} (MISMATCH!)")
                    all_match = False
            
            if all_match:
                print("\n✅ All week_ids correctly match week_numbers!")
            else:
                print("\n⚠️  Some week_ids do not match week_numbers")


if __name__ == '__main__':
    main()

