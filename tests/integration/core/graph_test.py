import pytest
import time
import json
from typing import Dict

from .base_graph_test import TestBaseGraph

from tigergraphx.core import Graph
from tigergraphx.core.view.node_view import NodeView


class TestGraph1(TestBaseGraph):
    def setup_graph(self):
        """Set up the graph and add nodes and edges."""
        graph_schema = {
            "graph_name": "UserProductGraph",
            "nodes": {
                "User": {
                    "primary_key": "id",
                    "attributes": {
                        "id": "STRING",
                        "name": "STRING",
                        "age": "UINT",
                    },
                },
                "Product": {
                    "primary_key": "id",
                    "attributes": {
                        "id": "STRING",
                        "name": "STRING",
                        "price": "DOUBLE",
                    },
                },
            },
            "edges": {
                "purchased": {
                    "is_directed_edge": True,
                    "from_node_type": "User",
                    "to_node_type": "Product",
                    "attributes": {
                        "purchase_date": "DATETIME",
                        "quantity": "DOUBLE",
                    },
                },
                "similar_to": {
                    "is_directed_edge": False,
                    "from_node_type": "Product",
                    "to_node_type": "Product",
                    "attributes": {
                        "purchase_date": "DATETIME",
                        "quantity": "DOUBLE",
                    },
                },
            },
        }
        self.G = Graph(graph_schema=graph_schema)

    @pytest.fixture(autouse=True)
    def add_nodes_and_edges(self):
        """Add nodes and edges before each test case."""
        # Initialize the graph
        self.setup_graph()

        # Adding nodes and edges
        self.G.add_node("User_A", "User")
        self.G.add_node("User_B", "User", name="B")
        self.G.add_node("User_C", "User", name="C", age=30)
        self.G.add_node("Product_1", "Product")
        self.G.add_node("Product_2", "Product", name="2")
        self.G.add_node("Product_3", "Product", name="3", price=50)
        self.G.add_edge("User_A", "Product_1", "User", "purchased", "Product")
        self.G.add_edge(
            "User_B",
            "Product_2",
            "User",
            "purchased",
            "Product",
            purchase_date="2024-01-12",
        )
        self.G.add_edge(
            "User_C",
            "Product_1",
            "User",
            "purchased",
            "Product",
            purchase_date="2024-01-12",
            quantity=5.5,
        )
        self.G.add_edge(
            "User_C",
            "Product_2",
            "User",
            "purchased",
            "Product",
            purchase_date="2024-01-12",
            quantity=15.5,
        )
        ebunch_to_add = [
            ("User_C", "Product_3", {"purchase_date": "2024-01-12", "quantity": 25.5})
        ]
        self.G.add_edges_from(
            ebunch_to_add,
            "User",
            "purchased",
            "Product",
        )
        ebunch_to_add = [("Product_1", "Product_3")]
        self.G.add_edges_from(
            ebunch_to_add,
            "Product",
            "similar_to",
            "Product",
        )
        time.sleep(1)

        yield  # The test case runs here

        self.G.clear()

    @pytest.fixture(scope="class", autouse=True)
    def drop_graph(self):
        """Drop the graph after all tests are done in the session."""
        yield
        self.setup_graph()
        self.G.drop_graph()

    # ------------------------------ NodeView Property ------------------------------
    def test_nodes_property(self):
        # Access the nodes property
        nodes_view = self.G.nodes
        # Verify that it returns a NodeView instance
        assert isinstance(nodes_view, NodeView), "Expected a NodeView instance."
        # Check __getitem__ method
        user_c_data = nodes_view[("User", "User_C")]
        assert (
            user_c_data["name"] == "C"
        ), f"Expected name 'C', got {user_c_data['name']}"
        assert user_c_data["age"] == 30, f"Expected age 30, got {user_c_data['age']}"
        # Check __contains__ method
        assert ("User", "User_A") in nodes_view, "Expected 'User_A' to be in nodes_view"
        assert (
            "User",
            "User_D",
        ) not in nodes_view, "Expected 'User_D' to not be in nodes_view"
        # Check __iter__ method
        node_ids = {node for node in nodes_view}
        expected_ids = {
            ("User", "User_A"),
            ("User", "User_B"),
            ("User", "User_C"),
            ("Product", "Product_1"),
            ("Product", "Product_2"),
            ("Product", "Product_3"),
        }
        assert (
            node_ids == expected_ids
        ), f"Expected node ids {expected_ids}, got {node_ids}"
        # Check __len__ method (already tested)
        assert len(nodes_view) == 6, f"Expected 6 nodes, got {len(nodes_view)}"

    # ------------------------------ Node Operations ------------------------------
    def test_add_node_without_type(self):
        with pytest.raises(
            ValueError,
            match="Multiple node types detected. Please specify a node type.",
        ):
            self.G.add_node("D", "")

    def test_has_nodes(self):
        # Test node existence
        assert self.G.has_node("User_A", "User")
        assert self.G.has_node("User_B", "User")
        assert self.G.has_node("User_C", "User")
        assert self.G.has_node("Product_1", "Product")
        assert self.G.has_node("Product_2", "Product")
        assert self.G.has_node("Product_3", "Product")
        assert not self.G.has_node("User_D", "User")

    def test_has_node_without_type(self):
        with pytest.raises(
            ValueError,
            match="Multiple node types detected. Please specify a node type.",
        ):
            self.G.has_node("D", "")

    def test_get_node_data(self):
        # Test fetching node data
        node_data = self.time_execution(
            lambda: self.G.get_node_data("User_C", "User"), "get_node_data"
        )
        assert node_data["id"] == "User_C"
        assert node_data["name"] == "C"
        assert node_data["age"] == 30

    def test_get_node_edges(self):
        # Test fetching edges of a node
        node_edges = self.time_execution(
            lambda: self.G.get_node_edges("User_C", "User", "purchased"),
            "get_node_edges",
        )
        assert len(node_edges) == 3

    # ------------------------------ Edge Operations ------------------------------
    def test_add_edge_without_target_node_type(self):
        with pytest.raises(
            ValueError,
            match="Multiple node types detected. Please specify a node type.",
        ):
            self.G.add_edge("User_A", "Product_2", "User", "purchased", "")

    def test_add_edge_without_source_node_type(self):
        with pytest.raises(
            ValueError,
            match="Multiple node types detected. Please specify a node type.",
        ):
            self.G.add_edge("User_A", "Product_2", "", "purchased", "Product")

    def test_add_edge_without_edge_type(self):
        with pytest.raises(
            ValueError,
            match="Multiple edge types detected. Please specify an edge type.",
        ):
            self.G.add_edge("User_A", "Product_2", "User", "", "Product")

    def test_has_edges(self):
        # Test edge existence
        assert not self.G.has_edge(
            "User_A", "Product_2", "User", "purchased", "Product"
        )
        assert not self.G.has_edge(
            "User_A", "Product_3", "User", "purchased", "Product"
        )
        assert self.G.has_edge("User_C", "Product_1", "User", "purchased", "Product")
        assert self.G.has_edge("User_C", "Product_2", "User", "purchased", "Product")
        assert self.G.has_edge("User_C", "Product_3", "User", "purchased", "Product")

    def test_get_edge_data(self):
        # Test fetching edge data
        edge_data = self.time_execution(
            lambda: self.G.get_edge_data(
                "User_C", "Product_2", "User", "purchased", "Product"
            ),
            "get_edge_data",
        )
        assert edge_data["purchase_date"] == "2024-01-12 00:00:00"
        assert edge_data["quantity"] == 15.5

    # ------------------------------ Statistics Operations ------------------------------
    def test_degree(self):
        # Test degree calculations
        degree = self.time_execution(
            lambda: self.G.degree("Product_1", "Product", ["reverse_purchased"]),
            "degree",
        )
        assert degree == 2

        degree = self.time_execution(
            lambda: self.G.degree("Product_1", "Product", ["similar_to"]), "degree"
        )
        assert degree == 1

        degree = self.time_execution(
            lambda: self.G.degree(
                "Product_1", "Product", ["reverse_purchased", "similar_to"]
            ),
            "degree",
        )
        assert degree == 3

        degree = self.time_execution(
            lambda: self.G.degree("Product_1", "Product", []), "degree"
        )
        assert degree == 3

    def test_number_of_nodes(self):
        # Test number of nodes for specific node types
        num_user_nodes = self.G.number_of_nodes(node_type="User")
        assert num_user_nodes == 3, f"Expected 3 User nodes, got {num_user_nodes}"

        num_product_nodes = self.G.number_of_nodes(node_type="Product")
        assert (
            num_product_nodes == 3
        ), f"Expected 3 Product nodes, got {num_product_nodes}"

        # Test total number of nodes (without specifying node type)
        total_nodes = self.G.number_of_nodes()
        assert total_nodes == 6, f"Expected 6 total nodes, got {total_nodes}"

        # Test with an invalid node type
        with pytest.raises(ValueError, match="Invalid node type"):
            self.G.number_of_nodes(node_type="InvalidType")

    # ------------------------------ Query Operations ------------------------------
    def test_get_nodes(self):
        # Define the return attributes and test parameters
        return_attributes = ["id", "name", "age"]
        nodes = self.time_execution(
            lambda: self.G.get_nodes(
                node_type="User",
                filter_expression="s.age > 20",
                return_attributes=return_attributes,
                limit=10,
            ),
            "get_nodes",
        )

        # Assertions to verify the test output
        assert nodes is not None, "No nodes returned."
        assert len(nodes) <= 10, "Expected at most 10 nodes, but got more."
        assert set(nodes.columns) == set(
            return_attributes
        ), f"Expected columns {return_attributes}, but got {list(nodes.columns)}."

    def test_get_neighbors(self):
        # Define return attributes and test parameters
        return_attributes = ["id", "name", "price"]
        neighbors = self.time_execution(
            lambda: self.G.get_neighbors(
                start_nodes=["User_A", "User_B"],
                start_node_type="User",
                edge_types=["purchased"],
                target_node_types="Product",
                filter_expression="s.id != t.id",
                return_attributes=return_attributes,
                limit=5,
            ),
            "get_neighbors",
        )

        # Assertions to verify the test output
        assert neighbors is not None, "No neighbors returned."
        assert len(neighbors) <= 5, "Expected at most 5 neighbors, but got more."
        assert set(neighbors.columns) == set(
            return_attributes
        ), f"Expected columns {return_attributes}, but got {list(neighbors.columns)}."


class TestGraph2(TestBaseGraph):
    def setup_graph(self):
        """Set up the graph and add nodes and edges."""
        graph_schema = {
            "graph_name": "ERGraph",
            "nodes": {
                "Entity": {
                    "primary_key": "id",
                    "attributes": {
                        "id": "STRING",
                        "entity_type": "STRING",
                        "description": "STRING",
                        "source_id": "STRING",
                    },
                },
            },
            "edges": {
                "relationship": {
                    "is_directed_edge": True,
                    "from_node_type": "Entity",
                    "to_node_type": "Entity",
                    "attributes": {
                        "weight": "DOUBLE",
                        "description": "STRING",
                        "keywords": "STRING",
                        "source_id": "STRING",
                    },
                },
            },
        }
        self.G = Graph(graph_schema=graph_schema)

    @pytest.fixture(autouse=True)
    def add_nodes_and_edges(self):
        """Add nodes and edges before each test case."""
        # Initialize the graph
        self.setup_graph()

        # Adding nodes and edges
        self.G.add_node(
            "Entity_1",
            "Entity",
            entity_type="Type1",
            description="Desc1",
            source_id="Source1",
        )
        self.G.add_node(
            "Entity_2",
            "Entity",
            entity_type="Type2",
            description="Desc2",
            source_id="Source2",
        )
        self.G.add_edge(
            "Entity_1",
            "Entity_2",
            "Entity",
            "relationship",
            "Entity",
            weight=1.0,
            description="Relates to",
            keywords="key1,key2",
            source_id="SourceRel",
        )

        yield  # The test case runs here

        self.G.clear()

    @pytest.fixture(scope="class", autouse=True)
    def drop_graph(self):
        """Drop the graph after all tests are done in the session."""
        yield
        self.setup_graph()
        self.G.drop_graph()

    # ------------------------------ Homogeneous Graph ------------------------------
    def test_homogeneous_graph(self):
        # Assertions
        assert self.G.has_node("Entity_1")
        assert self.G.has_node("Entity_2")
        assert self.G.has_edge(
            "Entity_1", "Entity_2", "Entity", "relationship", "Entity"
        )

    # ------------------------------ Schema Operations ------------------------------
    def test_get_schema(self):
        # Get the graph schema in JSON format
        schema = self.G.get_schema(format="json")
        assert isinstance(schema, str)
        schema_dict = json.loads(schema)
        expected_schema_dict = {
            "graph_name": "ERGraph",
            "nodes": {
                "Entity": {
                    "primary_key": "id",
                    "attributes": {
                        "id": {"data_type": "STRING", "default_value": None},
                        "entity_type": {"data_type": "STRING", "default_value": None},
                        "description": {"data_type": "STRING", "default_value": None},
                        "source_id": {"data_type": "STRING", "default_value": None},
                    },
                    "vector_attributes": {},
                }
            },
            "edges": {
                "relationship": {
                    "is_directed_edge": True,
                    "from_node_type": "Entity",
                    "to_node_type": "Entity",
                    "attributes": {
                        "weight": {"data_type": "DOUBLE", "default_value": None},
                        "description": {"data_type": "STRING", "default_value": None},
                        "keywords": {"data_type": "STRING", "default_value": None},
                        "source_id": {"data_type": "STRING", "default_value": None},
                    },
                    "discriminator": [],
                }
            },
        }
        assert schema_dict == expected_schema_dict

        # Get the graph schema in Dict format
        schema = self.G.get_schema(format="dict")
        assert isinstance(schema, dict)
        assert schema["graph_name"] == "ERGraph"
        assert "Entity" in schema["nodes"]
        assert "relationship" in schema["edges"]
        assert schema["edges"]["relationship"]["is_directed_edge"] is True

    def test_from_db(self):
        G = Graph.from_db(graph_name=self.G.name)
        # Get the graph schema in Dict format
        schema = G.get_schema(format="dict")
        assert isinstance(schema, dict)
        assert schema["graph_name"] == "ERGraph"
        assert "Entity" in schema["nodes"]
        assert "relationship" in schema["edges"]
        assert schema["edges"]["relationship"]["is_directed_edge"] is True

    # ------------------------------ Data Loading Operations ------------------------------
    def create_loading_job_config(self) -> Dict:
        """
        Generate the LoadingJobConfig using a dictionary.
        """
        config_dict = {
            "loading_job_name": "loading_job_ERGraph",
            "files": [
                {
                    "file_alias": "f_entity",
                    "file_path": "/home/tigergraph/data/lightrag/ultradomain_fin/entity.csv",
                    "csv_parsing_options": {
                        "separator": ",",
                        "header": True,
                        "EOL": "\\n",
                        "quote": "DOUBLE",
                    },
                    "node_mappings": [
                        {
                            "target_name": "Entity",
                            "attribute_column_mappings": {
                                "id": "id",
                                "entity_type": "entity_type",
                                "description": "description",
                                "source_id": "source_id",
                            },
                        }
                    ],
                },
                {
                    "file_alias": "f_relationship",
                    "file_path": "/home/tigergraph/data/lightrag/ultradomain_fin/relationship.csv",
                    "csv_parsing_options": {
                        "separator": ",",
                        "header": True,
                        "EOL": "\\n",
                        "quote": "DOUBLE",
                    },
                    "edge_mappings": [
                        {
                            "target_name": "relationship",
                            "source_node_column": "source",
                            "target_node_column": "target",
                            "attribute_column_mappings": {
                                "weight": "weight",
                                "description": "description",
                                "keywords": "keywords",
                                "source_id": "source_id",
                            },
                        }
                    ],
                },
            ],
        }

        return config_dict

    def test_loading_job(self):
        # Load data
        loading_job_config = self.create_loading_job_config()
        assert loading_job_config is not None
        # self.G.load_data(loading_job_config)
        # assert len(self.G.nodes) > 0
