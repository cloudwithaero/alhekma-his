# Al Hekma Hospital HIS

Hospital Information System for Al Hekma Hospital - Mansoura.

## Project Structure

- `backend/` — Frappe/ERPNext custom app (`alhekma`)
- `frontend/` — React/Vite hospital frontend
- `docs/PROJECT_STATE.md` — current project state and handoff guide

## Start Here

Before making changes:

1. Read `docs/PROJECT_STATE.md`.
2. Inspect both `backend/` and `frontend/`.
3. Preserve the existing architecture and project rules.
4. Do not modify Frappe, ERPNext, or Healthcare core files.
5. Keep backend customization inside `backend/alhekma/`.
6. Keep frontend code inside `frontend/`.

## Important

`docs/PROJECT_STATE.md` is the current handoff document.
Verify implementation details against the actual source code before making changes.

Do not make architectural or data-model changes without understanding the existing project state.
