# Prompt Preservation Strategy

## Critical Requirements

**MUST PRESERVE:**
1. ✅ Every single word in every prompt (exact text matching)
2. ✅ All variable placeholders (e.g., `{name}`, `{WEEK4_VIDEOS_EXERCISES}`)
3. ✅ Exact flow logic (scenario classification, iteration handling, question progression)
4. ✅ User experience (timing, responses, transitions)

## Preservation Approach

### Phase 1: Extract Prompts (Exact Copy)
- Extract ALL prompts from current code files
- Store them EXACTLY as-is in database
- No modifications, no reformatting, no "improvements"
- Preserve all whitespace, line breaks, formatting

### Phase 2: Database Storage
- Store prompts in `system_prompts` table with `prompt_text` field (TEXT type - no length limits)
- Store content blocks in `week_content_blocks` table
- Use exact matching for variable substitution

### Phase 3: Code Integration
- Replace hardcoded dict lookups with database queries
- Ensure database returns prompts in EXACT same format
- Maintain same variable substitution logic
- Keep same flow control logic

## Current Prompt Locations

### Week 1 (`temporary_main.py`)
- Questions: Lines 471-486
- System Prompts: Lines 489-870+ (complex structure)
- Content Blocks: Various constants (HOMEWORK_QUESTIONS_Q2, THINKING_FLEXIBLY_NOTES, etc.)

### Week 2 (`temporary_week2_main.py`)
- Questions: Lines 442-451
- System Prompts: Lines 452-1040+

### Week 3 (`temporary_main_q16_22.py`)
- Questions: Lines 411-440
- System Prompts: Lines 441-1632+

### Week 4 (`week4_main.py`)
- Questions: Lines 192-200
- System Prompts: Lines 203-387
- Welcome Message: Lines 389-396
- Final Response: Lines 398-399
- Content Blocks: WEEK4_VIDEOS_EXERCISES, WEEK4_EXERCISE1, WEEK4_EXERCISE2

### Week 5 (`week5_main.py`)
- Questions: Lines 189-197
- System Prompts: Lines 198-590+

## Variable Substitution Requirements

### Must Preserve These Patterns:
- `{name}` - User's name
- `{WEEK4_VIDEOS_EXERCISES}` - Content block
- `{WEEK4_EXERCISE1}` - Content block
- `{WEEK4_EXERCISE2}` - Content block
- `{Answer to question X}` - Previous user answers
- `{{name}}` - Double braces (f-string escaping)
- `{{Response from 1}}` - Previous responses

### Substitution Logic:
- Must happen at runtime (not in database)
- Must match current code's substitution logic exactly
- Must preserve all other text unchanged

## Flow Preservation Requirements

### Question Progression:
- Must maintain exact same question order
- Must preserve transition messages (e.g., Q2 transition in Week 4)
- Must preserve welcome messages and final responses

### Scenario Classification:
- Must use exact same classifier prompts
- Must classify into same scenarios (SCENARIO_1, SCENARIO_2, SCENARIO_3, etc.)
- Must use same scenario response prompts

### Iteration Handling:
- Must preserve max_iterations logic
- Must preserve iteration counting
- Must preserve question completion logic

### Validation:
- Must preserve validation prompts (if any)
- Must preserve validation logic
- Must preserve follow-up question logic

## Implementation Checklist

### Before Migration:
- [ ] Extract ALL prompts from ALL week files
- [ ] Verify exact text (character-by-character comparison)
- [ ] Document all variable placeholders
- [ ] Document all content blocks
- [ ] Document flow logic for each week

### During Migration:
- [ ] Insert prompts into database with exact text
- [ ] Insert content blocks with exact text
- [ ] Insert questions with exact text
- [ ] Verify database storage (query and compare)

### After Migration:
- [ ] Update code to read from database
- [ ] Verify variable substitution works
- [ ] Test flow logic matches exactly
- [ ] Test user experience is identical
- [ ] Compare outputs side-by-side (old vs new)

## Testing Strategy

### Unit Tests:
1. Extract prompt from database
2. Compare character-by-character with original
3. Verify variable substitution
4. Verify scenario classification

### Integration Tests:
1. Run same user input through old and new system
2. Compare outputs word-for-word
3. Verify flow progression matches
4. Verify timing matches

### User Acceptance:
1. Test with real user scenarios
2. Verify responses are identical
3. Verify flow feels the same
4. No user-facing changes

## Risk Mitigation

### Backup Strategy:
- Keep original code files as backup
- Version control all changes
- Can rollback instantly if needed

### Validation:
- Automated comparison scripts
- Manual review of critical prompts
- Side-by-side testing

### Rollback Plan:
- If any prompt differs, rollback immediately
- If flow differs, rollback immediately
- If user experience differs, rollback immediately

## Success Criteria

✅ **ZERO** word changes in prompts
✅ **ZERO** flow changes from user perspective
✅ **ZERO** timing changes
✅ **ZERO** response differences
✅ Database is just a storage layer - completely transparent to user


