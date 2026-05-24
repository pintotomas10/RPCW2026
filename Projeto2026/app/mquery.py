from SPARQLWrapper import SPARQLWrapper, JSON

GRAPHDB_ENDPOINT = "http://localhost:7200/repositories/festival"

def exec_query(query):
    sparql = SPARQLWrapper(GRAPHDB_ENDPOINT)
    sparql.setQuery(query)
    sparql.setReturnFormat(JSON)
    try:
        return sparql.query().convert()
    except Exception as e:
        print(f"Erro ao executar a query SPARQL: {e}")
        return None

def exec_update(query):
    sparql = SPARQLWrapper(GRAPHDB_ENDPOINT + "/statements")
    sparql.setMethod('POST')
    sparql.setQuery(query)
    try:
        sparql.query()
        return True
    except Exception as e:
        print(f"Erro ao executar o update SPARQL: {e}")
        return False