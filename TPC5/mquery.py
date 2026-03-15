from SPARQLWrapper import SPARQLWrapper, JSON

GRAPHDB_ENDPOINT = "http://localhost:7200/repositories/biblioteca_temporal"

def exec_query(query):
    sparql = SPARQLWrapper(GRAPHDB_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        return sparql.query().convert() # executa a query, converte os resultados para JSON e devolve
    except Exception as e:
        print(f"Erro ao executar a query SPARQL: {e}")
        return None