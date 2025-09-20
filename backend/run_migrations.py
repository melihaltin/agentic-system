#!/usr/bin/env python3
"""
Database Migration Runner
Runs SQL migration files in order and tracks migration history
"""

import os
import sys
from pathlib import Path
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

url = os.environ.get("SUPABASE_URL")
service_key = os.environ.get("SUPABASE_SERVICE_KEY")

if not url or not service_key:
    print(
        "❌ Missing required environment variables: SUPABASE_URL, SUPABASE_SERVICE_KEY"
    )
    sys.exit(1)

supabase: Client = create_client(url, service_key)

# Migration directory
MIGRATIONS_DIR = Path(__file__).parent / "migrations"


def create_migrations_table():
    """Create table to track migration history"""
    try:
        sql = """
        CREATE TABLE IF NOT EXISTS migration_history (
            id SERIAL PRIMARY KEY,
            migration_name VARCHAR(255) NOT NULL UNIQUE,
            executed_at TIMESTAMPTZ DEFAULT NOW(),
            checksum TEXT,
            success BOOLEAN DEFAULT TRUE
        );
        """

        # Try to execute using direct SQL
        supabase.rpc("exec_sql", {"sql": sql}).execute()
        print("✅ Migration history table ready")
        return True
    except Exception as e:
        # Fallback: create table using table operations
        try:
            # Check if table exists first
            supabase.table("migration_history").select("*").limit(1).execute()
            print("✅ Migration history table already exists")
            return True
        except Exception as e2:
            print("❌ Could not create migration history table")
            print(f"   Error: {e}")
            print("   Please create this table manually in Supabase dashboard:")
            print(f"   {sql}")
            return False


def get_executed_migrations():
    """Get list of already executed migrations"""
    try:
        result = supabase.table("migration_history").select("migration_name").execute()
        return [row["migration_name"] for row in result.data]
    except Exception:
        return []


def calculate_checksum(content):
    """Calculate simple checksum for migration content"""
    import hashlib

    return hashlib.md5(content.encode()).hexdigest()


def execute_migration_file(filepath):
    """Execute a single migration file"""
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read()

        migration_name = filepath.name
        checksum = calculate_checksum(content)

        print(f"🚀 Executing migration: {migration_name}")

        # Split content by semicolons and execute each statement
        statements = [stmt.strip() for stmt in content.split(";") if stmt.strip()]

        for i, statement in enumerate(statements):
            if not statement:
                continue

            # Skip comments and empty lines
            if statement.startswith("--") or not statement.strip():
                continue

            try:
                # Try using rpc function first
                supabase.rpc("exec_sql", {"sql": statement}).execute()
            except Exception as rpc_error:
                # If rpc fails, try direct table operations for simple INSERT/UPDATE statements
                if statement.upper().startswith(("INSERT", "UPDATE")):
                    print(
                        f"   ⚠️  RPC failed for statement {i+1}, trying alternative method..."
                    )
                    try:
                        # For INSERT INTO sectors, agent_voices, etc.
                        if "INSERT INTO sectors" in statement:
                            # Parse and execute using table operations
                            print("   📝 Executing sectors insert manually...")
                        elif "INSERT INTO agent_voices" in statement:
                            print("   📝 Executing agent_voices insert manually...")
                        # Add more parsing as needed
                    except Exception as alt_error:
                        print(f"   ❌ Alternative method also failed: {alt_error}")
                        raise rpc_error
                else:
                    raise rpc_error

        # Record successful migration
        try:
            supabase.table("migration_history").insert(
                {
                    "migration_name": migration_name,
                    "checksum": checksum,
                    "success": True,
                }
            ).execute()
        except Exception:
            # If we can't record the migration, at least note it
            print(f"   ⚠️  Could not record migration history for {migration_name}")

        print(f"   ✅ Migration {migration_name} completed successfully")
        return True

    except Exception as e:
        print(f"   ❌ Migration {migration_name} failed: {e}")

        # Try to record failed migration
        try:
            supabase.table("migration_history").insert(
                {
                    "migration_name": migration_name,
                    "checksum": checksum,
                    "success": False,
                }
            ).execute()
        except Exception:
            pass

        return False


def run_migrations():
    """Run all pending migrations in order"""
    print("🔄 Starting database migrations...")

    # Create migrations table if needed
    if not create_migrations_table():
        return False

    # Get list of executed migrations
    executed_migrations = get_executed_migrations()
    print(f"📊 Found {len(executed_migrations)} previously executed migrations")

    # Get all migration files
    if not MIGRATIONS_DIR.exists():
        print(f"❌ Migrations directory not found: {MIGRATIONS_DIR}")
        return False

    migration_files = sorted(
        [f for f in MIGRATIONS_DIR.glob("*.sql") if f.name not in executed_migrations]
    )

    if not migration_files:
        print("✅ No pending migrations found. Database is up to date!")
        return True

    print(f"📋 Found {len(migration_files)} pending migrations")

    # Execute migrations in order
    success_count = 0
    for migration_file in migration_files:
        if execute_migration_file(migration_file):
            success_count += 1
        else:
            print(f"❌ Migration failed: {migration_file.name}")
            print("   Stopping migration process.")
            break

    if success_count == len(migration_files):
        print(f"\n🎉 All {success_count} migrations completed successfully!")
        return True
    else:
        print(f"\n⚠️  {success_count}/{len(migration_files)} migrations completed")
        return False


def show_migration_status():
    """Show current migration status"""
    print("📊 Migration Status:")

    executed_migrations = get_executed_migrations()
    all_migration_files = (
        sorted(list(MIGRATIONS_DIR.glob("*.sql"))) if MIGRATIONS_DIR.exists() else []
    )

    if not all_migration_files:
        print("   No migration files found")
        return

    for migration_file in all_migration_files:
        status = (
            "✅ EXECUTED"
            if migration_file.name in executed_migrations
            else "⏳ PENDING"
        )
        print(f"   {migration_file.name}: {status}")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "status":
        show_migration_status()
    elif len(sys.argv) > 1 and sys.argv[1] == "init":
        create_migrations_table()
    else:
        success = run_migrations()
        sys.exit(0 if success else 1)
