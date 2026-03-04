import json
import os
import re
from collections import defaultdict

from rdflib import Graph, Literal, Namespace 
from rdflib.namespace import OWL, RDF

BASE_URI = "http://www.semanticweb.org/utilizador/ontologies/2026/biblioteca_temporal/"
JSON_FILES = ["dataset_temporal_100.json", "dataset_temporal_v2_100.json"]
ONTOLOGY_FILE = "bibliotecaTemporal.ttl"
OUTPUT_FILE = "bibliotecaTemporal_povoada.ttl"

CLASS_MAP = {
    "LinhaOriginal": "LinhaOriginal",
    "LinhaAlternativa": "LinhaAlternativa",
    "Biblioteca": "Biblioteca",
    "EventoHistorico": "EventoHistórico",
    "EventoFuturo": "EventoFuturo",
    "Bibliotecario": "Bibliotecário",
    "Autor": "Autor",
    "Leitor": "Leitor",
    "LivroHistorico": "LivroHistórico",
    "LivroFiccional": "LivroFiccional",
    "LivroParadoxal": "LivroParodoxal",
}

PROPERTY_MAP = {
    "trabalhaEm": "trabalhaEm",
    "existeEm": "existeEm",
    "pertenceA": "pertenteA",
    "refereEvento": "refere",
    "escritoPor": "éEscritoPor",
    "nome": "nome",
}

DATATYPE_PROPERTIES = {"nome"}


def normalizar_id(valor: str) -> str:
    texto = str(valor).strip()
    texto = re.sub(r"[^A-Za-z0-9_]", "_", texto)
    texto = re.sub(r"_+", "_", texto)
    if not texto:
        return "RecursoSemId"
    if texto[0].isdigit():
        texto = f"_{texto}"
    return texto


def garantir_lista(valor):
    if isinstance(valor, list):
        return valor
    return [valor]


def carregar_json(caminho: str):
    with open(caminho, "r", encoding="utf-8") as f:
        return json.load(f)


def agregar_recursos(base_dir: str):
    recursos = defaultdict(lambda: {
        "classes": set(),
        "obj_props": defaultdict(set),
        "data_props": defaultdict(set),
    })

    for file_name in JSON_FILES:
        json_path = os.path.join(base_dir, file_name)
        if not os.path.exists(json_path):
            print(f"[AVISO] Ficheiro não encontrado: {file_name}")
            continue

        dados = carregar_json(json_path)
        if not isinstance(dados, list):
            print(f"[AVISO] Formato inválido em {file_name}: esperado array JSON")
            continue

        for item in dados:
            if not isinstance(item, dict) or "id" not in item:
                continue

            sujeito_id = normalizar_id(item["id"])
            registo = recursos[sujeito_id]

            tipo = item.get("tipo")
            if tipo:
                classe = CLASS_MAP.get(tipo, tipo)
                registo["classes"].add(classe)

            for chave, valor in item.items():
                if chave in {"id", "tipo"}:
                    continue

                prop = PROPERTY_MAP.get(chave, chave)
                for v in garantir_lista(valor):
                    if chave in DATATYPE_PROPERTIES:
                        registo["data_props"][prop].add(str(v))
                    else:
                        registo["obj_props"][prop].add(normalizar_id(v))

    return recursos


def povoar_ontologia(base_dir: str):
    ont_path = os.path.join(base_dir, ONTOLOGY_FILE)
    out_path = os.path.join(base_dir, OUTPUT_FILE)

    if not os.path.exists(ont_path):
        raise FileNotFoundError(f"Ontologia base não encontrada: {ont_path}")

    graph = Graph()
    graph.parse(ont_path, format="turtle")

    ns = Namespace(BASE_URI)
    recursos = agregar_recursos(base_dir)

    object_props_usadas = set()
    datatype_props_usadas = set()
    for registo in recursos.values():
        object_props_usadas.update(registo["obj_props"].keys())
        datatype_props_usadas.update(registo["data_props"].keys())

    for prop in sorted(object_props_usadas):
        graph.add((ns[prop], RDF.type, OWL.ObjectProperty))

    for prop in sorted(datatype_props_usadas):
        graph.add((ns[prop], RDF.type, OWL.DatatypeProperty))

    for sujeito_id, registo in recursos.items():
        sujeito = ns[sujeito_id]
        graph.add((sujeito, RDF.type, OWL.NamedIndividual))

        for classe in sorted(registo["classes"]):
            graph.add((sujeito, RDF.type, ns[classe]))

        for prop, valores in registo["obj_props"].items():
            pred = ns[prop]
            for alvo_id in sorted(valores):
                graph.add((sujeito, pred, ns[alvo_id]))

        for prop, valores in registo["data_props"].items():
            pred = ns[prop]
            for literal in sorted(valores):
                graph.add((sujeito, pred, Literal(literal)))

    graph.serialize(destination=out_path, format="turtle")
    print(f"Sucesso: ontologia povoada gerada em {out_path}")
    print(f"Recursos adicionados/atualizados: {len(recursos)}")


def main():
    base_dir = os.path.dirname(__file__)
    povoar_ontologia(base_dir)


if __name__ == "__main__":
    main()
