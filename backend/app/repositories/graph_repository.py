import abc
import logging
from typing import List, Tuple, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pgvector.sqlalchemy import Vector
from app.models.graph import GraphNode, GraphRelationship

logger = logging.getLogger("app.repositories.graph_repository")

class IGraphRepository(abc.ABC):
    """
    Strategic Provider-Independent Interface defining Knowledge Graph operations.
    Keeps query languages (Cypher, Gremlin, pgvector SQL) isolated inside infrastructure adapters.
    """
    @abc.abstractmethod
    async def add_entity_node(
        self,
        node_id: str,
        entity_type: str,
        properties: dict,
        embedding: Optional[List[float]] = None
    ) -> None:
        pass

    @abc.abstractmethod
    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: dict
    ) -> None:
        pass

    @abc.abstractmethod
    async def get_similar_nodes(
        self,
        query_embedding: List[float],
        limit: int = 10,
        threshold: float = 0.5
    ) -> List[Tuple[str, float]]:
        pass

    @abc.abstractmethod
    async def get_entities_by_type(self, entity_type: str) -> List[GraphNode]:
        pass


class PostgreSQLGraphRepository(IGraphRepository):
    """
    Concrete PostgreSQL graph repository implementing pgvector similarity query lookups.
    """
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_entities_by_type(self, entity_type: str) -> List[GraphNode]:
        logger.info(f"PostgreSQLGraphRepository: fetching nodes of type {entity_type}")
        query = select(GraphNode).filter(GraphNode.entity_type == entity_type)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def add_entity_node(
        self,
        node_id: str,
        entity_type: str,
        properties: dict,
        embedding: Optional[List[float]] = None
    ) -> None:
        logger.info(f"PostgreSQLGraphRepository: upserting node ID: {node_id} ({entity_type})")
        
        # Check if node already exists
        query = select(GraphNode).filter(GraphNode.id == node_id)
        result = await self.session.execute(query)
        node = result.scalars().first()
        
        if node:
            node.properties.update(properties)
            if embedding:
                node.embedding = embedding
        else:
            node = GraphNode(
                id=node_id,
                entity_type=entity_type,
                properties=properties,
                embedding=embedding
            )
            self.session.add(node)
        await self.session.flush()

    async def add_relationship(
        self,
        source_id: str,
        target_id: str,
        relation_type: str,
        properties: dict
    ) -> None:
        logger.info(f"PostgreSQLGraphRepository: adding edge {source_id} -[{relation_type}]-> {target_id}")
        
        # Verify if relationship already exists
        query = select(GraphRelationship).filter(
            GraphRelationship.source_id == source_id,
            GraphRelationship.target_id == target_id,
            GraphRelationship.relation_type == relation_type
        )
        result = await self.session.execute(query)
        rel = result.scalars().first()
        
        if rel:
            rel.properties.update(properties)
        else:
            rel = GraphRelationship(
                source_id=source_id,
                target_id=target_id,
                relation_type=relation_type,
                properties=properties
            )
            self.session.add(rel)
        await self.session.flush()

    async def get_similar_nodes(
        self,
        query_embedding: List[float],
        limit: int = 10,
        threshold: float = 0.5
    ) -> List[Tuple[str, float]]:
        logger.info("PostgreSQLGraphRepository: executing pgvector similarity search.")
        # pgvector cosine distance operator is <=>
        query = select(
            GraphNode.id,
            (1 - GraphNode.embedding.cosine_distance(query_embedding)).label("similarity")
        ).filter(
            (1 - GraphNode.embedding.cosine_distance(query_embedding)) >= threshold
        ).order_by(
            GraphNode.embedding.cosine_distance(query_embedding)
        ).limit(limit)
        
        result = await self.session.execute(query)
        rows = result.all()
        return [(str(row[0]), float(row[1])) for row in rows]
