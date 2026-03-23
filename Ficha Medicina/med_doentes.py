import json
import urllib.parse
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, XSD

g = Graph()
g.parse("med_tratamentos.ttl", format="turtle")

ONTO = Namespace("http://www.example.org/disease-ontology#")
g.bind("", ONTO)

def make_uri(text):
    clean_text = text.strip().replace(" ", "_").replace("'", "").replace('"', '')
    clean_text = clean_text.replace("(", "").replace(")", "")
    return URIRef(ONTO + urllib.parse.quote(clean_text))

print("A processar doentes.json...")

with open('doentes.json', mode='r', encoding='utf-8') as file:
    doentes = json.load(file)

patient_id = 3

for doente in doentes:
    nome = doente["nome"]
    sintomas = doente["sintomas"]
    
    patient_uri = ONTO[f"Patient{patient_id}"]
    patient_id += 1
    
    g.add((patient_uri, RDF.type, ONTO.Patient))
    g.add((patient_uri, ONTO.name, Literal(nome, datatype=XSD.string)))
    
    for sintoma in sintomas:
        sintoma_uri = make_uri(sintoma)
        g.add((sintoma_uri, RDF.type, ONTO.Symptom)) 
        g.add((patient_uri, ONTO.exhibitsSymptom, sintoma_uri))

output_file = "med_doentes.ttl"
g.serialize(destination=output_file, format="turtle")
print(f"Ficheiro '{output_file}' gerado com sucesso.")