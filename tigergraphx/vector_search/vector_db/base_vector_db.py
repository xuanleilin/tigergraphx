from abc import ABC, abstractmethod
from typing import List
import pandas as pd

from tigergraphx.config import BaseVectorDBConfig


class BaseVectorDB(ABC):
    """Abstract base class for managing vector database connections."""

    def __init__(self, config: BaseVectorDBConfig):
        """
        Initialize the vector database connection.

        Args:
            config: Configuration for the vector DB connection.
        """
        self.config = config

    @abstractmethod
    def insert_data(self, data: pd.DataFrame) -> None:
        """
        Insert data into the vector database.

        Args:
            data: The data to insert.
        """
        pass

    @abstractmethod
    def query(
        self,
        query_embedding: List[float],
        k: int = 10,
    ) -> List[str]:
        """
        Perform a similarity search and return matching IDs.

        Args:
            query_embedding: The vector to search with.
            k: Number of nearest neighbors to return.

        Returns:
            List of result IDs.
        """
        pass
