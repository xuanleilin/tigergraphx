from typing import Dict, Any
from pydantic import Field, field_validator

from ..base_config import BaseConfig
from .vector_db_settings import BaseVectorDBConfig, LanceDBConfig
from .llm_settings import BaseLLMConfig, OpenAIConfig
from .embedding_settings import BaseEmbeddingConfig, OpenAIEmbeddingConfig
from .chat_settings import BaseChatConfig, OpenAIChatConfig


class Settings(BaseConfig):
    """
    Application settings, including configurations for vector databases, LLMs,
    embeddings, and chat models.
    """

    vector_db: LanceDBConfig | BaseVectorDBConfig = Field(
        description="Configuration for the vector database."
    )
    llm: OpenAIConfig | BaseLLMConfig = Field(
        description="Configuration for the language model."
    )
    embedding: OpenAIEmbeddingConfig | BaseEmbeddingConfig = Field(
        description="Configuration for the embedding model."
    )
    chat: OpenAIChatConfig | BaseChatConfig = Field(
        description="Configuration for the chat model."
    )

    @field_validator("vector_db", mode="before")
    @classmethod
    def validate_vector_db(cls, value: Dict[str, Any]) -> BaseVectorDBConfig:
        """
        Validate and instantiate the vector_db field.

        Args:
            value (Dict[str, Any]): The input configuration for the vector database.

        Returns:
            BaseVectorDBConfig: The instantiated configuration.

        Raises:
            ValueError: If the type of vector database is unknown.
        """
        type_map = {"LanceDB": LanceDBConfig}
        db_type = value.get("type")
        if db_type not in type_map:
            raise ValueError(f"Unknown vector_db type: {db_type}")
        return type_map[db_type](**value)

    @field_validator("llm", mode="before")
    @classmethod
    def validate_llm(cls, value: Dict[str, Any]) -> BaseLLMConfig:
        """
        Validate and instantiate the llm field.

        Args:
            value (Dict[str, Any]): The input configuration for the language model.

        Returns:
            BaseLLMConfig: The instantiated configuration.

        Raises:
            ValueError: If the type of language model is unknown.
        """
        type_map = {"OpenAI": OpenAIConfig}
        llm_type = value.get("type")
        if llm_type not in type_map:
            raise ValueError(f"Unknown llm type: {llm_type}")
        return type_map[llm_type](**value)

    @field_validator("embedding", mode="before")
    @classmethod
    def validate_embedding(cls, value: Dict[str, Any]) -> BaseEmbeddingConfig:
        """
        Validate and instantiate the embedding field.

        Args:
            value (Dict[str, Any]): The input configuration for the embedding model.

        Returns:
            BaseEmbeddingConfig: The instantiated configuration.

        Raises:
            ValueError: If the type of embedding model is unknown.
        """
        type_map = {"OpenAI": OpenAIEmbeddingConfig}
        embed_type = value.get("type")
        if embed_type not in type_map:
            raise ValueError(f"Unknown embedding type: {embed_type}")
        return type_map[embed_type](**value)

    @field_validator("chat", mode="before")
    @classmethod
    def validate_chat(cls, value: Dict[str, Any]) -> BaseChatConfig:
        """
        Validate and instantiate the chat field.

        Args:
            value (Dict[str, Any]): The input configuration for the chat model.

        Returns:
            BaseChatConfig: The instantiated configuration.

        Raises:
            ValueError: If the type of chat model is unknown.
        """
        type_map = {"OpenAI": OpenAIChatConfig}
        chat_type = value.get("type")
        if chat_type not in type_map:
            raise ValueError(f"Unknown chat type: {chat_type}")
        return type_map[chat_type](**value)
