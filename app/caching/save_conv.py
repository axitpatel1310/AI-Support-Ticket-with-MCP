import sqlite3

def save_message(conversation_id, role, content):
    conn = sqlite3.connect("db.sqlite")

    conn.execute(
        """
        INSERT INTO messages
        (conversation_id, role, content)
        VALUES (?, ?, ?)
        """,
        (conversation_id, role, content)
    )

    conn.execute(
        """
        UPDATE conversations
        SET last_activity = CURRENT_TIMESTAMP
        WHERE id = ?
        """,
        (conversation_id,)
    )

    conn.commit()
    conn.close()
    
def create_conversation(user_id):
    conn = sqlite3.connect("db.sqlite")

    cursor = conn.execute(
        """
        INSERT INTO conversations (user_id)
        VALUES (?)
        """,
        (user_id,)
    )

    conversation_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return conversation_id