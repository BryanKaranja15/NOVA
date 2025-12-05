# Files to Remove - Cleanup List

## 1. Outdated/Duplicate Database Schema Files
Keep only: `database_schema_final.sql`
Remove:
- `database_schema.sql` (original, replaced by final)
- `database_schema_simplified.sql` (outdated simplification attempt)
- `database_schema_corrected.sql` (intermediate version)

## 2. Outdated Documentation Files
Keep only: `SYSTEM_ARCHITECTURE.md` (current)
Remove:
- `ARCHITECTURE_WITH_DATABASE.md` (outdated, replaced by SYSTEM_ARCHITECTURE.md)
- `CODE_EXAMPLE_BEFORE_AFTER.md` (development doc, not needed)
- `SCHEMA_COMPARISON.md` (comparison doc, no longer relevant)
- `DATABASE_TABLES_SUMMARY.md` (redundant with other docs)
- `CORRECTED_SCHEMA_EXPLANATION.md` (temporary explanation doc)
- `DATABASE_FIXES_SUMMARY.md` (temporary summary, info in SYSTEM_ARCHITECTURE.md)

## 3. Duplicate/Unnecessary SQL Scripts
Keep only essential scripts:
- `scripts/create_all_tables.sql` (or the simple version if preferred)
- `scripts/clear_database.sql` (or the simple version if preferred)
- `scripts/drop_all_tables.sql` (or the simple version if preferred)
- `scripts/verify_database.py` (useful for testing)

Remove:
- `scripts/clear_database_simple.sql` (if keeping the full version)
- `scripts/create_all_tables_simple.sql` (if keeping the full version)
- `scripts/drop_all_tables_simple.sql` (if keeping the full version)
- `scripts/clear_and_drop_database.sql` (can be done with separate scripts)
- `scripts/remove_unnecessary_tables.sql` (one-time migration script, no longer needed)
- `scripts/remove_unnecessary_tables_simple.sql` (one-time migration script)
- `scripts/remove_unnecessary_tables.py` (one-time migration script)
- `scripts/remove_only_unnecessary.sql` (one-time migration script)
- `scripts/restore_necessary_tables.sql` (one-time migration script)
- `scripts/restore_necessary_tables_simple.sql` (one-time migration script)

## 4. Test/Development Files
Remove:
- `test.py` (test file, not used in production)
- `follow.py` (old file, only referenced in comment)
- `PROGRESS_STRUCTURE_EXAMPLE.json` (example file, not needed)

## 5. Old Text/Prompt Files
Remove:
- `All Videos + Exercises.txt` (old reference material)
- `Copy of Week 1 prompts.txt` (old prompts, now in code/database)

## 6. Unused Large Directories
Remove (if not using LightRAG):
- `LIGHTRAG_FOLDER/` (entire directory - large third-party library not used in main app)

## 7. Cache/Build Files (can regenerate)
Remove:
- `__pycache__/` directories (Python cache, regenerated automatically)
- Note: `venv/` should stay (virtual environment), but should be in .gitignore

## 8. Redundant Setup Documentation
Keep only: `SETUP_DATABASE.md` or `SUPABASE_SETUP.md` (whichever is more current)
Remove the other one if they're duplicates.

## 9. Other Documentation
Consider keeping but could remove if redundant:
- `WEEK_INTEGRATION_README.md` (if info is in SYSTEM_ARCHITECTURE.md)
- `PORT_CONFIGURATION.md` (if info is in SYSTEM_ARCHITECTURE.md)
- `DATABASE_RISKS_AND_ISSUES.md` (useful reference, but could be archived)
- `DATABASE_SCHEMA_DOCUMENTATION.md` (useful reference, but could be archived)
- `SYSTEM_FLOW_DIAGRAM.md` (useful reference, but could be archived)

## Summary
Total files/directories to remove: ~30-40 items
This will significantly clean up the directory while keeping all essential files.


