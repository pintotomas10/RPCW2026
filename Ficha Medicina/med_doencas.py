import csv
import urllib.parse
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, OWL, RDFS, XSD

g = Graph()
g.parse("medical.ttl", format="turtle")

ONTO = Namespace("http://www.example.org/disease-ontology#")
g.bind("", ONTO)

def make_uri(text):
    clean_text = text.strip().replace(" ", "_").replace("'", "").replace('"', '')
    clean_text = clean_text.replace("(", "").replace(")", "")
    return URIRef(ONTO + urllib.parse.quote(clean_text))

print("A processar Disease_Syntoms.csv...")
with open('Disease_Syntoms.csv', mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    next(reader, None) 
    for row in reader:
        if not row: continue
        
        disease_name = row[0].strip()
        disease_uri = make_uri(disease_name)
        
        g.add((disease_uri, RDF.type, ONTO.Disease))
        
        for symptom_name in row[1:]:
            symptom_name = symptom_name.strip()
            if symptom_name: 
                symptom_uri = make_uri(symptom_name)
                g.add((symptom_uri, RDF.type, ONTO.Symptom))
                g.add((disease_uri, ONTO.hasSymptom, symptom_uri))

print("A processar Disease_Description.csv...")

g.add((ONTO.description, RDF.type, OWL.DatatypeProperty))
g.add((ONTO.description, RDFS.domain, ONTO.Disease))
g.add((ONTO.description, RDFS.range, XSD.string))

with open('Disease_Description.csv', mode='r', encoding='utf-8') as file:
    reader = csv.reader(file)
    header = next(reader, None)
    for row in reader:
        if len(row) >= 2:
            disease_uri = make_uri(row[0])
            description_text = row[1].strip()
            g.add((disease_uri, ONTO.description, Literal(description_text, datatype=XSD.string)))

output_file = "med_doencas.ttl"
g.serialize(destination=output_file, format="turtle")
print(f"Ficheiro '{output_file}' gerado com sucesso.")