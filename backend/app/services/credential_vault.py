import logging
import base64
import hashlib
import json
from cryptography.fernet import Fernet
from app.core.config import settings
from app.repositories.graph_repository import PostgreSQLGraphRepository
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("app.services.credential_vault")

class CredentialVault:
    """
    Symmetric Cryptographic Vault managing secure storage and retrieval 
    of external portal usernames and passwords.
    """
    @staticmethod
    def _get_cipher() -> Fernet:
        # Derive a secure 32-byte key from the SECRET_KEY setting using SHA-256
        key_source = settings.SECRET_KEY.encode("utf-8")
        key_hash = hashlib.sha256(key_source).digest()
        fernet_key = base64.urlsafe_b64encode(key_hash)
        return Fernet(fernet_key)

    @classmethod
    def encrypt_password(cls, password: str) -> str:
        cipher = cls._get_cipher()
        encrypted_bytes = cipher.encrypt(password.encode("utf-8"))
        return encrypted_bytes.decode("utf-8")

    @classmethod
    def decrypt_password(cls, encrypted_password: str) -> str:
        cipher = cls._get_cipher()
        decrypted_bytes = cipher.decrypt(encrypted_password.encode("utf-8"))
        return decrypted_bytes.decode("utf-8")

    @classmethod
    async def save_portal_credentials(
        cls,
        session: AsyncSession,
        portal_name: str,
        username: str,
        password: str
    ) -> None:
        logger.info(f"CredentialVault: encrypting and saving credentials for portal: {portal_name}")
        graph_repo = PostgreSQLGraphRepository(session)
        
        node_id = f"credential:{portal_name.lower().strip()}"
        encrypted_pass = cls.encrypt_password(password)
        
        properties = {
            "portal": portal_name,
            "username": username,
            "encrypted_password": encrypted_pass
        }
        
        await graph_repo.add_entity_node(
            node_id=node_id,
            entity_type="CREDENTIAL",
            properties=properties
        )
        await session.commit()

    @classmethod
    async def get_portal_credentials(
        cls,
        session: AsyncSession,
        portal_name: str
    ) -> dict:
        logger.info(f"CredentialVault: retrieving credentials for portal: {portal_name}")
        graph_repo = PostgreSQLGraphRepository(session)
        
        node_id = f"credential:{portal_name.lower().strip()}"
        node = await graph_repo.get_entity_node(node_id)
        if not node:
            return {}
            
        props = dict(node.properties)
        try:
            decrypted_pass = cls.decrypt_password(props["encrypted_password"])
            return {
                "portal": props["portal"],
                "username": props["username"],
                "password": decrypted_pass
            }
        except Exception as e:
            logger.error(f"CredentialVault: decryption failed for portal {portal_name}: {e}")
            return {}

    @classmethod
    async def get_all_stored_usernames(
        cls,
        session: AsyncSession
    ) -> dict:
        logger.info("CredentialVault: listing stored portal usernames")
        graph_repo = PostgreSQLGraphRepository(session)
        nodes = await graph_repo.get_entities_by_type("CREDENTIAL")
        
        results = {}
        for node in nodes:
            props = dict(node.properties)
            results[props["portal"].lower()] = props["username"]
        return results
