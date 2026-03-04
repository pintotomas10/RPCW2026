import rdflib  # type: ignore
import sys

# Configure UTF-8 encoding for terminal output
sys.stdout.reconfigure(encoding='utf-8')

def run_queries(output_file=None):
    # Open output file if specified
    file_handle = None
    if output_file:
        file_handle = open(output_file, 'w', encoding='utf-8')
    
    def print_output(text=""):
        """Print to both terminal and file if specified"""
        print(text)
        if file_handle:
            file_handle.write(text + '\n')
    
    # 1. Criar o grafo e carregar a ontologia
    g = rdflib.Graph()
    try:
        g.parse("bibliotecaTemporal_povoada.ttl", format="ttl")
        print_output(f"✓ Ontologia carregada com sucesso\n")
    except Exception as e:
        print_output(f"Erro ao carregar o ficheiro: {e}")
        if file_handle:
            file_handle.close()
        return

    # Definir o prefixo para as queries
    PREFIX = """
    PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/biblioteca_temporal/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX owl: <http://www.w3.org/2002/07/owl#>
    """

    # --- Query 1: Livros por linha temporal ---
    print_output("=" * 70)
    print_output("QUESTÃO 1 — Livros por linha temporal")
    print_output("=" * 70)
    print_output("Liste todos os livros que existem na linha temporal original (LinhaOriginal).\n")
    q1 = PREFIX + """
    SELECT ?livro WHERE {
        ?livro :existeEm ?linha .
        ?linha a :LinhaOriginal .
    }
    """
    results = list(g.query(q1))
    print_output(f"Resultados: {len(results)} livros\n")
    for i, row in enumerate(results, 1):
        nome = str(row.livro).split('/')[-1]
        print_output(f"{i}. {nome}")

    # --- Query 2: Livros em múltiplas linhas temporais ---
    print_output("\n" + "=" * 70)
    print_output("QUESTÃO 2 — Livros em múltiplas linhas temporais")
    print_output("=" * 70)
    print_output("Identifique os livros que existem em mais do que uma linha temporal.\n")
    q2 = PREFIX + """
    SELECT ?livro (COUNT(?linha) as ?nLinhas) WHERE {
        ?livro :existeEm ?linha .
    }
    GROUP BY ?livro
    HAVING (COUNT(?linha) > 1)
    """
    results = list(g.query(q2))
    print_output(f"Resultados: {len(results)} livros\n")
    for i, row in enumerate(results, 1):
        nome = str(row.livro).split('/')[-1]
        print_output(f"{i}. {nome} — {row.nLinhas} linhas temporais")

    # --- Query 3: Livros paradoxais ---
    print_output("\n" + "=" * 70)
    print_output("QUESTÃO 3 — Livros paradoxais")
    print_output("=" * 70)
    print_output("Liste todos os livros classificados como LivroParodoxal.\n")
    q3 = PREFIX + """
    SELECT ?livro WHERE {
        ?livro a :LivroParodoxal .
    }
    """
    results = list(g.query(q3))
    print_output(f"Resultados: {len(results)} livros\n")
    for i, row in enumerate(results, 1):
        nome = str(row.livro).split('/')[-1]
        print_output(f"{i}. {nome}")

    # --- Query 4: Livros históricos e eventos ---
    print_output("\n" + "=" * 70)
    print_output("QUESTÃO 4 — Livros históricos e eventos")
    print_output("=" * 70)
    print_output("Para cada LivroHistorico, indique os eventos históricos que esse livro refere.\n")
    q4 = PREFIX + """
    SELECT ?livro ?evento WHERE {
        ?livro a :LivroHistórico .
        ?evento a :EventoHistórico .
        ?livro :refere ?evento .
    }
    ORDER BY ?livro
    """
    results = list(g.query(q4))
    print_output(f"Resultados: {len(results)} relações\n")
    current_livro = None
    for i, row in enumerate(results, 1):
        livro_nome = str(row.livro).split('/')[-1]
        evento_nome = str(row.evento).split('/')[-1]
        if livro_nome != current_livro:
            if current_livro is not None:
                print_output()
            print_output(f"{livro_nome}:")
            current_livro = livro_nome
        print_output(f"  → {evento_nome}")

    # --- Query 5: Inconsistências semânticas ---
    print_output("\n" + "=" * 70)
    print_output("QUESTÃO 5 — Inconsistências semânticas")
    print_output("=" * 70)
    print_output("Identifique livros classificados como LivroHistorico que referem eventos futuros.\n")
    q5 = PREFIX + """
    SELECT ?livro ?evento WHERE {
        ?livro a :LivroHistórico .
        ?evento a :EventoFuturo .
        ?livro :refere ?evento .
    }
    """
    results = list(g.query(q5))
    print_output(f"Resultados: {len(results)} inconsistências\n")
    if len(results) == 0:
        print_output("✓ Nenhuma inconsistência encontrada!")
    else:
        for i, row in enumerate(results, 1):
            livro_nome = str(row.livro).split('/')[-1]
            evento_nome = str(row.evento).split('/')[-1]
            print_output(f"{i}. {livro_nome} → {evento_nome}")

    # --- Query 6: Autores mais prolíficos ---
    print_output("\n" + "=" * 70)
    print_output("QUESTÃO 6 — Autores mais prolíficos")
    print_output("=" * 70)
    print_output("Liste os autores e o número de livros que escreveram,\nordenando o resultado por número de livros em ordem decrescente.\n")
    q6 = PREFIX + """
    SELECT ?autor (COUNT(DISTINCT ?livro) as ?nLivros) WHERE {
        ?livro :éEscritoPor ?autor .
    }
    GROUP BY ?autor
    ORDER BY desc(?nLivros)
    """
    results = list(g.query(q6))
    print_output(f"Resultados: {len(results)} autores\n")
    for i, row in enumerate(results, 1):
        autor_nome = str(row.autor).split('/')[-1]
        print_output(f"{i}. {autor_nome} — {row.nLivros} livro(s)")

    # --- Query 7: Autores de livros paradoxais ---
    print_output("\n" + "=" * 70)
    print_output("QUESTÃO 7 — Autores de livros paradoxais")
    print_output("=" * 70)
    print_output("Identifique os autores que escreveram pelo menos um livro paradoxal.\n")
    q7 = PREFIX + """
    SELECT DISTINCT ?autor WHERE {
        ?livro :éEscritoPor ?autor .
        ?livro a :LivroParodoxal .
    }
    ORDER BY ?autor
    """
    results = list(g.query(q7))
    print_output(f"Resultados: {len(results)} autores\n")
    for i, row in enumerate(results, 1):
        autor_nome = str(row.autor).split('/')[-1]
        print_output(f"{i}. {autor_nome}")

    # --- Query 8: Livros em linhas alternativas ---
    print_output("\n" + "=" * 70)
    print_output("QUESTÃO 8 — Livros em linhas alternativas")
    print_output("=" * 70)
    print_output("Liste todos os livros que existem em pelo menos uma linha temporal alternativa.\n")
    q8 = PREFIX + """
    SELECT DISTINCT ?livro ?linha WHERE {
        ?livro :existeEm ?linha .
        ?linha a :LinhaAlternativa .
    }
    ORDER BY ?livro
    """
    results = list(g.query(q8))
    print_output(f"Resultados: {len(results)} livros\n")
    current_livro = None
    for i, row in enumerate(results, 1):
        livro_nome = str(row.livro).split('/')[-1]
        linha_nome = str(row.linha).split('/')[-1]
        if livro_nome != current_livro:
            if current_livro is not None:
                print_output()
            print_output(f"{livro_nome}:")
            current_livro = livro_nome
        print_output(f"  → {linha_nome}")

    # --- Query 9: Bibliotecários ---
    print_output("\n" + "=" * 70)
    print_output("QUESTÃO 9 — Bibliotecários")
    print_output("=" * 70)
    print_output("Indique todos os bibliotecários e a biblioteca onde trabalham.\n")
    q9 = PREFIX + """
    SELECT ?pessoa ?biblioteca WHERE {
        ?pessoa a :Bibliotecário .
        ?pessoa :trabalhaEm ?biblioteca .
    }
    ORDER BY ?pessoa
    """
    results = list(g.query(q9))
    print_output(f"Resultados: {len(results)} bibliotecários\n")
    for i, row in enumerate(results, 1):
        pessoa_nome = str(row.pessoa).split('/')[-1]
        bib_nome = str(row.biblioteca).split('/')[-1]
        print_output(f"{i}. {pessoa_nome} → {bib_nome}")

    # --- Query 10: Livros escritos por Cronos ---
    print_output("\n" + "=" * 70)
    print_output("QUESTÃO 10 — Livros escritos por Cronos")
    print_output("=" * 70)
    print_output("Liste todos os livros escritos por Cronos e indique em que linhas temporais esses livros existem.\n")
    q10 = PREFIX + """
    SELECT ?livro ?linha WHERE {
        ?livro :éEscritoPor :Cronos .
        ?livro :existeEm ?linha .
    }
    ORDER BY ?livro
    """
    results = list(g.query(q10))
    print_output(f"Resultados: {len(results)} livros\n")
    if len(results) == 0:
        print_output("✗ Cronos não escreveu nenhum livro no dataset.")
    else:
        for i, row in enumerate(results, 1):
            livro_nome = str(row.livro).split('/')[-1]
            linha_nome = str(row.linha).split('/')[-1]
            print_output(f"{i}. {livro_nome} → {linha_nome}")

    # --- Bonus Query 1: Livros que não referem nenhum evento ---
    print_output("\n" + "=" * 70)
    print_output("QUESTÃO BÔNUS 1 — Livros sem eventos referenciados")
    print_output("=" * 70)
    print_output("Identifique livros que não referem nenhum evento.\n")
    qb1 = PREFIX + """
    SELECT ?livro WHERE {
        ?livro a :Livro .
        FILTER NOT EXISTS { ?livro :refere ?evento . }
    }
    ORDER BY ?livro
    """
    results = list(g.query(qb1))
    print_output(f"Resultados: {len(results)} livros\n")
    if len(results) == 0:
        print_output("✓ Todos os livros referem pelo menos um evento!")
    else:
        for i, row in enumerate(results, 1):
            livro_nome = str(row.livro).split('/')[-1]
            print_output(f"{i}. {livro_nome}")

    # --- Bonus Query 2: Livros sem linha temporal ---
    print_output("\n" + "=" * 70)
    print_output("QUESTÃO BÔNUS 2 — Livros sem linha temporal")
    print_output("=" * 70)
    print_output("Verifique se existe algum livro sem linha temporal associada.\n")
    qb2 = PREFIX + """
    SELECT ?livro WHERE {
        ?livro :pertenteA ?biblioteca .
        FILTER NOT EXISTS { ?livro :existeEm ?linha . }
    }
    """
    results = list(g.query(qb2))
    print_output(f"Resultados: {len(results)} livros\n")
    if len(results) == 0:
        print_output("✓ Todos os livros tém uma linha temporal associada!")
    else:
        for i, row in enumerate(results, 1):
            livro_nome = str(row.livro).split('/')[-1]
            print_output(f"{i}. {livro_nome}")

    # --- Bonus Query 3: Autores que são também leitores ---
    print_output("\n" + "=" * 70)
    print_output("QUESTÃO BÔNUS 3 — Autores que são também leitores")
    print_output("=" * 70)
    print_output("Identifique autores que sejam também leitores.\n")
    qb3 = PREFIX + """
    SELECT DISTINCT ?pessoa WHERE {
        ?pessoa a :Autor .
        ?pessoa a :Leitor .
    }
    """
    results = list(g.query(qb3))
    print_output(f"Resultados: {len(results)} pessoas\n")
    if len(results) == 0:
        print_output("✗ Nenhuma pessoa é simultaneamente Autor e Leitor.")
    else:
        for i, row in enumerate(results, 1):
            pessoa_nome = str(row.pessoa).split('/')[-1]
            print_output(f"{i}. {pessoa_nome}")

    # --- Bonus Query 4: Autores de livros paradoxais com contagem ---
    # --- Bonus Query 4: Autores de livros paradoxais com contagem ---
    print_output("\n" + "=" * 70)
    print_output("QUESTÃO BÓNUS 4 — Autores de livros paradoxais (por quantidade)")
    print_output("=" * 70)
    print_output("Ordenar por ordem decrescente os autores que escreveram pelo menos um livro paradoxal.\n")
    qb4 = PREFIX + """
    SELECT ?autor (COUNT(DISTINCT ?livro) as ?nLivros) WHERE {
        ?livro :éEscritoPor ?autor .
        ?livro a :LivroParodoxal .
    }
    GROUP BY ?autor
    ORDER BY desc(?nLivros)
    """
    results = list(g.query(qb4))
    print_output(f"Resultados: {len(results)} autores\n")
    if len(results) == 0:
        print_output("✗ Nenhum autor escreveu livros paradoxais.")
    else:
        for i, row in enumerate(results, 1):
            autor_nome = str(row.autor).split('/')[-1]
            print_output(f"{i}. {autor_nome} — {row.nLivros} livro(s) paradoxal(is)")

    print_output("\n" + "=" * 70)
    print_output("✓ Todas as queries executadas com sucesso!")
    print_output("=" * 70)
    
    # Close file if it was opened
    if file_handle:
        file_handle.close()
        print(f"\n✓ Resultados salvos em '{output_file}'")

if __name__ == "__main__":
    import sys
    
    # Check if output file was specified as argument
    output_file = sys.argv[1] if len(sys.argv) > 1 else None
    run_queries(output_file)
