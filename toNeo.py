from py2neo import Graph, Node, Relationship
from decouple import config
from neo4j import GraphDatabase
import pandas as pd
import sys

if len(sys.argv) != 2:
    print("You must type <python> <program> <parameter_id>")
    exit()

try:
    integer_param = int(sys.argv[1])
except ValueError:
    print("Error: The provided parameter is not an integer.")
    sys.exit(1)


uri = "bolt://localhost:7687"
user = "neo4j"
password = config('DATABASE_PASSWORD')

class DatabaseManager:
    def __init__(self, uri, user, password):
        self._uri = uri
        self._user = user
        self._password = password

    def connect(self):
        return GraphDatabase.driver(self._uri, auth=(self._user, self._password))

db_manager = DatabaseManager(uri, user, password)


id = str(sys.argv[1])
output_locations = "This disease occurs in "
locations_list = []
compounds_list = []
genes_list = []
drugs_list = []
output_drugs = "This disease can be cured with the following drugs "
output_genes = "Genes associated with this disease are "

disease = f"Disease::DOID:{id}" #363



rescom = []

with db_manager.connect() as driver:
    with driver.session() as session:
        ###Name
        names = session.run(f"""
            MATCH (d:`Disease::DOID:{id}`) 
            RETURN d.name as namedisease
            """)
        
        for name in names:
            print("Name of the disease: ", name["namedisease"], '\n')

        ### GENES
        

        genes = session.run(f"""
            MATCH (d:`Disease::DOID:{id}`)-[:DaG]->(relatedNode) 
            WHERE relatedNode.kind = "Gene" 
            RETURN relatedNode.id AS relatedNodeId, relatedNode.name as relatedNodeName
        """)

        for gene in genes:
            genes_list.append(gene["relatedNodeId"])
            output_genes += gene["relatedNodeName"] + ", "

        
        ###

        ###LOCATIONS
        locations = session.run(f"""
                MATCH (d:`Disease::DOID:{id}`)-[:DlA]->(relatedNode) 
                RETURN relatedNode.id AS relatedNodeId, relatedNode.name AS relatedNodeName
            """)

        for location in locations:
            locations_list.append(location["relatedNodeId"])
            output_locations += location["relatedNodeName"] + ", "
        ###COMPOUNDS

        result = session.run(f"""
            MATCH (d:`Disease::DOID:{id}`)<-[:CtD]-(relatedNode)
            WHERE relatedNode.kind = 'Compound'
            RETURN relatedNode.id AS relatedNodeId
        """)
        
        for record in result:
            compounds_list.append(record["relatedNodeId"])
        
        ### DRUGS
        cypher_query_up_to_down = """
        MATCH (c)-[:CuG]->(g)<-[:AdG]-(a)
        WHERE c.id IN $compounds AND g.id IN $genes AND a.id in $anatomies
        RETURN c.name AS cName
        """

        result = session.run(cypher_query_up_to_down, compounds=compounds_list, genes=genes_list, anatomies=locations_list)

        rescom = [record["cName"] for record in result]

        for cName in rescom:
            drugs_list.append(cName)

        cypher_query_down_to_up = """
        MATCH (c)-[:CdG]->(g)<-[:AuG]-(a)
        WHERE c.id IN $compounds AND g.id IN $genes AND a.id in $anatomies
        RETURN c.name AS cName
        """
        result = session.run(cypher_query_down_to_up, compounds=compounds_list, genes=genes_list, anatomies=locations_list)

        rescom = [record["cName"] for record in result]

        for cName in rescom:
            drugs_list.append(cName)


drugs_list = list(set(drugs_list))
for drug in drugs_list:
    output_drugs += drug + ", "

print(output_drugs[:-2] + ".", '\n')

output_locations = output_locations[:-2] + "."
print(output_locations, '\n')

print(output_genes[:-2] + ".")

