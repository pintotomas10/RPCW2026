# Questão 1 — Livros por linha temporal
1. Liste todos os livros que existem na linha temporal original (LinhaOriginal).
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/biblioteca_temporal/>
SELECT ?livro WHERE {
    ?livro :existeEm ?linha .
    ?linha a :LinhaOriginal .
}
```

# Questão 2 — Livros em múltiplas linhas temporais
2. Identifique os livros que existem em mais do que uma linha temporal.
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/biblioteca_temporal/>
SELECT ?livro WHERE {
    ?livro :existeEm ?linha .
}
GROUP BY ?livro
HAVING (COUNT(?linha) > 1)
```

# Questão 3 — Livros paradoxais
3. Liste todos os livros classificados como LivroParadoxal.
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/biblioteca_temporal/>
SELECT ?livro WHERE {
    ?livro a :LivroParodoxal .
}
```

# Questão 4 — Livros históricos e eventos
4. Para cada LivroHistorico, indique os eventos históricos que esse livro refere.
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/biblioteca_temporal/>
SELECT ?livro ?evento WHERE {
    ?livro a :LivroHistórico .
    ?evento a :EventoHistórico .
    ?livro :refere ?evento .
}
```

# Questão 5 — Inconsistências semânticas
5. Identifique livros classificados como LivroHistorico que referem eventos futuros.
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/biblioteca_temporal/>
SELECT ?livro ?evento WHERE {
    ?livro a :LivroHistórico .
    ?evento a :EventoFuturo .
    ?livro :refere ?evento .
}
```

# Questão 6 — Autores mais prolíficos
6. Liste os autores e o número de livros que escreveram, ordenando o resultado por número de livros em ordem decrescente.
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/biblioteca_temporal/>
SELECT ?autor (COUNT(DISTINCT ?livro) as ?nLivros) WHERE {
    ?livro :éEscritoPor ?autor .
}
GROUP BY ?autor
ORDER BY desc(?nLivros)
```

# Questão 7 — Autores de livros paradoxais
7. Identifique os autores que escreveram pelo menos um livro paradoxal.
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/biblioteca_temporal/>
SELECT DISTINCT ?autor WHERE {
    ?livro :éEscritoPor ?autor .
    ?livro a :LivroParodoxal .
}
ORDER BY ?autor
```

# Questão 8 — Livros em linhas alternativas
8. Liste todos os livros que existem em pelo menos uma linha temporal alternativa (LinhaAlternativa).
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/biblioteca_temporal/>
SELECT DISTINCT ?livro ?linha WHERE {
    ?livro :existeEm ?linha .
    ?linha a :LinhaAlternativa .
}
```

# Questão 9 — Bibliotecários
9. Indique todos os bibliotecários e a biblioteca onde trabalham.
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/biblioteca_temporal/>
SELECT ?pessoa ?biblioteca WHERE {
    ?pessoa a :Bibliotecário .
    ?pessoa :trabalhaEm ?biblioteca .
}
```

# Questão 10 — Livros escritos por Cronos
10. Liste todos os livros escritos por Cronos e indique em que linhas temporais esses livros existem.
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/biblioteca_temporal/>
SELECT ?livro ?linha WHERE {
    ?livro :éEscritoPor :Cronos .
    ?livro :existeEm ?linha .
}
```

# Questões Bónus (opcionais)
1. Identifique livros que não referem nenhum evento.
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/biblioteca_temporal/>
SELECT ?livro WHERE {
    ?livro a :Livro .
    FILTER NOT EXISTS { ?livro :refere ?evento . }
}
ORDER BY ?livro
```

2. Verifique se existe algum livro sem linha temporal associada.
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/biblioteca_temporal/>
SELECT ?livro WHERE {
    ?livro :pertenteA ?biblioteca .
    FILTER NOT EXISTS { ?livro :existeEm ?linha . }
}
```

3. Identifique autores que sejam também leitores (caso essa propriedade esteja modelada).
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/biblioteca_temporal/>
SELECT DISTINCT ?pessoa WHERE {
    ?pessoa a :Autor .
    ?pessoa a :Leitor .
}
```

4. Ordenar por ordem decrescente os autores que escreveram pelo menos um livro paradoxal.
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/biblioteca_temporal/>
SELECT ?autor (COUNT(DISTINCT ?livro) as ?nLivros) WHERE {
    ?livro :éEscritoPor ?autor .
    ?livro a :LivroParodoxal .
}
GROUP BY ?autor
ORDER BY desc(?nLivros)
```
