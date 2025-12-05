"""
Manually populate Week 4 data - Direct extraction from week4_main.py

This is a test script to populate Week 4 first, then we'll automate for other weeks.
"""

import sys
from pathlib import Path
from flask import Flask
from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).parent.parent))

from database.db_config import init_db

# Import week4 module to get constants
# We'll suppress Flask app.run() by mocking it
import week4_main

app = Flask(__name__)
db = init_db(app)

def populate_week4():
    """Populate Week 4 data from week4_main module."""
    print("="*60)
    print("POPULATING WEEK 4")
    print("="*60)
    
    with app.app_context():
        with db.engine.connect() as conn:
            # Insert week
            week_result = conn.execute(
                text("""
                    INSERT INTO weeks (week_number, name, title, welcome_message, is_active)
                    VALUES (4, 'Week 4', 'Asking for Help', :welcome, TRUE)
                    ON CONFLICT (week_number) 
                    DO UPDATE SET welcome_message = EXCLUDED.welcome_message
                    RETURNING week_id
                """),
                {'welcome': week4_main.WELCOME_MESSAGE}
            )
            week_id = week_result.fetchone()[0]
            print(f"✓ Week 4 (week_id: {week_id})")
            
            # Insert questions
            for qnum, qtext in week4_main.QUESTIONS.items():
                conn.execute(
                    text("""
                        INSERT INTO questions (week_id, question_number, question_text)
                        VALUES (:week_id, :qnum, :qtext)
                        ON CONFLICT (week_id, question_number)
                        DO UPDATE SET question_text = EXCLUDED.question_text
                    """),
                    {'week_id': week_id, 'qnum': qnum, 'qtext': qtext}
                )
            print(f"✓ Inserted {len(week4_main.QUESTIONS)} questions")
            
            # Insert system prompts
            prompt_count = 0
            for qnum, prompts in week4_main.SYSTEM_PROMPTS.items():
                # Get question_id
                q_result = conn.execute(
                    text("SELECT question_id FROM questions WHERE week_id = :week_id AND question_number = :qnum"),
                    {'week_id': week_id, 'qnum': qnum}
                )
                q_row = q_result.fetchone()
                if not q_row:
                    print(f"  ⚠️  Question {qnum} not found")
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
                    prompt_count += 1
            print(f"✓ Inserted {prompt_count} system prompts")
            
            # Insert content blocks
            content_blocks = {
                'WEEK4_VIDEOS_EXERCISES': week4_main.WEEK4_VIDEOS_EXERCISES,
                'WEEK4_EXERCISE1': week4_main.WEEK4_EXERCISE1,
                'WEEK4_EXERCISE2': week4_main.WEEK4_EXERCISE2,
                'FINAL_RESPONSE': week4_main.FINAL_RESPONSE
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
            print(f"✓ Inserted {len([c for c in content_blocks.values() if c])} content blocks")
            
            conn.commit()
    
    print("\n✅ Week 4 populated successfully!")

if __name__ == '__main__':
    populate_week4()


