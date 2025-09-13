"""
Database service for persistent data storage.
"""

import sqlite3
import asyncio
import aiosqlite
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import json
from config.settings import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class DatabaseService:
    """Service for database operations using SQLite."""

    def __init__(self, database_url: Optional[str] = None):
        self.database_url = database_url or settings.DATABASE_URL
        # Extract database path from URL
        if self.database_url.startswith("sqlite:///"):
            self.db_path = self.database_url.replace("sqlite:///", "")
        else:
            self.db_path = "ai_agents.db"

        self._initialized = False

    async def initialize(self) -> None:
        """Initialize the database and create tables."""
        if self._initialized:
            return

        try:
            async with aiosqlite.connect(self.db_path) as db:
                await self._create_tables(db)
                await db.commit()

            self._initialized = True
            logger.info(f"Database initialized at {self.db_path}")

        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    async def _create_tables(self, db: aiosqlite.Connection) -> None:
        """Create necessary database tables."""
        # Conversations table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS conversations (
                id TEXT PRIMARY KEY,
                agent_name TEXT NOT NULL,
                user_id TEXT,
                session_id TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """
        )

        # Messages table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id TEXT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT,
                FOREIGN KEY (conversation_id) REFERENCES conversations (id)
            )
        """
        )

        # Agent states table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_states (
                id TEXT PRIMARY KEY,
                agent_name TEXT NOT NULL,
                session_id TEXT,
                state_data TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # User preferences table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS user_preferences (
                user_id TEXT PRIMARY KEY,
                preferences TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )

        # Agent logs table
        await db.execute(
            """
            CREATE TABLE IF NOT EXISTS agent_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT NOT NULL,
                log_level TEXT NOT NULL,
                message TEXT NOT NULL,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                metadata TEXT
            )
        """
        )

    async def create_conversation(
        self,
        agent_name: str,
        user_id: Optional[str] = None,
        session_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """
        Create a new conversation record.

        Args:
            agent_name: Name of the agent
            user_id: Optional user identifier
            session_id: Optional session identifier
            metadata: Optional metadata dictionary

        Returns:
            Conversation ID
        """
        await self.initialize()

        conversation_id = (
            f"conv_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{agent_name}"
        )

        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO conversations (id, agent_name, user_id, session_id, metadata)
                    VALUES (?, ?, ?, ?, ?)
                """,
                    (
                        conversation_id,
                        agent_name,
                        user_id,
                        session_id,
                        json.dumps(metadata) if metadata else None,
                    ),
                )
                await db.commit()

            logger.info(
                f"Created conversation {conversation_id} for agent {agent_name}"
            )
            return conversation_id

        except Exception as e:
            logger.error(f"Failed to create conversation: {e}")
            raise

    async def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        """
        Add a message to a conversation.

        Args:
            conversation_id: Conversation identifier
            role: Message role (user, assistant, system)
            content: Message content
            metadata: Optional metadata dictionary

        Returns:
            Message ID
        """
        await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    """
                    INSERT INTO messages (conversation_id, role, content, metadata)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        conversation_id,
                        role,
                        content,
                        json.dumps(metadata) if metadata else None,
                    ),
                )
                await db.commit()
                return cursor.lastrowid

        except Exception as e:
            logger.error(
                f"Failed to add message to conversation {conversation_id}: {e}"
            )
            raise

    async def get_conversation_messages(
        self, conversation_id: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get messages for a conversation.

        Args:
            conversation_id: Conversation identifier
            limit: Optional limit on number of messages

        Returns:
            List of message dictionaries
        """
        await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                query = """
                    SELECT id, role, content, timestamp, metadata
                    FROM messages
                    WHERE conversation_id = ?
                    ORDER BY timestamp ASC
                """

                if limit:
                    query += f" LIMIT {limit}"

                cursor = await db.execute(query, (conversation_id,))
                rows = await cursor.fetchall()

                messages = []
                for row in rows:
                    message = {
                        "id": row[0],
                        "role": row[1],
                        "content": row[2],
                        "timestamp": row[3],
                        "metadata": json.loads(row[4]) if row[4] else None,
                    }
                    messages.append(message)

                return messages

        except Exception as e:
            logger.error(
                f"Failed to get messages for conversation {conversation_id}: {e}"
            )
            raise

    async def save_agent_state(
        self, agent_name: str, session_id: str, state_data: Dict[str, Any]
    ) -> None:
        """
        Save agent state to database.

        Args:
            agent_name: Name of the agent
            session_id: Session identifier
            state_data: State data dictionary
        """
        await self.initialize()

        state_id = f"{agent_name}_{session_id}"

        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT OR REPLACE INTO agent_states 
                    (id, agent_name, session_id, state_data, updated_at)
                    VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
                """,
                    (state_id, agent_name, session_id, json.dumps(state_data)),
                )
                await db.commit()

        except Exception as e:
            logger.error(f"Failed to save agent state for {agent_name}: {e}")
            raise

    async def load_agent_state(
        self, agent_name: str, session_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Load agent state from database.

        Args:
            agent_name: Name of the agent
            session_id: Session identifier

        Returns:
            State data dictionary or None if not found
        """
        await self.initialize()

        state_id = f"{agent_name}_{session_id}"

        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    """
                    SELECT state_data FROM agent_states
                    WHERE id = ?
                """,
                    (state_id,),
                )

                row = await cursor.fetchone()
                if row:
                    return json.loads(row[0])

                return None

        except Exception as e:
            logger.error(f"Failed to load agent state for {agent_name}: {e}")
            raise

    async def save_user_preferences(
        self, user_id: str, preferences: Dict[str, Any]
    ) -> None:
        """
        Save user preferences.

        Args:
            user_id: User identifier
            preferences: Preferences dictionary
        """
        await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT OR REPLACE INTO user_preferences 
                    (user_id, preferences, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                """,
                    (user_id, json.dumps(preferences)),
                )
                await db.commit()

        except Exception as e:
            logger.error(f"Failed to save preferences for user {user_id}: {e}")
            raise

    async def get_user_preferences(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Get user preferences.

        Args:
            user_id: User identifier

        Returns:
            Preferences dictionary or None if not found
        """
        await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                cursor = await db.execute(
                    """
                    SELECT preferences FROM user_preferences
                    WHERE user_id = ?
                """,
                    (user_id,),
                )

                row = await cursor.fetchone()
                if row:
                    return json.loads(row[0])

                return None

        except Exception as e:
            logger.error(f"Failed to get preferences for user {user_id}: {e}")
            raise

    async def log_agent_activity(
        self,
        agent_name: str,
        log_level: str,
        message: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Log agent activity to database.

        Args:
            agent_name: Name of the agent
            log_level: Log level (INFO, WARNING, ERROR, etc.)
            message: Log message
            metadata: Optional metadata
        """
        await self.initialize()

        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    """
                    INSERT INTO agent_logs (agent_name, log_level, message, metadata)
                    VALUES (?, ?, ?, ?)
                """,
                    (
                        agent_name,
                        log_level,
                        message,
                        json.dumps(metadata) if metadata else None,
                    ),
                )
                await db.commit()

        except Exception as e:
            logger.error(f"Failed to log activity for agent {agent_name}: {e}")

    async def cleanup_old_data(self, days: int = 30) -> Dict[str, int]:
        """
        Clean up old data from the database.

        Args:
            days: Number of days to keep

        Returns:
            Dictionary with cleanup statistics
        """
        await self.initialize()

        cutoff_date = datetime.now().timestamp() - (days * 24 * 3600)

        try:
            async with aiosqlite.connect(self.db_path) as db:
                # Clean up old conversations and their messages
                cursor = await db.execute(
                    """
                    DELETE FROM conversations 
                    WHERE created_at < datetime(?, 'unixepoch')
                """,
                    (cutoff_date,),
                )

                conversations_deleted = cursor.rowcount

                # Clean up old agent logs
                cursor = await db.execute(
                    """
                    DELETE FROM agent_logs 
                    WHERE timestamp < datetime(?, 'unixepoch')
                """,
                    (cutoff_date,),
                )

                logs_deleted = cursor.rowcount

                await db.commit()

                logger.info(
                    f"Cleanup completed: {conversations_deleted} conversations, {logs_deleted} logs deleted"
                )

                return {
                    "conversations_deleted": conversations_deleted,
                    "logs_deleted": logs_deleted,
                }

        except Exception as e:
            logger.error(f"Failed to cleanup old data: {e}")
            raise


# Global database service instance
database_service = DatabaseService()
