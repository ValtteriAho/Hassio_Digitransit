# Contributing

## Development setup

1. Create and activate a virtual environment.
2. Install dependencies:

   ```bash
   pip install -r requirements-dev.txt
   ```

## Local checks

Run all quality checks before opening a pull request.

```bash
ruff check .
pytest -q
```

## Secret safety

Do not commit real API keys or tokens.

- Keep placeholders like `YOUR_API_KEY` in tracked example files.
- Put personal values in untracked local files.
- Rotate any key immediately if it was accidentally committed.

## Pull requests

1. Keep changes focused and small.
2. Include tests for behavior changes when possible.
3. Update docs when setup or behavior changes.
4. Ensure CI passes.

## Release checklist

1. Update `CHANGELOG.md` under `Unreleased` and cut a versioned section.
2. Set the same version in `custom_components/digitransit/manifest.json`.
3. Run local checks:

   ```bash
   ruff check .
   pytest -q
   ```
4. Confirm no real secrets are present in tracked files.
