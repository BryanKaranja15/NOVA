# Database Integration Risks & Issues

## Critical Issues (Will Break System)

### 1. **Code Still Uses In-Memory State**
**Current Code:**
```python
conversation_states = {}  # In-memory dictionary
state = conversation_states[session_id]  # Gets from memory
```

**Problem:**
- State is lost on server restart
- Database exists but code doesn't use it
- No persistence between requests if server crashes

**Impact:** 🔴 **CRITICAL** - System works but loses all state on restart

---

### 2. **Hardcoded Prompts Not in Database**
**Current Code:**
```python
QUESTIONS = {
    1: "What was one main idea you took away?",
    2: "How was your experience...",
    # Hardcoded in Python
}

SYSTEM_PROMPTS = {
    1: {
        "classifier": "...",
        "scenario_1_respond": "...",
        # Hardcoded in Python
    }
}
```

**Problem:**
- Prompts are still in code, not database
- Database tables exist but are empty
- Code will fail if it tries to load from empty database

**Impact:** 🔴 **CRITICAL** - System will break if code tries to use database

---

### 3. **No Database Integration in Code**
**Current Code:**
- No imports: `from database.db_models import ...`
- No database queries
- No database initialization in week modules

**Problem:**
- Database is set up but completely unused
- Code has no way to read from database
- Prompts/questions still come from hardcoded dicts

**Impact:** 🔴 **CRITICAL** - Database is orphaned, code doesn't use it

---

## Data Structure Mismatches

### 4. **State Structure Mismatch**
**Current Code:**
```python
state.answers = {1: ["answer1", "answer2"], 2: ["answer3"]}  # Dict of lists
state.nova_responses = {1: ["response1"], 2: ["response2"]}  # Dict of lists
state.iteration_count = {1: 2, 2: 1}  # Dict
state.question_completed = {1: True, 2: False}  # Dict
```

**Database:**
- `user_answers` - Separate rows per answer
- `nova_responses` - Separate rows per response
- `question_completions` - Separate rows per question
- `conversation_states.conversation_data` - JSONB (can store dicts)

**Problem:**
- Code expects dicts, database has separate tables
- Need to convert between formats
- Performance: Multiple queries vs single dict access

**Impact:** 🟡 **MEDIUM** - Requires data transformation layer

---

### 5. **Session ID vs User ID Mismatch**
**Current Code:**
```python
session_id = session.get('session_id')  # Flask session
state = conversation_states[session_id]  # Uses session_id as key
```

**Database Schema:**
- Uses `session_id` (good - matches!)
- But some old docs reference `user_id`

**Problem:**
- Need to ensure all tables use `session_id` consistently
- No `users` table means no user authentication

**Impact:** 🟢 **LOW** - Schema already uses session_id, but verify all tables

---

### 6. **Week Number vs Week ID**
**Current Code:**
```python
week_number = 4  # Hardcoded
QUESTIONS = {...}  # Week-specific questions
```

**Database:**
- `weeks.week_id` - Primary key (SERIAL)
- `weeks.week_number` - Week number (1-6)

**Problem:**
- Code uses `week_number`, database needs `week_id` for foreign keys
- Need to look up `week_id` from `week_number` first

**Impact:** 🟡 **MEDIUM** - Need helper function to get week_id

---

## Prompt Structure Issues

### 7. **Prompt Type Mismatch**
**Current Code:**
```python
SYSTEM_PROMPTS = {
    1: {
        "classifier": "...",
        "scenario_1_respond": "...",
        "scenario_2_respond": "...",
    }
}
```

**Database:**
- `system_prompts.prompt_type` - Single string
- `system_prompts.scenario_name` - Separate field

**Problem:**
- Code expects nested dict, database is flat
- Need to query multiple rows and reconstruct dict
- Performance: Multiple queries per question

**Impact:** 🟡 **MEDIUM** - Need query helper to build dict structure

---

### 8. **Variable Substitution Complexity**
**Current Code:**
```python
# In prompts: "{Answer to question 4}"
# Code does: state.get_answer(4) to replace it
system_prompt = state.substitute_variables(system_prompt)
```

**Database:**
- Prompts stored with placeholders: `"{Answer to question 4}"`
- Need to query `user_answers` to get answer
- Need to replace in code before sending to LLM

**Problem:**
- Variable substitution logic must work with database queries
- Need to handle: `{name}`, `{Answer to question X}`, `{WEEK4_CONTENT}`
- Performance: Additional queries for each variable

**Impact:** 🟡 **MEDIUM** - Complex substitution logic needed

---

### 9. **Content Block Insertion**
**Current Code:**
```python
WEEK4_VIDEOS_EXERCISES = "..."  # Hardcoded constant
# Used in prompts via {WEEK4_VIDEOS_EXERCISES}
```

**Database:**
- `week_content_blocks` table stores these
- Need to query and insert into prompts

**Problem:**
- Code does simple string replacement
- Database requires query + replacement
- Need to handle multiple content blocks per prompt

**Impact:** 🟡 **MEDIUM** - Additional query overhead

---

## Performance & Reliability Issues

### 10. **Database Query Overhead**
**Current:**
- In-memory dict access: O(1), instant
- No network latency
- No database connection overhead

**With Database:**
- Network round-trip to Supabase
- Connection pooling overhead
- Multiple queries per request (questions, prompts, content blocks, state)

**Problem:**
- Slower response times
- More points of failure
- Database connection limits

**Impact:** 🟡 **MEDIUM** - Performance degradation, need caching

---

### 11. **No Caching Strategy**
**Current:**
- Prompts loaded once at startup (in-memory)
- Instant access

**With Database:**
- Queries on every request
- Same prompts queried repeatedly

**Problem:**
- Unnecessary database load
- Slower responses
- Higher Supabase costs

**Impact:** 🟡 **MEDIUM** - Need caching layer

---

### 12. **Transaction Management**
**Current:**
- In-memory updates are instant
- No rollback needed

**With Database:**
- Multiple inserts per request:
  - `user_answers` insert
  - `conversation_messages` insert (user)
  - `conversation_messages` insert (nova)
  - `conversation_states` update
  - `question_completions` insert/update

**Problem:**
- Need transactions for atomicity
- Partial failures leave inconsistent state
- Need rollback on errors

**Impact:** 🟡 **MEDIUM** - Need proper transaction handling

---

### 13. **Database Connection Failures**
**Current:**
- No external dependencies for state
- Always works (if server is up)

**With Database:**
- Supabase could be down
- Network issues
- Connection pool exhaustion
- Rate limiting

**Problem:**
- System completely breaks if database unavailable
- No fallback mechanism
- Need error handling and retries

**Impact:** 🔴 **HIGH** - Need fallback/error handling

---

## Data Migration Issues

### 14. **No Data Migration Script**
**Current:**
- Prompts in code
- Questions in code
- Content blocks in code

**Database:**
- Tables exist but are empty
- No way to populate from code

**Problem:**
- Manual data entry required
- Error-prone
- Time-consuming
- No version control for data

**Impact:** 🔴 **HIGH** - Need migration script to populate database

---

### 15. **Existing State Loss**
**Current:**
- In-memory state for active sessions
- JSON file for progress

**With Database:**
- Old in-memory state will be lost
- Need to migrate existing progress from JSON
- Active sessions will reset

**Problem:**
- Users lose progress
- Conversations reset
- Need migration strategy

**Impact:** 🟡 **MEDIUM** - Need migration for existing users

---

## Code Integration Issues

### 16. **No Database Models Created**
**Current:**
- `database/db_config.py` exists
- `database/db_models.py` does NOT exist

**Problem:**
- No SQLAlchemy models defined
- Can't query database from Python
- No ORM layer

**Impact:** 🔴 **CRITICAL** - Can't use database without models

---

### 17. **Week Modules Don't Import Database**
**Current:**
```python
# week4_main.py
from progress_tracker import progress_tracker  # Uses JSON file
# No database imports
```

**Problem:**
- Code has no database awareness
- No way to load prompts from database
- Still uses hardcoded data

**Impact:** 🔴 **CRITICAL** - Database is unused

---

### 18. **Progress Tracker Still Uses JSON**
**Current:**
```python
from progress_tracker import progress_tracker
progress_tracker.update_user_progress(session_id, week_number, question_number)
# Writes to user_progress.json
```

**Problem:**
- Progress still saved to JSON file
- Database `question_completions` table unused
- Dual storage (inconsistent)

**Impact:** 🟡 **MEDIUM** - Need to update progress_tracker.py

---

## Schema-Specific Issues

### 19. **Missing Foreign Key Data**
**Database Requires:**
- `week_id` to create questions
- `question_id` to create prompts
- `week_id` to create content blocks

**Current:**
- No data in database
- Can't create questions without weeks
- Can't create prompts without questions

**Problem:**
- Need to insert in order: weeks → questions → prompts → content blocks
- Circular dependencies possible
- Need seed data script

**Impact:** 🟡 **MEDIUM** - Need proper data insertion order

---

### 20. **JSONB Field Complexity**
**Database:**
```sql
conversation_data JSONB NOT NULL  -- Stores complex state
```

**Current Code:**
```python
state.answers = {1: ["a1", "a2"], 2: ["a3"]}  # Complex nested structure
```

**Problem:**
- Need to serialize/deserialize JSONB
- Query complexity for nested data
- Type safety issues
- Harder to query specific fields

**Impact:** 🟡 **MEDIUM** - Need JSONB handling utilities

---

## Testing & Validation Issues

### 21. **No Integration Tests**
**Problem:**
- Can't test database integration
- Can't verify prompts load correctly
- Can't test state persistence

**Impact:** 🟡 **MEDIUM** - Need test suite

---

### 22. **No Data Validation**
**Problem:**
- No validation that prompts are complete
- No check for missing prompts
- No verification of prompt structure

**Impact:** 🟡 **MEDIUM** - Need validation scripts

---

## Summary of Risks

### 🔴 **CRITICAL (Must Fix)**
1. Code doesn't use database (still in-memory)
2. No database models (db_models.py missing)
3. Hardcoded prompts not migrated
4. Database connection failure = system down

### 🟡 **MEDIUM (Should Fix)**
5. Data structure mismatches
6. Performance issues (no caching)
7. Transaction management
8. Week number vs week_id
9. Prompt structure conversion
10. Variable substitution complexity
11. No data migration script

### 🟢 **LOW (Nice to Have)**
12. Session ID consistency (already good)
13. Integration tests
14. Data validation

---

## Recommended Approach

### Phase 1: Keep Current System Working
1. ✅ Database schema created (done)
2. ⚠️ **Create database models** (db_models.py)
3. ⚠️ **Create data migration script** (extract prompts from code)
4. ⚠️ **Populate database** with existing prompts/questions

### Phase 2: Gradual Integration
5. ⚠️ **Add caching layer** (cache prompts in memory)
6. ⚠️ **Create service layer** (abstract database access)
7. ⚠️ **Update one week module** as test
8. ⚠️ **Add error handling** (fallback to in-memory if DB fails)

### Phase 3: Full Migration
9. ⚠️ **Update all week modules**
10. ⚠️ **Update progress_tracker** to use database
11. ⚠️ **Remove hardcoded data**
12. ⚠️ **Add monitoring/logging**

---

## Quick Fixes Needed NOW

1. **Create `database/db_models.py`** - SQLAlchemy models
2. **Create migration script** - Extract prompts from code to database
3. **Add error handling** - Don't break if database unavailable
4. **Add caching** - Cache prompts in memory after first load


