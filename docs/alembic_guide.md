## Using Alembic

[Alembic](https://alembic.sqlalchemy.org/) manages changes to the database schema. Each change is a
version-controlled **migration** file in `alembic/versions/`, so everyone's database (and production)
can be brought to the same schema by running the same files in order.

The database URL comes from `DATABASE_URL` (same as the app, see `src/app/core/database.py`), defaulting
to a local SQLite file `gradvision.db`. `alembic/env.py` reads our models from `app.models.models`, so
**Alembic only sees tables that are defined there.**

> Run all `alembic` commands from the **repo root** (where `alembic.ini` lives), not from `src/`.

### Setting up your database (first time, or after pulling new migrations)

```bash
uv run alembic upgrade head
```

This creates any missing tables and applies any migrations your database hasn't run yet. It's safe to
re-run; if you're already up to date it does nothing. Do this after every `git pull` that adds a file
to `alembic/versions/`.

### Changing the schema

1. Edit the models in `src/app/models/models.py`.
2. Generate a migration by comparing the models to the database:
   ```bash
   uv run alembic revision --autogenerate -m "add notes column to tasks"
   ```
   Your database must be up to date (`upgrade head`) before you do this, or Alembic will diff against the wrong state.
3. **Open the new file in `alembic/versions/` and review it.** Do note that autogenerate also has some limitations:
   - It can't detect table/column *renames*, so it emits a drop + add (which loses data). Rewrite as `op.alter_column` / `op.rename_table`.
   - It doesn't see `association_proxy`s or `@property`s. These aren't columns, so changing them needs no migration.
   - Adding a `nullable=False` column to a table that already has rows needs a `server_default`.
4. Apply it: `uv run alembic upgrade head`
5. Commit the migration file together with the model change.

### Common commands

| Command | What it does |
|---|---|
| `uv run alembic upgrade head` | Apply all pending migrations |
| `uv run alembic upgrade +1` | Apply just the next migration |
| `uv run alembic downgrade -1` | Undo the most recent migration |
| `uv run alembic downgrade base` | Undo everything (empties the schema) |
| `uv run alembic current` | Show which revision the database is at |
| `uv run alembic history` | List all migrations, newest first |
| `uv run alembic heads` | Show the latest revision(s). More than one means branched history, so run `alembic merge heads` |
| `uv run alembic check` | Fail if the models differ from the migrations (a quick "did I forget a migration?" check) |
| `uv run alembic upgrade head --sql` | Print the SQL instead of running it (handy for reviewing before production) |
| `uv run alembic revision -m "msg"` | Create an empty migration to hand-write (data migrations, etc.) |
| `uv run alembic stamp head` | Mark the database as up to date **without running anything** (see below) |

### `Base.metadata.create_all()` vs. Alembic

`create_all()` creates tables that don't exist yet and **never alters existing ones**. It doesn't record
what it did, so Alembic has no idea the tables are there. Pick one owner for the schema, and for this
project that's Alembic. Don't call `create_all()` in app code.

- If you ran `create_all()` on a database (or have an old `gradvision.db` from before Alembic) and then run
  `alembic upgrade head`, it fails with `table ... already exists`. Either delete the `.db` file and run
  `alembic upgrade head`, or, if the tables already match the models and you want to keep the data, run
  `alembic stamp head` once to tell Alembic "this database is already at the latest revision".
- Adding a column to a model and re-running `create_all()` does **nothing**, because the table already exists.
  That's the situation migrations exist for.

### Gotchas

- **Never edit a migration that's been merged/shared.** Add a new one on top instead. Editing history
  makes teammates' databases and yours disagree.
- **SQLite can't `ALTER` most things** (change a column type, drop a constraint, and so on). If a local
  migration of that kind fails, wrap the operation in `with op.batch_alter_table("table") as batch:`.
  Postgres doesn't have this limitation.
- **Merge conflicts in migrations:** if two branches each add a migration, `alembic heads` shows two heads.
  Run `uv run alembic merge heads -m "merge"` to join them.
- Resetting your local database is always an option: delete `gradvision.db` and run `alembic upgrade head`.