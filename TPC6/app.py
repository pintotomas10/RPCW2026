from flask import Flask, render_template
from mquery import exec_query
from datetime import datetime

app = Flask(__name__)

data_hora_local = datetime.now()
data_iso = data_hora_local.strftime('%Y-%m-%dT%H:%M:%S')

@app.route('/')
def index():
    q = """ PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX : <http://example.org/biblioteca-temporal#>
        select ?livroID ?titulo ?tipoID ?nomeAutor ?pais where {
            ?livro a ?tipoLivro .
            filter (?tipoLivro in (:LivroHistorico, :LivroFiccional, :LivroParadoxal))
            optional {?livro :titulo ?titulo . }
            ?livro :escritoPor/:nome ?nomeAutor .
            ?livro :escritoPor/:paisOrigem ?pais .
            BIND(STRAFTER(STR(?livro), "#") AS ?livroID)
            BIND(STRAFTER(STR(?tipoLivro), "#") AS ?tipoID)
    }
    order by ?titulo
"""
    res = exec_query(q)
    livros = []
    for livro in res["results"]["bindings"]:
        l = {
            "id": livro["livroID"]["value"],
            "tipo": livro["tipoID"]["value"],
            "autor": livro["nomeAutor"]["value"],
            "pais": livro["pais"]["value"],
        }
        if  "titulo" in livro:
            l["titulo"] = livro["titulo"]["value"]
        livros.append(l)  
    return render_template('lista.html', livros=livros)

@app.route('/livro/<id_livro>')
def livro(id_livro):
    q = f"""
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    PREFIX : <http://example.org/biblioteca-temporal#>
    select ?livroID ?titulo ?tipoID ?nomeAutor ?pais ?linhaID ?eventoID ?nomeEvento ?desc where {{
        ?livro a ?tipoLivro .
        filter (?tipoLivro in (:LivroHistorico, :LivroFiccional, :LivroParadoxal))
        BIND(STRAFTER(STR(?livro), "#") AS ?livroID)
        BIND(STRAFTER(STR(?tipoLivro), "#") AS ?tipoID)
        FILTER(?livroID = "{id_livro}")
        optional {{ ?livro :titulo ?titulo . }}
        ?livro :escritoPor/:nome ?nomeAutor .
        ?livro :escritoPor/:paisOrigem ?pais .
        optional {{ ?livro :existeEm ?linha . BIND(STRAFTER(STR(?linha), "#") AS ?linhaID) }}
        optional {{
            ?livro :refereEvento ?evento .
            ?evento :designacao ?nomeEvento .
            ?evento :descricao ?desc .
            BIND(STRAFTER(STR(?evento), "#") AS ?eventoID)
        }}
    }}
    limit 1
    """
    res = exec_query(q)
    livro = {}
    if res and res["results"]["bindings"]:
        d = res["results"]["bindings"][0]
        if "livroID" in d:
            livro["id"] = d["livroID"]["value"]
        if "tipoID" in d:
            livro["tipo"] = d["tipoID"]["value"]
        if "nomeAutor" in d:
            livro["autor"] = d["nomeAutor"]["value"]
        if "pais" in d:
            livro["pais"] = d["pais"]["value"]
        if "titulo" in d:
            livro["titulo"] = d["titulo"]["value"]
        if "linhaID" in d:
            livro["linha"] = d["linhaID"]["value"]
        if "eventoID" in d:
            livro["eventoID"] = d["eventoID"]["value"]
        if "nomeEvento" in d:
            livro["nomeEvento"] = d["nomeEvento"]["value"]
        if "desc" in d:
            livro["desc"] = d["desc"]["value"]
    return render_template('livro.html', livro=livro)

@app.route('/eventos')
def eventos():
    q = '''
    PREFIX : <http://example.org/biblioteca-temporal#>
    SELECT ?eventoID ?designacao ?desc (GROUP_CONCAT(?livroID; separator=", ") AS ?livros) WHERE {
        ?evento a :Evento .
        ?evento :designacao ?designacao .
        ?evento :descricao ?desc .
        BIND(STRAFTER(STR(?evento), "#") AS ?eventoID)
        OPTIONAL {
            ?livro :refereEvento ?evento .
            BIND(STRAFTER(STR(?livro), "#") AS ?livroID)
        }
    }
    GROUP BY ?eventoID ?designacao ?desc
    ORDER BY ?designacao
    '''
    res = exec_query(q)
    eventos = []
    if res and res["results"]["bindings"]:
        for e in res["results"]["bindings"]:
            evento = {
                "id": e["eventoID"]["value"],
                "designacao": e["designacao"]["value"],
                "desc": e["desc"]["value"],
                "livros": e["livros"]["value"].split(", ") if "livros" in e and e["livros"]["value"] else []
            }
            eventos.append(evento)
    return render_template('eventos.html', eventos=eventos)



# Página das linhas temporais (só id da linha e títulos dos livros, cada linha é link)
@app.route('/linhas')
def linhas():
    q = '''
    PREFIX : <http://example.org/biblioteca-temporal#>
    SELECT ?linhaID (GROUP_CONCAT(?livroID; separator=", ") AS ?livros) (GROUP_CONCAT(?titulo; separator="||") AS ?titulos) WHERE {
        ?linha a :LinhaTemporal .
        BIND(STRAFTER(STR(?linha), "#") AS ?linhaID)
        OPTIONAL {
            ?livro :existeEm ?linha .
            OPTIONAL { ?livro :titulo ?titulo . }
            BIND(STRAFTER(STR(?livro), "#") AS ?livroID)
        }
    }
    GROUP BY ?linhaID 
    ORDER BY ?linhaID
    '''
    res = exec_query(q)
    linhas = []
    if res and res["results"]["bindings"]:
        for l in res["results"]["bindings"]:
            livros = []
            if "livros" in l and l["livros"]["value"]:
                ids = l["livros"]["value"].split(", ")
                titulos = l["titulos"]["value"].split("||") if "titulos" in l and l["titulos"]["value"] else ["" for _ in ids]
                for i, lid in enumerate(ids):
                    livros.append({
                        "id": lid,
                        "titulo": titulos[i] if i < len(titulos) else ""
                    })
            linhas.append({
                "id": l["linhaID"]["value"],
                "livros": livros
            })
    return render_template('linhas.html', linhas=linhas)

# Página de uma linha temporal específica
@app.route('/linha/<id_linha>')
def linha(id_linha):
    q = f'''
    PREFIX : <http://example.org/biblioteca-temporal#>
    SELECT ?livroID ?titulo ?tipoLivroID WHERE {{
        ?linha a :LinhaTemporal .
        BIND(STRAFTER(STR(?linha), "#") AS ?linhaID)
        FILTER(?linhaID = "{id_linha}")
        ?livro :existeEm ?linha .
        OPTIONAL {{ ?livro :titulo ?titulo . }}
        ?livro a ?tipoLivro .
        filter (?tipoLivro in (:LivroHistorico, :LivroFiccional, :LivroParadoxal))
        BIND(STRAFTER(STR(?livro), "#") AS ?livroID)
        BIND(STRAFTER(STR(?tipoLivro), "#") AS ?tipoLivroID)
    }}
    ORDER BY ?titulo
    '''
    res = exec_query(q)
    livros = []
    if res and res["results"]["bindings"]:
        for l in res["results"]["bindings"]:
            livros.append({
                "id": l["livroID"]["value"],
                "titulo": l["titulo"]["value"] if "titulo" in l else "",
                "tipo": l["tipoLivroID"]["value"] if "tipoLivroID" in l else ""
            })
    linha = {"id": id_linha, "livros": livros}
    return render_template('linha.html', linha=linha)

if __name__ == '__main__':
    app.run(debug=True)