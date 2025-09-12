# Supabase Migration Guide

This guide helps you migrate between traditional PostgreSQL and Supabase backends, or set up dual support.

## Architecture Overview

The backend supports both traditional PostgreSQL with custom JWT authentication and Supabase with built-in auth. You can:

1. **Traditional Only**: Use PostgreSQL + SQLAlchemy + custom JWT (default)
2. **Supabase Only**: Use Supabase for everything (auth, database, storage)
3. **Hybrid**: Use both systems (useful for migration)

## Migration Scenarios

### 1. From Traditional to Supabase

#### Step 1: Set up Supabase Project
1. Create a new project at [supabase.com](https://supabase.com)
2. Run the SQL setup script in `sql/supabase_setup.sql`
3. Get your project URL and API keys

#### Step 2: Update Configuration
```bash
# Add to your .env file
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here
USE_SUPABASE_AUTH=true  # Switch to Supabase auth
```

#### Step 3: Migrate Existing Users (Optional)
Create a migration script to move existing users:

```python
# migration_to_supabase.py
import asyncio
from core.database import async_session_factory
from core.supabase import supabase_client
from features.users.repository import UserRepository

async def migrate_users():
    async with async_session_factory() as session:
        user_repo = UserRepository(session)
        users = await user_repo.get_all(skip=0, limit=1000)
        
        for user in users:
            # Create user in Supabase Auth (they'll need to reset password)
            try:
                auth_response = supabase_client.service_client.auth.admin.create_user({
                    "email": user.email,
                    "password": "temp_password_12345",  # They'll reset this
                    "email_confirm": True,
                    "user_metadata": {
                        "username": user.username,
                        "full_name": user.full_name,
                        "bio": user.bio,
                        "avatar_url": user.avatar_url
                    }
                })
                
                # Create profile record
                if auth_response.user:
                    profile_data = {
                        "id": auth_response.user.id,
                        "email": user.email,
                        "username": user.username,
                        "full_name": user.full_name,
                        "bio": user.bio,
                        "avatar_url": user.avatar_url,
                        "is_active": user.is_active
                    }
                    
                    supabase_client.service_client.table('profiles').insert(profile_data).execute()
                    print(f"Migrated user: {user.email}")
                    
            except Exception as e:
                print(f"Failed to migrate user {user.email}: {str(e)}")

if __name__ == "__main__":
    asyncio.run(migrate_users())
```

### 2. From Supabase to Traditional

#### Step 1: Set up Traditional Database
1. Set up PostgreSQL database
2. Configure environment variables for traditional setup
3. Run Alembic migrations

#### Step 2: Export Supabase Data
```python
# export_from_supabase.py
from core.supabase import supabase_client

def export_users():
    # Get all profiles from Supabase
    response = supabase_client.service_client.table('profiles').select('*').execute()
    
    # Save to JSON for manual import
    import json
    with open('supabase_users_export.json', 'w') as f:
        json.dump(response.data, f, indent=2)
    
    print(f"Exported {len(response.data)} users")

if __name__ == "__main__":
    export_users()
```

#### Step 3: Switch Configuration
```bash
USE_SUPABASE_AUTH=false  # Switch back to traditional auth
```

### 3. Hybrid Setup (Both Systems)

You can run both systems simultaneously by:

1. Keep both database configurations
2. Use different endpoints for different auth methods
3. Allow users to choose their preferred auth method

## API Endpoint Mapping

| Feature | Traditional | Supabase |
|---------|------------|----------|
| Register | `POST /api/v1/auth/register` | `POST /api/v1/auth/supabase/register` |
| Login | `POST /api/v1/auth/login` | `POST /api/v1/auth/supabase/login` |
| Logout | `POST /api/v1/auth/logout` | `POST /api/v1/auth/supabase/logout` |
| Profile | `GET /api/v1/users/me` | `GET /api/v1/auth/supabase/me` |
| Update | `PUT /api/v1/users/me` | `PUT /api/v1/auth/supabase/profile` |

## Key Differences

### Authentication
- **Traditional**: Custom JWT tokens, manual password hashing
- **Supabase**: Built-in auth with email verification, password reset, etc.

### Database
- **Traditional**: SQLAlchemy ORM with Alembic migrations
- **Supabase**: Direct SQL with Row Level Security policies

### File Storage
- **Traditional**: Local file system or S3-compatible storage
- **Supabase**: Built-in storage with automatic CDN

### Real-time Features
- **Traditional**: Would need WebSocket implementation
- **Supabase**: Built-in real-time subscriptions

## Benefits of Each Approach

### Traditional PostgreSQL
- ✅ Full control over database schema
- ✅ Custom business logic
- ✅ No vendor lock-in
- ✅ Works offline
- ❌ More setup and maintenance
- ❌ Need to implement auth features manually

### Supabase
- ✅ Rapid development
- ✅ Built-in auth, storage, real-time
- ✅ Automatic API generation
- ✅ Row Level Security
- ✅ Dashboard for data management
- ❌ Vendor lock-in
- ❌ Less control over infrastructure
- ❌ Internet connection required

## Best Practices

1. **Start with Traditional** if you have complex business logic
2. **Start with Supabase** if you want to move fast and don't need complex customization
3. **Use Hybrid** during migration periods
4. **Always backup** before switching systems
5. **Test thoroughly** in development before switching production systems

## Environment Variables Reference

```bash
# Traditional PostgreSQL
POSTGRES_SERVER=localhost
POSTGRES_PORT=5432
POSTGRES_USER=your_username
POSTGRES_PASSWORD=your_password
POSTGRES_DB=team_ai_db

# Supabase
SUPABASE_URL=https://your-project-ref.supabase.co
SUPABASE_ANON_KEY=your-anon-key-here
SUPABASE_SERVICE_KEY=your-service-role-key-here

# Control which system to use
USE_SUPABASE_AUTH=false  # true for Supabase, false for traditional
```
