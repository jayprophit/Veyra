#!/usr/bin/env python3
"""
Database Migration Setup Script for Financial Master
Initialize Alembic for production-grade database versioning
"""

import os
import sys
from pathlib import Path


def create_alembic_structure():
    """Create Alembic directory structure for Financial Master."""

    alembic_config = """# Configuration for Alembic DB migration tool

[alembic]
# path to migration scripts
sqlalchemy.url = driver://user:password@localhost/dbname

# template used to generate migration file names; The default value is %%(rev)s_%%(slug)s
# Uncomment the line below if you want the files to be prepended with date and time
#file_template = %%(created_at)s_%%(rev)s_%%(slug)s

# sys.path path, will be prepended to sys.path if present
# defaults to the current working directory
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as text, choices are 'ltz', 'utc', or None (defaults to None)
timezone = utc

# max length of characters to apply to the "slug" field
# truncate_slug_len = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
# revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
# sourceless = false

# logging configuration
# when set to 'true', Alembic will log the SQL statements
# executed; this is useful for debugging issues with
# databases that silently ignore certain DDL directives
# sqlalchemy_echo = false

# when set to 'true', or to a list of strings, the alembic migrate
# process will not attempt to get column information via the
# 'PRAGMA table_info' call on SQLite databases
# sqlalchemy.url uses this to mean an immediate "throw" on
# an attempt using no arguments with SQLAlchemy
# on_version_apply = None

[loggers]
keys = root,sqlalchemy

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

    env_py = '''"""
Alembic environment for Financial Master
Auto-generates migrations from SQLAlchemy models
"""

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# This is the Alembic Config object
config = context.config

# Process Alembic configuration file
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add your model's MetaData object here
target_metadata = None

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode (no database connection)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode (with database connection)."""
    configuration = config.get_section(config.config_ini_section)
    configuration["sqlalchemy.url"] = config.get_main_option("sqlalchemy.url")

    connectable = engine_from_config(
        configuration, prefix="sqlalchemy.", poolclass=pool.NullPool
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
'''

    script_py = '''"""
Alembic migration template
Automatically generated migrations go here
"""

from alembic import op
import sqlalchemy as sa

# Migration version
revision = ${repr(up_revision)}
down_revision = ${repr(down_revision)}
branch_labels = ${repr(branch_labels)}
depends_on = ${repr(depends_on)}


def upgrade() -> None:
    """Forward migration"""
    ${upgrades if upgrades else "pass"}


def downgrade() -> None:
    """Backward migration - rollback"""
    ${downgrades if downgrades else "pass"}
'''

    return {
        'alembic.ini': alembic_config,
        'alembic/env.py': env_py,
        'alembic/script.py.mako': script_py,
    }


def setup_alembic():
    """Set up Alembic directory structure."""

    print("Setting up Alembic for Financial Master")
    print("=" * 70)

    # Create alembic directory
    alembic_dir = Path("alembic")
    alembic_dir.mkdir(exist_ok=True)
    (alembic_dir / "versions").mkdir(exist_ok=True)

    # Create configuration files
    files = create_alembic_structure()

    for file_path, content in files.items():
        full_path = Path(file_path)
        full_path.parent.mkdir(parents=True, exist_ok=True)

        if not full_path.exists():
            print(f"Creating: {file_path}")
            full_path.write_text(content)
        else:
            print(f"Already exists: {file_path}")

    print("\n✓ Alembic setup complete!")
    print("\nNext steps:")
    print("1. Update alembic.ini with your database URL")
    print("2. Create initial migration:")
    print("   alembic revision --autogenerate -m 'Initial migration'")
    print("3. Apply migrations:")
    print("   alembic upgrade head")
    print("4. To rollback:")
    print("   alembic downgrade -1")
    print("\nUseful commands:")
    print("  alembic revision --autogenerate -m 'Description'  # Create new migration")
    print("  alembic upgrade head                               # Apply all pending")
    print("  alembic downgrade <revision>                       # Rollback to specific")
    print("  alembic history                                    # Show migration history")


if __name__ == "__main__":
    setup_alembic()
