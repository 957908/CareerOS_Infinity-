import logging
from typing import List, Tuple, Any
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("app.core.vector_store")

class VectorStore:
    """
    Vector search execution helpers binding to pgvector columns inside PostgreSQL.
    """
    @staticmethod
    async def get_similar_items(
        session: AsyncSession,
        table_name: str,
        embedding_column: str,
        query_embedding: List[float],
        limit: int = 10,
        threshold: float = 0.5
    ) -> List[Tuple[str, float]]:
        """
        Calculates cosine similarity distance matching on vector tables using pgvector <=> operator.
        """
        logger.info(f"VectorStore: executing semantic similarity query on: {table_name}")
        
        # pgvector uses <=> operator for cosine distance. 
        # Cosine Similarity is 1 - Cosine Distance.
        # Query maps the select ordering by distance.
        query_sql = text(f"""
            SELECT id, 1 - ({embedding_column} <=> :query_vector) as similarity
            FROM {table_name}
            WHERE 1 - ({embedding_column} <=> :query_vector) >= :threshold
            ORDER BY {embedding_column} <=> :query_vector
            LIMIT :limit
        """)
        
        # Bind vector input representation (must format as standard pg float array string)
        vector_str = "[" + ",".join(map(str, query_embedding)) + "]"
        
        result = await session.execute(
            query_sql,
            {"query_vector": vector_str, "threshold": threshold, "limit": limit}
        )
        
        rows = result.fetchall()
        return [(str(row[0]), float(row[1])) for row in rows]
