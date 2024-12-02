import logging
from typing import Optional, Dict, List
import pandas as pd

from tigergraphx.config import (
    TigerGraphConnectionConfig,
    GraphSchema,
    LoadingJobConfig,
    NodeSpec,
    NeighborSpec,
)
from tigergraphx.core.graph_context import GraphContext
from tigergraphx.core.gsql import (
    CREATE_QUERY_API_DEGREE,
    CREATE_QUERY_API_GET_NODE_EDGES,
)
from tigergraphx.core.managers import (
    NodeManager,
    EdgeManager,
    QueryManager,
    SchemaManager,
    StatisticsManager,
    DataManager,
)

logger = logging.getLogger(__name__)


class BaseGraph:
    def __init__(
        self,
        graph_schema: GraphSchema,
        tigergraph_connection_config: Optional[TigerGraphConnectionConfig] = None,
        drop_existing_graph: bool = False,
    ):
        # Set graph name
        self.name = graph_schema.graph_name

        # Initialize the graph context with the provided schema and connection config
        self._context = GraphContext(
            graph_schema=graph_schema,
            tigergraph_connection_config=tigergraph_connection_config,
        )
        self.node_type = self._context.node_type
        self.edge_type = self._context.edge_type

        # Initialize managers for handling different aspects of the graph
        self._schema_manager = SchemaManager(self._context)
        self._data_manager = DataManager(self._context)
        self._node_manager = NodeManager(self._context)
        self._edge_manager = EdgeManager(self._context)
        self._statistics_manager = StatisticsManager(self._context)
        self._query_manager = QueryManager(self._context)

        # Create the schema, drop the graph first if drop_existing_graph is True
        schema_is_created = self._schema_manager.create_schema(
            drop_existing_graph=drop_existing_graph
        )

        # Install queries
        if schema_is_created:
            gsql_script = self._create_gsql_install_queries(self.name)
            result = self._context.connection.gsql(gsql_script)
            if "Saved as draft query with type/semantic error" in result:
                error_msg = f"Query type/semantic error. GSQL response: {result}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

    # ------------------------------ Category 1: Schema Operations ------------------------------
    def create_schema(self, drop_existing_graph=False) -> bool:
        return self._schema_manager.create_schema(drop_existing_graph)

    # ------------------------------ Category 2: Data Loading Operations ------------------------------
    def load_data(self, loading_job_config: LoadingJobConfig):
        return self._data_manager.load_data(loading_job_config)

    # ------------------------------ Category 3: Node Operations ------------------------------
    def _add_node(self, node_id: str, node_type: str, **attr):
        return self._node_manager.add_node(node_id, node_type, **attr)

    def _has_node(self, node_id: str, node_type: str) -> bool:
        return self._node_manager.has_node(node_id, node_type)

    def _get_node_data(self, node_id: str, node_type: str) -> Dict:
        return self._node_manager.get_node_data(node_id, node_type)

    def _get_node_edges(
        self,
        node_id: str,
        node_type: str,
        edge_types: List | str,
        num_edge_samples: int = 1000,
    ) -> List:
        return self._node_manager.get_node_edges(
            node_id, node_type, edge_types, num_edge_samples
        )

    # ------------------------------ Category 4: Edge Operations ------------------------------
    def _add_edge(
        self,
        src_node_id: str,
        tgt_node_id: str,
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
        **attr,
    ):
        return self._edge_manager.add_edge(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type, **attr
        )

    def _has_edge(
        self,
        src_node_id: str | int,
        tgt_node_id: str | int,
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
    ) -> bool:
        return self._edge_manager.has_edge(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

    def _get_edge_data(
        self,
        src_node_id: str,
        tgt_node_id: str,
        src_node_type: str,
        edge_type: str,
        tgt_node_type: str,
    ) -> Dict:
        return self._edge_manager.get_edge_data(
            src_node_id, tgt_node_id, src_node_type, edge_type, tgt_node_type
        )

    # ------------------------------ Category 5: Statistics Operations ------------------------------
    def _degree(self, node_id: str, node_type: str, edge_types: List | str) -> int:
        return self._statistics_manager.degree(node_id, node_type, edge_types)

    # ------------------------------ Category 6: Query Operations ------------------------------
    def run_query(self, query_name: str, params: Dict = {}):
        return self._query_manager.run_query(query_name, params)

    def _get_nodes(
        self,
        node_type: str,
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame | None:
        return self._query_manager.get_nodes(
            node_type, filter_expression, return_attributes, limit
        )

    def _get_nodes_from_spec(self, spec: NodeSpec) -> pd.DataFrame | None:
        return self._query_manager.get_nodes_from_spec(spec)

    def _get_neighbors(
        self,
        start_nodes: str | List[str],
        start_node_type: str,
        edge_types: Optional[str | List[str]] = None,
        target_node_types: Optional[str | List[str]] = None,
        filter_expression: Optional[str] = None,
        return_attributes: Optional[str | List[str]] = None,
        limit: Optional[int] = None,
    ) -> pd.DataFrame | None:
        return self._query_manager.get_neighbors(
            start_nodes=start_nodes,
            start_node_type=start_node_type,
            edge_types=edge_types,
            target_node_types=target_node_types,
            filter_expression=filter_expression,
            return_attributes=return_attributes,
            limit=limit,
        )

    def _get_neighbors_from_spec(self, spec: NeighborSpec) -> pd.DataFrame | None:
        return self._query_manager.get_neighbors_from_spec(spec)

    # ------------------------------ Utilities ------------------------------
    @staticmethod
    def _create_gsql_install_queries(graph_name: str):
        gsql_script = f"""
USE GRAPH {graph_name}
{CREATE_QUERY_API_DEGREE}
{CREATE_QUERY_API_GET_NODE_EDGES}
INSTALL QUERY *
"""
        return gsql_script.strip()