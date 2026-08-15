import logging
from typing import Optional, Dict, Any
import litellm
from litellm import completion
from app.core.config import settings

logger = logging.getLogger("app.core.ai_gateway")

class AIGateway:
    """
    Unified AI Gateway orchestrating model routing and provider exceptions fallbacks.
    """
    @staticmethod
    async def generate_response(
        messages: list,
        model: str = "gemini/gemini-3.5-flash",
        fallback_model: Optional[str] = "gemini/gemini-3.5-flash-lite",
        temperature: float = 0.2,
        max_tokens: int = 1500
    ) -> str:
        logger.info(f"AIGateway: routing prompt to model: {model}")
        kwargs = {}
        if settings.GEMINI_API_KEY:
            kwargs["api_key"] = settings.GEMINI_API_KEY

        try:
            # Route completion query
            response = completion(
                model=model,
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            text = response.choices[0].message.content
            logger.info("AIGateway: completion succeeded.")
            return text
        except Exception as e:
            logger.error(f"AIGateway: primary model {model} failed: {e}. Executing fallback.")
            if fallback_model:
                try:
                    response = completion(
                        model=fallback_model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens
                    )
                    text = response.choices[0].message.content
                    logger.info(f"AIGateway: fallback model {fallback_model} succeeded.")
                    return text
                except Exception as fe:
                    logger.critical(f"AIGateway: fallback model failed: {fe}")
                    raise RuntimeError("AI service failed to respond.") from fe
            raise RuntimeError("AI primary provider failed with no fallbacks configured.") from e

    @staticmethod
    async def generate_embeddings(
        text: str,
        model: str = "gemini/text-embedding-004"
    ) -> list[float]:
        """
        Generates semantic dimensions embeddings list for pgvector indexing.
        """
        logger.info(f"AIGateway: generating text embeddings using model: {model}")
        kwargs = {}
        if settings.GEMINI_API_KEY:
            kwargs["api_key"] = settings.GEMINI_API_KEY

        try:
            response = litellm.embedding(
                model=model,
                input=[text],
                **kwargs
            )
            embeddings = response['data'][0]['embedding']
            return embeddings
        except Exception as e:
            logger.error(f"AIGateway: embedding generation failed ({e}), returning default zero-vector.")
            return [0.0] * 1536
