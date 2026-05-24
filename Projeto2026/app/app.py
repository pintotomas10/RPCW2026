from flask import Flask, render_template, request, redirect, url_for
from mquery import exec_query, exec_update
import uuid
import re

app = Flask(__name__)


@app.route('/')
def home():
    # Estatísticas principais
    q_stats = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT (COUNT(DISTINCT ?edicao) AS ?num_edicoes) (COUNT(DISTINCT ?musica) AS ?num_musicas) WHERE {{
        ?edicao a :FestivalEdition .
        OPTIONAL {{ ?edicao :hasContestant ?c . ?c :performsSong ?musica . }}
    }}
    """
    stats_res = exec_query(q_stats)
    stats = {
        "num_edicoes": 0,
        "num_musicas": 0,
        "num_artistas": 0,
        "num_compositores": 0,
        "num_fases": 0,
        "edicoes_com_semifinal": 0,
    }
    if stats_res and stats_res.get("results", {}).get("bindings"):
        r = stats_res["results"]["bindings"][0]
        stats["num_edicoes"] = int(r.get("num_edicoes", {}).get("value", 0))
        stats["num_musicas"] = int(r.get("num_musicas", {}).get("value", 0))

    q_people_stats = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT (COUNT(DISTINCT ?artistaNome) AS ?num_artistas)
           (COUNT(DISTINCT ?comp) AS ?num_compositores)
    WHERE {{
        OPTIONAL {{ ?c a :Contestant ; :artistName ?artistaNome . }}
        OPTIONAL {{ ?musica :hasComposer ?comp . }}
    }}
    """
    people_stats_res = exec_query(q_people_stats)
    if people_stats_res and people_stats_res.get("results", {}).get("bindings"):
        r = people_stats_res["results"]["bindings"][0]
        stats["num_artistas"] = int(r.get("num_artistas", {}).get("value", 0))
        stats["num_compositores"] = int(r.get("num_compositores", {}).get("value", 0))

    q_phase_stats = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT (COUNT(DISTINCT ?fase) AS ?num_fases)
           (COUNT(DISTINCT ?edSemi) AS ?edicoes_com_semifinal)
    WHERE {{
        OPTIONAL {{ ?ed a :FestivalEdition ; :hasPhase ?fase . }}
        OPTIONAL {{
            ?edSemi a :FestivalEdition ; :hasPhase ?sf .
            ?sf a :SemiFinal .
        }}
    }}
    """
    phase_stats_res = exec_query(q_phase_stats)
    if phase_stats_res and phase_stats_res.get("results", {}).get("bindings"):
        r = phase_stats_res["results"]["bindings"][0]
        stats["num_fases"] = int(r.get("num_fases", {}).get("value", 0))
        stats["edicoes_com_semifinal"] = int(r.get("edicoes_com_semifinal", {}).get("value", 0))

    # Top 5 compositores por número de músicas
    q_top = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?nomeCompositor (COUNT(?musica) AS ?totalMusicas) WHERE {{
        ?musica :hasComposer ?compositor .
        ?compositor :personName ?nomeCompositor .
    }}
    GROUP BY ?nomeCompositor
    ORDER BY DESC(?totalMusicas)
    LIMIT 5
    """
    top_res = exec_query(q_top)
    top_compositors = []
    if top_res and top_res.get("results", {}).get("bindings"):
        for row in top_res["results"]["bindings"]:
            top_compositors.append({
                "nome": row.get("nomeCompositor", {}).get("value", "N/A"),
                "total": int(row.get("totalMusicas", {}).get("value", 0)),
            })

    # Top 5 artistas por participações
    q_top_artists = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?nome (COUNT(?c) AS ?total) WHERE {{
        ?c a :Contestant ; :artistName ?nome .
    }}
    GROUP BY ?nome
    ORDER BY DESC(?total)
    LIMIT 5
    """
    top_artists_res = exec_query(q_top_artists)
    top_artists = []
    if top_artists_res and top_artists_res.get("results", {}).get("bindings"):
        for row in top_artists_res["results"]["bindings"]:
            top_artists.append({
                "nome": row.get("nome", {}).get("value", "N/A"),
                "total": int(row.get("total", {}).get("value", 0)),
            })

    # Último vencedor registado
    q_recent = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?ano ?titulo ?artista WHERE {{
        ?edicao a :FestivalEdition ; :editionYear ?ano .
        OPTIONAL {{ ?edicao :hasWinner ?musica . ?musica :songTitle ?titulo . OPTIONAL {{ ?musica :performedBy ?conc . ?conc :artistName ?artista . }} }}
    }} ORDER BY DESC(?ano) LIMIT 1
    """
    recent_res = exec_query(q_recent)
    recent_winner = {"ano": "N/A", "titulo": "N/A", "artista": "N/A"}
    if recent_res and recent_res.get("results", {}).get("bindings"):
        r = recent_res["results"]["bindings"][0]
        recent_winner = {
            "ano": r.get("ano", {}).get("value", "N/A"),
            "titulo": r.get("titulo", {}).get("value", "N/A"),
            "artista": r.get("artista", {}).get("value", "N/A"),
        }

    # Edição em destaque (mais recente)
    q_spotlight = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?ano ?vencedor ?artista ?diretor (COUNT(DISTINCT ?musica) AS ?num_musicas) WHERE {{
        ?edicao a :FestivalEdition ; :editionYear ?ano .
        OPTIONAL {{ ?edicao :hasContestant ?c . ?c :performsSong ?musica . }}
        OPTIONAL {{
            ?edicao :hasWinner ?winSong .
            ?winSong :songTitle ?vencedor .
            OPTIONAL {{ ?winSong :performedBy ?conc . ?conc :artistName ?artista . }}
        }}
        OPTIONAL {{ ?edicao :hasMusicDirector ?md . ?md :personName ?diretor . }}
    }}
    GROUP BY ?ano ?vencedor ?artista ?diretor
    ORDER BY DESC(?ano)
    LIMIT 1
    """
    spotlight_res = exec_query(q_spotlight)
    spotlight = {
        "ano": "N/A",
        "num_musicas": 0,
        "vencedor": "N/A",
        "artista": "N/A",
        "diretor": "N/A",
    }
    if spotlight_res and spotlight_res.get("results", {}).get("bindings"):
        r = spotlight_res["results"]["bindings"][0]
        spotlight = {
            "ano": r.get("ano", {}).get("value", "N/A"),
            "num_musicas": int(r.get("num_musicas", {}).get("value", 0)),
            "vencedor": r.get("vencedor", {}).get("value", "N/A"),
            "artista": r.get("artista", {}).get("value", "N/A"),
            "diretor": r.get("diretor", {}).get("value", "N/A"),
        }

    # Timeline por década
    q_yearly = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?ano (COUNT(DISTINCT ?musica) AS ?num_musicas) WHERE {{
        ?edicao a :FestivalEdition ; :editionYear ?ano .
        OPTIONAL {{ ?edicao :hasContestant ?c . ?c :performsSong ?musica . }}
    }}
    GROUP BY ?ano
    ORDER BY ?ano
    """
    yearly_res = exec_query(q_yearly)
    timeline = []
    decade_map = {}
    if yearly_res and yearly_res.get("results", {}).get("bindings"):
        for row in yearly_res["results"]["bindings"]:
            try:
                year = int(row.get("ano", {}).get("value", 0))
            except (TypeError, ValueError):
                continue
            decade = (year // 10) * 10
            if decade not in decade_map:
                decade_map[decade] = {"decada": f"{decade}s", "edicoes": 0, "musicas": 0}
            decade_map[decade]["edicoes"] += 1
            decade_map[decade]["musicas"] += int(row.get("num_musicas", {}).get("value", 0))
        timeline = [decade_map[d] for d in sorted(decade_map.keys())]

    return render_template(
        'index.html',
        stats=stats,
        top_compositors=top_compositors,
        top_artists=top_artists,
        recent_winner=recent_winner,
        spotlight=spotlight,
        timeline=timeline,
    )

@app.route('/edicao')
def index():
    # Query para listar todas as edições e respetivos vencedores
    q = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?ano ?vencedor ?artista_vencedor ?vencedorID ?temSemifinal WHERE {{
        ?edicao a :FestivalEdition ;
                :editionYear ?ano .
        OPTIONAL {{
            ?edicao :hasWinner ?musica .
            ?musica :songTitle ?vencedor .
            ?musica :performedBy ?concorrente .
            ?concorrente :artistName ?artista_vencedor .
            BIND(STRAFTER(STR(?musica), "Song_") AS ?vencedorID)
        }}
        BIND(EXISTS {{ ?edicao :hasPhase ?fase . ?fase a :SemiFinal . }} AS ?temSemifinal)
        BIND(STR(?ano) AS ?anoID)
    }} ORDER BY DESC(?ano)
    """
    res = exec_query(q)
    edicoes = []
    if res:
        raw_edicoes = []
        for row in res["results"]["bindings"]:
            ano = row["ano"]["value"]
            raw_edicoes.append({
                "ano": ano,
                "ano_int": int(ano),
                "vencedor": row["vencedor"]["value"] if "vencedor" in row else "N/A",
                "artista": row.get("artista_vencedor", {}).get("value", "N/A"),
                "vencedorID": row["vencedorID"]["value"] if "vencedorID" in row else "",
                "temSemifinal": row.get("temSemifinal", {}).get("value", "false")
            })

        raw_edicoes.sort(key=lambda item: item["ano_int"])
        for idx, item in enumerate(raw_edicoes, start=1):
            item["edicaoLabel"] = f"{idx}ª edição"

        edicoes = sorted(raw_edicoes, key=lambda item: item["ano_int"], reverse=True)
    return render_template('lista_edicoes.html', edicoes=edicoes)

@app.route('/edicao/<ano>')
def edicao_detalhe(ano):
    # Informacao geral da edicao
    q_info = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?ano_val (COUNT(DISTINCT ?musica) AS ?num_musicas) WHERE {{
        ?edicao a :FestivalEdition ;
                :editionYear ?ano_val .
        FILTER(STR(?ano_val) = "{ano}")
        OPTIONAL {{
            ?edicao :hasContestant ?c .
            ?c :performsSong ?musica .
        }}
    }}
    GROUP BY ?ano_val
    """
    info_res = exec_query(q_info)

    edicao_info = {
        "ano": ano,
        "num_musicas": 0,
        "fases": [],
        "vencedor": "N/A",
        "vencedor_artist": "N/A",
        "vencedor_place": "N/A"
    }

    if info_res and info_res["results"]["bindings"]:
        row = info_res["results"]["bindings"][0]
        edicao_info["ano"] = row.get("ano_val", {}).get("value", ano)
        edicao_info["num_musicas"] = int(row.get("num_musicas", {}).get("value", 0))

    # Fases: final e semifinais (se existirem), com local e apresentadores
    q_fases = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?fase ?tipo ?data ?local ?cidade
           (GROUP_CONCAT(DISTINCT ?apNome; separator=" | ") AS ?apresentadores)
    WHERE {{
        ?edicao a :FestivalEdition ;
                :editionYear ?ano_val ;
                :hasPhase ?fase .
        FILTER(STR(?ano_val) = "{ano}")

        BIND(IF(EXISTS {{ ?fase a :Final }}, "Final", "Semi-final") AS ?tipo)

        OPTIONAL {{ ?fase :phaseDate ?data . }}
        OPTIONAL {{
            ?fase :heldAt ?venue .
            ?venue :venueName ?local .
            OPTIONAL {{
                ?venue :locatedIn ?city .
                ?city :cityName ?cidade .
            }}
        }}
        OPTIONAL {{
            ?fase :hasPresenter ?ap .
            ?ap :personName ?apNome .
        }}
    }}
    GROUP BY ?fase ?tipo ?data ?local ?cidade
    ORDER BY ?tipo ?data
    """
    fases_res = exec_query(q_fases)

    if fases_res and fases_res["results"]["bindings"]:
        seen_fases = set()
        for row in fases_res["results"]["bindings"]:
            fase_uri = row.get("fase", {}).get("value")
            if not fase_uri or fase_uri in seen_fases:
                continue
            seen_fases.add(fase_uri)
            apresentadores_raw = row.get("apresentadores", {}).get("value", "")
            apresentadores = [a.strip() for a in apresentadores_raw.split(" | ") if a.strip()]
            edicao_info["fases"].append({
                "tipo": row.get("tipo", {}).get("value", "N/A"),
                "data": row.get("data", {}).get("value", "N/A"),
                "local": row.get("local", {}).get("value", "N/A"),
                "cidade": row.get("cidade", {}).get("value", "N/A"),
                "apresentadores": apresentadores
            })

    # Consulta do vencedor (se existir)
    q_winner = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?vencedor ?artista ?resultado WHERE {{
        ?edicao a :FestivalEdition ;
                :editionYear ?ano_val .
        FILTER(STR(?ano_val) = "{ano}")

        OPTIONAL {{
            ?edicao :hasWinner ?musica .
            ?musica :songTitle ?vencedor .
            OPTIONAL {{ ?musica :performedBy ?conc . ?conc :artistName ?artista . }}
            OPTIONAL {{ ?musica :eurovisionResult ?resultado . }}
        }}
    }} LIMIT 1
    """
    winner_res = exec_query(q_winner)
    if winner_res and winner_res.get("results", {}).get("bindings"):
        w = winner_res["results"]["bindings"][0]
        edicao_info["vencedor"] = w.get("vencedor", {}).get("value", "N/A")
        edicao_info["vencedor_artist"] = w.get("artista", {}).get("value", "N/A")
        edicao_info["vencedor_place"] = w.get("resultado", {}).get("value", "N/A")

    # Diretor musical (se existir) ligado à edição
    edicao_info["music_director"] = "N/A"
    q_director = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?mdName WHERE {{
        ?edicao a :FestivalEdition ; :editionYear ?ano_val .
        FILTER(STR(?ano_val) = "{ano}")
        OPTIONAL {{ ?edicao :hasMusicDirector ?md . ?md :personName ?mdName . }}
    }} LIMIT 1
    """
    dir_res = exec_query(q_director)
    if dir_res and dir_res.get('results', {}).get('bindings'):
        md = dir_res['results']['bindings'][0].get('mdName', {}).get('value')
        if md:
            edicao_info["music_director"] = md

    # Musicas com artista, compositores e letristas
    q = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT DISTINCT ?musica ?titulo ?artista
           (GROUP_CONCAT(DISTINCT ?compNome; separator=" | ") AS ?compositores)
           (GROUP_CONCAT(DISTINCT ?lirNome; separator=" | ") AS ?liricistas)
    WHERE {{
        ?edicao a :FestivalEdition ;
                :editionYear ?ano_val .
        FILTER(STR(?ano_val) = "{ano}")

        ?edicao :hasContestant ?concorrente .
        ?concorrente :performsSong ?musica .
        ?musica :songTitle ?titulo .

        OPTIONAL {{
            ?concorrente :artistName ?artista .
        }}

        OPTIONAL {{
            ?musica :hasComposer ?compInd .
            ?compInd :personName ?compNome .
        }}

        OPTIONAL {{
            ?musica :hasLyricist ?lirInd .
            ?lirInd :personName ?lirNome .
        }}
    }}
    GROUP BY ?musica ?titulo ?artista
    ORDER BY ?titulo
    """
    res = exec_query(q)
    participantes = []
    if res and res["results"]["bindings"]:
        for r in res["results"]["bindings"]:
            compositores_raw = r.get("compositores", {}).get("value", "")
            liricistas_raw = r.get("liricistas", {}).get("value", "")

            participantes.append({
                "id": r["musica"]["value"].split("/")[-1],
                "titulo": r["titulo"]["value"],
                "artista": r.get("artista", {}).get("value", "N/A"),
                "compositores": [c.strip() for c in compositores_raw.split(" | ") if c.strip()],
                "liricistas": [l.strip() for l in liricistas_raw.split(" | ") if l.strip()]
            })

    return render_template('edicao.html', ano=ano, participantes=participantes, edicao_info=edicao_info)


@app.route('/vencedores')
def vencedores():
    # Lista de vencedores por edição
    q = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?ano ?titulo ?artista ?resultado WHERE {{
        ?edicao a :FestivalEdition ; :editionYear ?ano .
        ?edicao :hasWinner ?musica .
        ?musica :songTitle ?titulo .
        OPTIONAL {{ ?musica :performedBy ?conc . ?conc :artistName ?artista . }}
        OPTIONAL {{ ?musica :eurovisionResult ?resultado . }}
    }} ORDER BY DESC(?ano) DESC(?resultado)
    """

    res = exec_query(q)
    vencedores = []
    if res and res.get("results", {}).get("bindings"):
        for row in res["results"]["bindings"]:
            vencedores.append({
                "ano": row.get("ano", {}).get("value", "N/A"),
                "titulo": row.get("titulo", {}).get("value", "N/A"),
                "artista": row.get("artista", {}).get("value", "N/A"),
                "europlace": row.get("resultado", {}).get("value", "N/A")
            })

    return render_template('vencedores.html', vencedores=vencedores)


@app.route('/pessoas')
def pessoas():
    # Lista de todos os artistas, liricistas, compositores e apresentadores
    q_artistas = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT DISTINCT ?nome WHERE {{
        ?p a :Contestant ;
           :artistName ?nome .
    }} ORDER BY ?nome
    """

    q_liricistas = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT DISTINCT ?nome WHERE {{
        ?p a :Lyricist ;
           :personName ?nome .
    }} ORDER BY ?nome
    """

    q_compositores = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT DISTINCT ?nome WHERE {{
        ?p a :Composer ;
           :personName ?nome .
    }} ORDER BY ?nome
    """

    q_apresentadores = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT DISTINCT ?nome WHERE {{
        ?p a :Presenter ;
           :personName ?nome .
    }} ORDER BY ?nome
    """

    def fetch_names(query):
        result = exec_query(query)
        names = []
        if result and result.get("results", {}).get("bindings"):
            for row in result["results"]["bindings"]:
                names.append(row.get("nome", {}).get("value", "N/A"))
        return names

    artistas = fetch_names(q_artistas)
    liricistas = fetch_names(q_liricistas)
    compositores = fetch_names(q_compositores)
    apresentadores = fetch_names(q_apresentadores)

    return render_template(
        'pessoas.html',
        artistas=artistas,
        liricistas=liricistas,
        compositores=compositores,
        apresentadores=apresentadores,
    )


@app.route('/cancoes')
def cancoes():
    # Lista de todas as canções
    q_cancoes = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT DISTINCT ?titulo ?ano ?artista 
           (GROUP_CONCAT(DISTINCT ?nomeCompositor; separator=", ") AS ?compositores)
           (GROUP_CONCAT(DISTINCT ?nomeLiricista; separator=", ") AS ?liricistas)
    WHERE {{
        ?edicao :editionYear ?ano ;
                :hasContestant ?c .
        ?c :performsSong ?musica ;
           :artistName ?artista .
        ?musica :songTitle ?titulo .
        OPTIONAL {{
            ?musica :hasComposer ?compositor .
            ?compositor :personName ?nomeCompositor .
        }}
        OPTIONAL {{
            ?musica :hasLyricist ?liricista .
            ?liricista :personName ?nomeLiricista .
        }}
    }}
    GROUP BY ?titulo ?ano ?artista
    ORDER BY DESC(?ano) ?titulo
    """
    
    cancoes_res = exec_query(q_cancoes)
    cancoes_list = []
    if cancoes_res and cancoes_res.get("results", {}).get("bindings"):
        for row in cancoes_res["results"]["bindings"]:
            cancoes_list.append({
                "titulo": row.get("titulo", {}).get("value", "N/A"),
                "ano": row.get("ano", {}).get("value", "N/A"),
                "artista": row.get("artista", {}).get("value", "N/A"),
                "compositores": row.get("compositores", {}).get("value", "N/A"),
                "liricistas": row.get("liricistas", {}).get("value", "N/A"),
            })
    
    return render_template('cancoes.html', cancoes=cancoes_list)


@app.route('/nova-edicao', methods=['GET', 'POST'])
def nova_edicao():
    erro = None
    sucesso = None
    ano_criado = None

    if request.method == 'POST':
        ano = request.form.get('ano', '').strip()

        if not ano.isdigit():
            erro = 'O ano tem de ser um número válido.'
        else:
            q_existe = f"""
            PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
            SELECT ?edicao WHERE {{
                ?edicao a :FestivalEdition ;
                        :editionYear ?ano .
                FILTER(STR(?ano) = "{ano}")
            }} LIMIT 1
            """
            existe_res = exec_query(q_existe)
            if existe_res and existe_res.get('results', {}).get('bindings'):
                erro = f'Já existe uma edição para o ano {ano}.'
            else:
                q_insert = f"""
                PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
                INSERT DATA {{
                    :Edition_{ano} a :FestivalEdition ;
                        :editionYear {ano} .
                }}
                """
                if exec_update(q_insert):
                    return redirect(url_for('edicao_detalhe', ano=ano))
                else:
                    erro = 'Não foi possível criar a edição.'

    return render_template('nova_edicao.html', erro=erro, sucesso=sucesso, ano_criado=ano_criado)


@app.route('/pessoa/<path:nome>')
def pessoa(nome):
    year = request.args.get('year', None)
    
    # Participações de uma pessoa por função
    q_artista = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT DISTINCT ?ano ?titulo WHERE {{
        ?edicao :editionYear ?ano ;
                :hasContestant ?c .
        ?c :artistName ?nomeArtista ;
           :performsSong ?musica .
        ?musica :songTitle ?titulo .
        FILTER(LCASE(STR(?nomeArtista)) = LCASE("{nome}"))
    }} ORDER BY DESC(?ano) ?titulo
    """

    q_liricista = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT DISTINCT ?ano ?titulo WHERE {{
        ?edicao :editionYear ?ano ;
                :hasContestant ?c .
        ?c :performsSong ?musica .
        ?musica :songTitle ?titulo ;
                :hasLyricist ?p .
        ?p :personName ?nomePessoa .
        FILTER(LCASE(STR(?nomePessoa)) = LCASE("{nome}"))
    }} ORDER BY DESC(?ano) ?titulo
    """

    q_compositor = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT DISTINCT ?ano ?titulo WHERE {{
        ?edicao :editionYear ?ano ;
                :hasContestant ?c .
        ?c :performsSong ?musica .
        ?musica :songTitle ?titulo ;
                :hasComposer ?p .
        ?p :personName ?nomePessoa .
        FILTER(LCASE(STR(?nomePessoa)) = LCASE("{nome}"))
    }} ORDER BY DESC(?ano) ?titulo
    """

    q_apresentador = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT DISTINCT ?ano ?tipoFase WHERE {{
        ?edicao :editionYear ?ano ;
                :hasPhase ?fase .
        ?fase :hasPresenter ?p .
        ?p :personName ?nomePessoa .
        BIND(IF(EXISTS {{ ?fase a :Final }}, "Final", "Semi-final") AS ?tipoFase)
        FILTER(LCASE(STR(?nomePessoa)) = LCASE("{nome}"))
    }} ORDER BY DESC(?ano) ?tipoFase
    """

    def fetch_rows(query):
        result = exec_query(query)
        rows = []
        if result and result.get("results", {}).get("bindings"):
            for row in result["results"]["bindings"]:
                rows.append({
                    "ano": row.get("ano", {}).get("value", "N/A"),
                    "titulo": row.get("titulo", {}).get("value", "N/A"),
                    "tipoFase": row.get("tipoFase", {}).get("value", "N/A"),
                })
        return rows

    participacoes_artista = fetch_rows(q_artista)
    participacoes_liricista = fetch_rows(q_liricista)
    participacoes_compositor = fetch_rows(q_compositor)
    participacoes_apresentador = fetch_rows(q_apresentador)

    return render_template(
        'pessoa.html',
        nome=nome,
        year=year,
        participacoes_artista=participacoes_artista,
        participacoes_liricista=participacoes_liricista,
        participacoes_compositor=participacoes_compositor,
        participacoes_apresentador=participacoes_apresentador,
    )
    
@app.route('/edicao/<ano>/nova-fase', methods=['GET', 'POST'])
def nova_fase(ano):
    erro = None
    sucesso = None

    if request.method == 'POST':
        tipo = request.form.get('tipo')
        data = request.form.get('data')
        local_nome = request.form.get('local')
        cidade_nome = request.form.get('cidade')
        apresentadores_raw = request.form.get('apresentadores', '')

        uid = uuid.uuid4().hex[:4]
        fase_id = f"{tipo}_{ano}_{uid}"
        venue_id = f"Venue_{local_nome.replace(' ', '_')}_{uid}"
        city_id = f"City_{cidade_nome.replace(' ', '_')}"

        # Processar apresentadores
        apresentadores = [ap.strip() for ap in apresentadores_raw.splitlines() if ap.strip()]
        triples_apresentadores = ""
        for ap in apresentadores:
            ap_uri = "Person_" + ap.replace(" ", "_")
            triples_apresentadores += f"""
            :{ap_uri} a :Person ; :personName "{ap}" .
            :{fase_id} :hasPresenter :{ap_uri} .
            """

        q = f"""
        PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
        INSERT DATA {{
            # Criar a Cidade
            :{city_id} a :City ; :cityName "{cidade_nome}" .

            # Criar o Local e ligar à Cidade
            :{venue_id} a :Venue ; :venueName "{local_nome}" ; :locatedIn :{city_id} .

            # Criar a Fase e ligar ao Local e à Edição
            :{fase_id} a :{tipo} ;
                :phaseDate "{data}" ;
                :heldAt :{venue_id} .

            :Edition_{ano} :hasPhase :{fase_id} .

            {triples_apresentadores}
        }}
        """

        if exec_update(q):
            return redirect(url_for('edicao_detalhe', ano=ano))
        else:
            erro = "Erro ao inserir no GraphDB. Verifica se o repositório está ligado."

    return render_template('nova_fase.html', ano=ano, erro=erro, sucesso=sucesso)


def slugify(text):
    text = text.lower().replace(" ", "_")
    return re.sub(r'\W+', '', text)

@app.route('/edicao/<ano>/nova-musica', methods=['GET', 'POST'])
def nova_musica(ano):
    erro = None
    sucesso = None

    if request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        artista = request.form.get('artista', '').strip()
        compositores = [c.strip() for c in request.form.get('compositores', '').replace('\n', ',').split(',') if c.strip()]
        liricistas = [l.strip() for l in request.form.get('liricistas', '').replace('\n', ',').split(',') if l.strip()]

        song_slug = slugify(titulo)
        artist_slug = slugify(artista)
        
        song_id = f"Song_{ano}_{song_slug}"
        contestant_id = f"Contestant_{ano}_{artist_slug}_{uuid.uuid4().hex[:4]}"
        person_id = f"Person_{artist_slug}"

        # Triplos de autores (Compositores e Liricistas)
        triples_autores = ""
        for c in compositores:
            c_slug = slugify(c)
            triples_autores += f"""
            :Person_{c_slug} a :Person, :Composer ; :personName "{c}" .
            :{song_id} :hasComposer :Person_{c_slug} .
            """
        
        for l in liricistas:
            l_slug = slugify(l)
            triples_autores += f"""
            :Person_{l_slug} a :Person, :Lyricist ; :personName "{l}" .
            :{song_id} :hasLyricist :Person_{l_slug} .
            """

        q = f"""
        PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
        INSERT DATA {{
            # 1. A Pessoa (O Artista real)
            :{person_id} a :Person, :Artist ;
                :personName "{artista}" .

            # 2. O Contestant (A inscrição no festival)
            :{contestant_id} a :Contestant ;
                :contestantId "{contestant_id}" ;
                :artistName "{artista}" ;      # CRUCIAL: Propriedade que o teu TTL usa para o nome no Contestant
                :belongsToEdition :Edition_{ano} ;
                :performsSong :{song_id} .

            # 3. A Música
            :{song_id} a :Song ;
                :songTitle "{titulo}" ;
                :isPerformedBy :{person_id} ;  # CORREÇÃO: No teu TTL é 'isPerformedBy'
                :isPerformedBy :{contestant_id} .

            # 4. Ligar a Edição ao Contestant
            :Edition_{ano} :hasContestant :{contestant_id} .

            {triples_autores}
        }}
        """

        if exec_update(q):
            return redirect(url_for('edicao_detalhe', ano=ano))
        else:
            erro = "Erro ao comunicar com o GraphDB. Verifica os logs."

    return render_template('nova_musica.html', ano=ano, erro=erro, sucesso=sucesso)

@app.route('/edicao/<ano>/vencedor', methods=['GET', 'POST'])
def vencedor(ano):
    erro = None
    sucesso = None
    ano_str = str(ano)

    if request.method == 'POST':
        contestant_id = request.form.get('contestant')
        resultado_euro = request.form.get('resultado_eurovisao', '').strip()

        q_lookup = f"""
        PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
        SELECT ?song WHERE {{
            :{contestant_id} :performsSong ?song .
        }}
        """
        lookup_res = exec_query(q_lookup)
        
        if not lookup_res or not lookup_res.get('results', {}).get('bindings'):
            erro = "Não foi possível encontrar a música associada."
        else:
            song_uri = lookup_res['results']['bindings'][0]['song']['value']

            q_check = f"""
            PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
            SELECT ?edicao ?oldWinner WHERE {{
                ?edicao a :FestivalEdition ; :editionYear ?y .
                FILTER(xsd:integer(?y) = {ano_str})
                OPTIONAL {{ ?edicao :hasWinner ?oldWinner . }}
            }} LIMIT 1
            """
            check_res = exec_query(q_check)

            if check_res and check_res.get('results', {}).get('bindings'):
                edicao_uri = check_res['results']['bindings'][0]['edicao']['value']
                
                q_delete = f"""
                PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
                DELETE {{
                    <{edicao_uri}> :hasWinner ?old .
                    ?old :eurovisionResult ?result .
                }}
                WHERE {{
                    <{edicao_uri}> :hasWinner ?old .
                    OPTIONAL {{ ?old :eurovisionResult ?result . }}
                }}
                """
                exec_update(q_delete)
                
                q_insert = f"""
                PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
                INSERT {{
                    <{edicao_uri}> :hasWinner <{song_uri}> .
                    <{song_uri}> :eurovisionResult "{resultado_euro}" .
                }}
                WHERE {{ }}
                """
                
                if exec_update(q_insert):
                    return redirect(url_for('edicao_detalhe', ano=ano))
                else:
                    erro = "Erro ao atualizar o vencedor."
            else:
                erro = "Não foi possível encontrar a edição para este ano."

    q_get = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?c ?titulo ?artista WHERE {{
        ?edicao a :FestivalEdition ; :editionYear ?y .
        FILTER(xsd:integer(?y) = {ano_str})
        ?edicao :hasContestant ?c .
        ?c :performsSong ?s .
        ?s :songTitle ?titulo .
        OPTIONAL {{ ?c :artistName ?artista . }}
    }} ORDER BY ?titulo
    """
    res = exec_query(q_get)
    contestants = []
    if res and "results" in res:
        for row in res['results']['bindings']:
            contestants.append({
                'id': row['c']['value'].split('/')[-1],
                'titulo': row['titulo']['value'],
                'artista': row.get('artista', {}).get('value', 'N/A')
            })

    current_winner_id = ""
    q_current = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?contestant WHERE {{
        ?edicao a :FestivalEdition ; :editionYear ?y ; :hasWinner ?song .
        ?edicao :hasContestant ?contestant .
        ?song :performedBy ?contestant .
        FILTER(xsd:integer(?y) = {ano_str})
    }} LIMIT 1
    """
    current_res = exec_query(q_current)
    if current_res and current_res.get('results', {}).get('bindings'):
        current_winner_id = current_res['results']['bindings'][0]['contestant']['value'].split('/')[-1]

    return render_template('novo_vencedor.html', ano=ano_str, contestants=contestants, current_winner_id=current_winner_id, erro=erro, sucesso=sucesso)


@app.route('/edicao/<ano>/diretor-musical', methods=['GET', 'POST'])
def diretor_musical(ano):
    erro = None
    sucesso = None
    ano_str = str(ano)

    # Diretor atual da edição (se existir)
    q_current = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?nome WHERE {{
        ?edicao a :FestivalEdition ; :editionYear ?y .
        FILTER(xsd:integer(?y) = {ano_str})
        OPTIONAL {{ ?edicao :hasMusicDirector ?md . ?md :personName ?nome . }}
    }} LIMIT 1
    """
    current_res = exec_query(q_current)
    current_director = ""
    if current_res and current_res.get('results', {}).get('bindings'):
        current_director = current_res['results']['bindings'][0].get('nome', {}).get('value', '')

    if request.method == 'POST':
        existing_name = request.form.get('director_existing', '').strip()
        new_name = request.form.get('director_new', '').strip()
        final_name = new_name if new_name else existing_name

        if not final_name:
            erro = "Escolhe um diretor existente ou escreve um novo nome."
        else:
            safe_name = final_name.replace('"', '\\"')
            director_id = f"Person_{slugify(final_name)}"
            q_update = f"""
            PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
            DELETE {{
                :Edition_{ano_str} :hasMusicDirector ?oldMd .
            }}
            INSERT {{
                :{director_id} a :Person ; :personName "{safe_name}" .
                :Edition_{ano_str} :hasMusicDirector :{director_id} .
            }}
            WHERE {{
                OPTIONAL {{ :Edition_{ano_str} :hasMusicDirector ?oldMd . }}
            }}
            """
            if exec_update(q_update):
                return redirect(url_for('edicao_detalhe', ano=ano_str))
            else:
                erro = "Erro ao atualizar o diretor musical."

    q_names = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT DISTINCT ?nome WHERE {{
        {{ ?p :personName ?nome . }}
        UNION
        {{ ?c a :Contestant ; :artistName ?nome . }}
    }}
    ORDER BY ?nome
    """
    names_res = exec_query(q_names)
    nomes = []
    if names_res and names_res.get('results', {}).get('bindings'):
        nomes = [r.get('nome', {}).get('value', 'N/A') for r in names_res['results']['bindings']]

    return render_template(
        'novo_diretor_musical.html',
        ano=ano_str,
        nomes=nomes,
        current_director=current_director,
        erro=erro,
        sucesso=sucesso,
    )


@app.route('/edicao/<ano>/musica/<musica_id>/editar', methods=['GET', 'POST'])
def editar_musica(ano, musica_id):
    erro = None
    sucesso = None
    musica_data = None

    if request.method == 'GET':
        q_get = f"""
        PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
        SELECT ?titulo ?artista ?nomeCompositor ?nomeLiricista WHERE {{
            :{musica_id} :songTitle ?titulo .
            OPTIONAL {{
                {{ :{musica_id} :isPerformedBy ?contestant }}
                UNION
                {{ :{musica_id} :performedBy ?contestant }}
                OPTIONAL {{ ?contestant :artistName ?artista . }}
            }}
            OPTIONAL {{ :{musica_id} :hasComposer ?comp . ?comp :personName ?nomeCompositor . }}
            OPTIONAL {{ :{musica_id} :hasLyricist ?lir . ?lir :personName ?nomeLiricista . }}
        }}
        """
        res = exec_query(q_get)
        if res and res.get('results', {}).get('bindings'):
            rows = res['results']['bindings']
            if rows:
                primeiro = rows[0]
                compositores = [r.get('nomeCompositor', {}).get('value', '') for r in rows if r.get('nomeCompositor', {}).get('value')]
                liricistas = [r.get('nomeLiricista', {}).get('value', '') for r in rows if r.get('nomeLiricista', {}).get('value')]
                musica_data = {
                    'titulo': primeiro.get('titulo', {}).get('value', ''),
                    'artista': primeiro.get('artista', {}).get('value', ''),
                    'compositores': ', '.join(compositores) if compositores else '',
                    'liricistas': ', '.join(liricistas) if liricistas else ''
                }
        
        if not musica_data:
            erro = "Música não encontrada."

    elif request.method == 'POST':
        titulo = request.form.get('titulo', '').strip()
        artista = request.form.get('artista', '').strip()
        compositores = [c.strip() for c in request.form.get('compositores', '').replace('\n', ',').split(',') if c.strip()]
        liricistas = [l.strip() for l in request.form.get('liricistas', '').replace('\n', ',').split(',') if l.strip()]

        q_lookup = f"""
        PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
        SELECT ?contestant WHERE {{
            {{ :{musica_id} :isPerformedBy ?contestant }}
            UNION
            {{ :{musica_id} :performedBy ?contestant }}
            ?contestant a :Contestant .
        }} LIMIT 1
        """
        lookup_res = exec_query(q_lookup)
        
        if not lookup_res or not lookup_res.get('results', {}).get('bindings'):
            erro = "Não foi possível encontrar o participante associado à música."
        else:
            contestant_id = lookup_res['results']['bindings'][0]['contestant']['value'].split('/')[-1]
            
            q_delete_autores = f"""
            PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
            DELETE {{
                :{musica_id} :hasComposer ?comp .
                :{musica_id} :hasLyricist ?lir .
            }}
            WHERE {{
                OPTIONAL {{ :{musica_id} :hasComposer ?comp . }}
                OPTIONAL {{ :{musica_id} :hasLyricist ?lir . }}
            }}
            """
            exec_update(q_delete_autores)
            
            triples_autores = ""
            for c in compositores:
                c_slug = slugify(c)
                triples_autores += f"""
                :Person_{c_slug} a :Person, :Composer ; :personName "{c}" .
                :{musica_id} :hasComposer :Person_{c_slug} .
                """
            
            for l in liricistas:
                l_slug = slugify(l)
                triples_autores += f"""
                :Person_{l_slug} a :Person, :Lyricist ; :personName "{l}" .
                :{musica_id} :hasLyricist :Person_{l_slug} .
                """
            
            q_update = f"""
            PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
            DELETE {{
                :{musica_id} :songTitle ?oldTitulo .
                :{contestant_id} :artistName ?oldArtista .
            }}
            INSERT {{
                :{musica_id} :songTitle "{titulo}" .
                :{contestant_id} :artistName "{artista}" .
                {triples_autores}
            }}
            WHERE {{
                :{musica_id} :songTitle ?oldTitulo .
                :{contestant_id} :artistName ?oldArtista .
            }}
            """
            
            if exec_update(q_update):
                return redirect(url_for('edicao_detalhe', ano=ano))
            else:
                erro = "Erro ao atualizar a música."

    return render_template('editar_musica.html', ano=ano, musica_id=musica_id, musica_data=musica_data, erro=erro, sucesso=sucesso)


@app.route('/edicao/<ano>/musica/<musica_id>/apagar', methods=['POST'])
def apagar_musica(ano, musica_id):
    q_lookup = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?contestant ?edicao WHERE {{
        ?edicao a :FestivalEdition ; :editionYear ?ano ;
                :hasContestant ?contestant .
        {{ :{musica_id} :isPerformedBy ?contestant }}
        UNION
        {{ :{musica_id} :performedBy ?contestant }}
        FILTER(STR(?ano) = "{ano}")
    }} LIMIT 1
    """
    lookup_res = exec_query(q_lookup)
    
    if lookup_res and lookup_res.get('results', {}).get('bindings'):
        contestant = lookup_res['results']['bindings'][0]['contestant']['value']
        edicao = lookup_res['results']['bindings'][0]['edicao']['value']
        contestant_id = contestant.split('/')[-1]
        
        q_delete = f"""
        PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
        DELETE {{
            :{musica_id} ?p1 ?o1 .
            ?comp ?p2 ?o2 .
            ?lir ?p3 ?o3 .
            :{contestant_id} ?p4 ?o4 .
            <{edicao}> :hasContestant :{contestant_id} .
        }}
        WHERE {{
            :{musica_id} ?p1 ?o1 .
            OPTIONAL {{ :{musica_id} :hasComposer ?comp . ?comp ?p2 ?o2 . }}
            OPTIONAL {{ :{musica_id} :hasLyricist ?lir . ?lir ?p3 ?o3 . }}
            :{contestant_id} ?p4 ?o4 .
        }}
        """
        
        if exec_update(q_delete):
            return {"status": "success", "message": "Música apagada com sucesso!"}, 200
        else:
            return {"status": "error", "message": "Erro ao apagar a música."}, 500
    else:
        return {"status": "error", "message": "Música não encontrada."}, 404
    

@app.route('/edicao/<ano>/fase/<int:fase_index>/editar', methods=['GET', 'POST'])
def editar_fase(ano, fase_index):
    erro = None
    sucesso = None
    fase_data = None

    if request.method == 'GET':
        q_fases = f"""
        PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
        SELECT ?fase ?tipo ?data ?local ?cidade
               (GROUP_CONCAT(DISTINCT ?apNome; separator="|") AS ?apresentadores)
        WHERE {{
            ?edicao a :FestivalEdition ;
                    :editionYear ?ano_val ;
                    :hasPhase ?fase .
            FILTER(STR(?ano_val) = "{ano}")
            BIND(IF(EXISTS {{ ?fase a :Final }}, "Final", "Semi-final") AS ?tipo)
            OPTIONAL {{ ?fase :phaseDate ?data . }}
            OPTIONAL {{
                ?fase :heldAt ?venue .
                ?venue :venueName ?local .
                OPTIONAL {{
                    ?venue :locatedIn ?city .
                    ?city :cityName ?cidade .
                }}
            }}
            OPTIONAL {{
                ?fase :hasPresenter ?ap .
                ?ap :personName ?apNome .
            }}
        }}
        GROUP BY ?fase ?tipo ?data ?local ?cidade
        ORDER BY ?tipo ?data
        """
        fases_res = exec_query(q_fases)
    
        if fases_res and fases_res.get('results', {}).get('bindings'):
            fases = fases_res['results']['bindings']
            if fase_index < len(fases):
                f = fases[fase_index]
                apresentadores_raw = f.get('apresentadores', {}).get('value', '')
                apresentadores_list = [a.strip() for a in apresentadores_raw.split('|') if a.strip()]
            
                fase_data = {
                    'tipo': f.get('tipo', {}).get('value', 'N/A'),
                    'data': f.get('data', {}).get('value', ''),
                    'local': f.get('local', {}).get('value', ''),
                    'cidade': f.get('cidade', {}).get('value', ''),
                    'apresentadores': '\n'.join(apresentadores_list),
                    'fase_uri': f.get('fase', {}).get('value', '')
                }
            else:
                erro = "Fase não encontrada."

    elif request.method == 'POST':
        tipo = request.form.get('tipo')
        data = request.form.get('data')
        local = request.form.get('local')
        cidade = request.form.get('cidade')
        apresentadores_raw = request.form.get('apresentadores', '')
    
        apresentadores = [a.strip() for a in apresentadores_raw.splitlines() if a.strip()]
    
        q_fases = f"""
        PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
        SELECT ?fase WHERE {{
            ?edicao a :FestivalEdition ;
                    :editionYear ?ano_val ;
                    :hasPhase ?fase .
            FILTER(STR(?ano_val) = "{ano}")
        }}
        ORDER BY ?fase LIMIT {fase_index + 1}
        """
        fases_res = exec_query(q_fases)
    
        if fases_res and fases_res.get('results', {}).get('bindings'):
            fases_list = fases_res['results']['bindings']
            if fase_index < len(fases_list):
                fase_uri = fases_list[fase_index]['fase']['value']
                fase_id = fase_uri.split('/')[-1]
            
                uid = uuid.uuid4().hex[:4]
                venue_id = f"Venue_{local.replace(' ', '_')}_{uid}"
                city_id = f"City_{cidade.replace(' ', '_')}"
            
                triples_apresentadores = ""
                for ap in apresentadores:
                    ap_uri = "Person_" + ap.replace(" ", "_")
                    triples_apresentadores += f"""
                    :{ap_uri} a :Person ; :personName "{ap}" .
                    :{fase_id} :hasPresenter :{ap_uri} .
                    """
            
                q_delete_ap = f"""
                PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
                DELETE {{
                    :{fase_id} :hasPresenter ?ap .
                }}
                WHERE {{
                    OPTIONAL {{ :{fase_id} :hasPresenter ?ap . }}
                }}
                """
                exec_update(q_delete_ap)
            
                q_update = f"""
                PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
                DELETE {{
                    :{fase_id} :phaseDate ?oldData .
                    :{fase_id} :heldAt ?oldVenue .
                }}
                INSERT {{
                    :{fase_id} :phaseDate "{data}" ;
                        :heldAt :{venue_id} .
                
                    :{city_id} a :City ; :cityName "{cidade}" .
                    :{venue_id} a :Venue ; :venueName "{local}" ; :locatedIn :{city_id} .
                
                    {triples_apresentadores}
                }}
                WHERE {{
                    OPTIONAL {{ :{fase_id} :phaseDate ?oldData . }}
                    OPTIONAL {{ :{fase_id} :heldAt ?oldVenue . }}
                }}
                """
            
                if exec_update(q_update):
                    return redirect(url_for('edicao_detalhe', ano=ano))
                else:
                    erro = "Erro ao atualizar a fase."
            else:
                erro = "Fase não encontrada."
    q_fases = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?fase ?tipo ?data ?local ?cidade
           (GROUP_CONCAT(DISTINCT ?apNome; separator="|") AS ?apresentadores)
    WHERE {{
        ?edicao a :FestivalEdition ;
                :editionYear ?ano_val ;
                :hasPhase ?fase .
        FILTER(STR(?ano_val) = "{ano}")
        BIND(IF(EXISTS {{ ?fase a :Final }}, "Final", "Semi-final") AS ?tipo)
        OPTIONAL {{ ?fase :phaseDate ?data . }}
        OPTIONAL {{
            ?fase :heldAt ?venue .
            ?venue :venueName ?local .
            OPTIONAL {{
                ?venue :locatedIn ?city .
                ?city :cityName ?cidade .
            }}
        }}
        OPTIONAL {{
            ?fase :hasPresenter ?ap .
            ?ap :personName ?apNome .
        }}
    }}
    GROUP BY ?fase ?tipo ?data ?local ?cidade
    ORDER BY ?tipo ?data
    """
    fases_res = exec_query(q_fases)
    
    if fases_res and fases_res.get('results', {}).get('bindings'):
        fases = fases_res['results']['bindings']
        if fase_index < len(fases):
            f = fases[fase_index]
            apresentadores_raw = f.get('apresentadores', {}).get('value', '')
            apresentadores_list = [a.strip() for a in apresentadores_raw.split('|') if a.strip()]
            
            fase_data = {
                'tipo': f.get('tipo', {}).get('value', 'N/A'),
                'data': f.get('data', {}).get('value', ''),
                'local': f.get('local', {}).get('value', ''),
                'cidade': f.get('cidade', {}).get('value', ''),
                'apresentadores': '\n'.join(apresentadores_list)
            }

    return render_template('editar_fase.html', ano=ano, fase_index=fase_index, fase_data=fase_data, erro=erro, sucesso=sucesso)

@app.route('/edicao/<ano>/fase/<int:fase_index>/apagar', methods=['POST'])
def apagar_fase(ano, fase_index):
    q_fases = f"""
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
    SELECT ?fase ?venue WHERE {{
        ?edicao a :FestivalEdition ;
                :editionYear ?ano_val ;
                :hasPhase ?fase .
        FILTER(STR(?ano_val) = "{ano}")
        OPTIONAL {{ ?fase :heldAt ?venue . }}
    }}
    ORDER BY ?fase LIMIT {fase_index + 1}
    """
    fases_res = exec_query(q_fases)

    if fases_res and fases_res.get('results', {}).get('bindings'):
        fases_list = fases_res['results']['bindings']
        if fase_index < len(fases_list):
            fase_uri = fases_list[fase_index]['fase']['value']
            fase_id = fase_uri.split('/')[-1]
        
            q_delete = f"""
            PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
            DELETE {{
                :{fase_id} ?p1 ?o1 .
                :Edition_{ano} :hasPhase :{fase_id} .
            }}
            WHERE {{
                :{fase_id} ?p1 ?o1 .
            }}
            """
        
            if exec_update(q_delete):
                return {"status": "success", "message": "Fase apagada com sucesso!"}, 200
            else:
                return {"status": "error", "message": "Erro ao apagar a fase."}, 500

    return {"status": "error", "message": "Fase não encontrada."}, 404

if __name__ == '__main__':    
    app.run(debug=True, port=5000)