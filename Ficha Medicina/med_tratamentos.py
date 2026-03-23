import csv
import urllib.parse
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF

g = Graph()
g.parse("med_doencas.ttl", format="turtle")

ONTO = Namespace("http://www.example.org/disease-ontology#")
g.bind("", ONTO)

def make_uri(text):
    clean_text = text.strip().replace(" ", "_").replace("'", "").replace('"', '')
    clean_text = clean_text.replace("(", "").replace(")", "")
    return URIRef(ONTO + urllib.parse.quote(clean_text))

print("A processar Disease_Treatment.csv...")

with open('Disease_Treatment.csv', mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    header = next(reader, None)
    for row in reader:
        if not row: continue
        
        disease_uri = make_uri(row[0])
        
        for treatment_name in row[1:]:
            treatment_name = treatment_name.strip()
            if treatment_name:
                treatment_uri = make_uri(treatment_name)
                g.add((treatment_uri, RDF.type, ONTO.Treatment))
                g.add((disease_uri, ONTO.hasTreatment, treatment_uri))

output_file = "med_tratamentos.ttl"
g.serialize(destination=output_file, format="turtle")
print(f"Ficheiro '{output_file}' gerado com sucesso.")