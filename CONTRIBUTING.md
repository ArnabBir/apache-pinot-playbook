# Contributing

## Principles

1. Keep documentation tied to runnable artifacts.
2. Prefer practical examples over vague advice.
3. Add or update tests when changing contracts, generators or service behavior.
4. Keep configs, queries and explanations in sync.

## Suggested workflow

1. Open an issue or design note.
2. Update the relevant docs chapter.
3. Update any affected schema, table config or contract.
4. Run:

   ```bash
   make generate-contracts
   python scripts/validate_repo.py
   pytest -q
   ```

5. Include before/after reasoning for performance-sensitive changes.

## Style

- Use complete sentences.
- Explain trade-offs, not only choices.
- Prefer deterministic examples that can be re-run.
