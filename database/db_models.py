"""
Database Models and Access Functions

This module provides functions to access database content (prompts, questions, etc.)
while maintaining the exact same interface as the hardcoded dicts.
"""

from flask import Flask, current_app, has_app_context
from sqlalchemy import text
from database.db_config import db, init_db
from typing import Dict, List, Optional, Any


def get_week_content(week_number: int, app: Flask = None) -> Dict[str, Any]:
    """
    Get all content for a week (questions, prompts, welcome message, etc.)
    Returns a dict that matches the structure of hardcoded QUESTIONS and SYSTEM_PROMPTS.
    
    Args:
        week_number: Week number (1-6)
        app: Flask app instance (required for database connection)
    
    Returns:
        {
            'week_id': int,
            'welcome_message': str,
            'final_response': str,
            'questions': {question_number: question_text, ...},
            'system_prompts': {question_number: {prompt_type: prompt_text, ...}, ...},
            'content_blocks': {block_name: content_text, ...}
        }
    """
    # Use provided app or current_app if in request context
    if app is None:
        if has_app_context():
            app = current_app
        else:
            raise ValueError("Flask app instance required or must be in application context")
    
    with app.app_context():
        with db.engine.connect() as conn:
            # Get week - using week_number (not week_id) to ensure correct week
            week_result = conn.execute(
                text("SELECT week_id, welcome_message FROM weeks WHERE week_number = :week_num"),
                {'week_num': week_number}
            )
            week_row = week_result.fetchone()
            if not week_row:
                raise ValueError(f"Week {week_number} not found in database")
            
            week_id = week_row[0]
            welcome_message = week_row[1]
            
            # Get questions - linked via week_id (which corresponds to week_number=4)
            questions_result = conn.execute(
                text("""
                    SELECT question_number, question_text 
                    FROM questions 
                    WHERE week_id = :week_id 
                    ORDER BY question_number
                """),
                {'week_id': week_id}
            )
            questions = {row[0]: row[1] for row in questions_result}
            
            # Get system prompts organized by question
            prompts_result = conn.execute(
                text("""
                    SELECT q.question_number, sp.prompt_type, sp.prompt_text, sp.scenario_name
                    FROM system_prompts sp
                    JOIN questions q ON sp.question_id = q.question_id
                    WHERE q.week_id = :week_id
                    ORDER BY q.question_number, sp.sort_order
                """),
                {'week_id': week_id}
            )
            
            system_prompts = {}
            for row in prompts_result:
                qnum, prompt_type, prompt_text, scenario_name = row
                if qnum not in system_prompts:
                    system_prompts[qnum] = {}
                system_prompts[qnum][prompt_type] = prompt_text
            
            # Get content blocks
            blocks_result = conn.execute(
                text("""
                    SELECT block_name, content_text 
                    FROM week_content_blocks 
                    WHERE week_id = :week_id
                """),
                {'week_id': week_id}
            )
            content_blocks = {row[0]: row[1] for row in blocks_result}
            
            # Get final response (stored as a content block or in week metadata)
            final_response = None
            final_result = conn.execute(
                text("SELECT content_text FROM week_content_blocks WHERE week_id = :week_id AND block_name = 'FINAL_RESPONSE'"),
                {'week_id': week_id}
            )
            final_row = final_result.fetchone()
            if final_row:
                final_response = final_row[0]
            
            return {
                'week_id': week_id,
                'welcome_message': welcome_message,
                'final_response': final_response,
                'questions': questions,
                'system_prompts': system_prompts,
                'content_blocks': content_blocks
            }


def get_question_prompts(week_number: int, question_number: int, app: Flask = None) -> Dict[str, str]:
    """
    Get all prompts for a specific question.
    Returns dict matching SYSTEM_PROMPTS[question_number] structure.
    
    Returns:
        {'classifier': '...', 'scenario_1_respond': '...', ...}
    """
    week_content = get_week_content(week_number, app)
    return week_content['system_prompts'].get(question_number, {})


def get_question_text(week_number: int, question_number: int, app: Flask = None) -> Optional[str]:
    """Get question text for a specific question."""
    week_content = get_week_content(week_number, app)
    return week_content['questions'].get(question_number)


def get_content_block(week_number: int, block_name: str, app: Flask = None) -> Optional[str]:
    """Get a content block by name (e.g., 'WEEK4_VIDEOS_EXERCISES')."""
    week_content = get_week_content(week_number, app)
    return week_content['content_blocks'].get(block_name)


def get_welcome_message(week_number: int, app: Flask = None) -> Optional[str]:
    """Get welcome message for a week."""
    week_content = get_week_content(week_number, app)
    return week_content.get('welcome_message')


def get_final_response(week_number: int, app: Flask = None) -> Optional[str]:
    """Get final response for a week."""
    week_content = get_week_content(week_number, app)
    return week_content.get('final_response')


def format_prompt_with_variables(prompt_text: str, variables: Dict[str, str]) -> str:
    """
    Format a prompt string with variable substitutions.
    Handles both {name} and {{name}} (f-string escaping) patterns.
    
    Args:
        prompt_text: The prompt template with placeholders
        variables: Dict of variable names to values
    
    Returns:
        Formatted prompt with variables substituted
    """
    result = prompt_text
    
    # Handle single braces {variable}
    for var_name, var_value in variables.items():
        result = result.replace(f"{{{var_name}}}", str(var_value))
    
    # Handle double braces {{variable}} (f-string escaping)
    for var_name, var_value in variables.items():
        result = result.replace(f"{{{{var_name}}}}", str(var_value))
    
    return result

