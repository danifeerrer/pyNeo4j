from py2neo import Graph, Node, Relationship
from neo4j import GraphDatabase
from decouple import config
import pandas as pd

graph = Graph("bolt://localhost:7687", auth=("neo4j", password))

nodes_df = pd.read_csv("./test/nodes_test.tsv", delimiter="\t")

relationships_df = pd.read_csv('./test/edges_test.tsv', delimiter="\t")

uri = "bolt://localhost:7687"
user = "neo4j"
password = config("DATABASE_PASSWORD")


for _, row in nodes_df.iterrows():
    # Check if 'id', 'name', and 'kind' columns exist in the row
    if not pd.isnull(row["id"]) and not pd.isnull(row["name"]) and not pd.isnull(row["kind"]):
        node = Node(row["id"])
        # Add properties to the node
        node["id"] = row["id"]
        node["name"] = row["name"]
        node["kind"] = row["kind"]
        graph.create(node)


for _, row in relationships_df.iterrows():
    node1_id = row["source"]
    node2_id = row["target"]

    # Check if both nodes exist before creating a relationship
    node1 = graph.nodes.match(id=node1_id).first()
    node2 = graph.nodes.match(id=node2_id).first()

    if node1 and node2:
        relation = Relationship(node1, row["metaedge"], node2)
        # Add properties to the relationship if needed
        relation["metaedge"] = row["metaedge"]
        relation["source"] = row["source"]
        relation["target"] = row["target"]
        graph.create(relation)
    else:
        print(f"One or both nodes with IDs {node1_id} and {node2_id} do not exist.")