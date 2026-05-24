# Algumas queries para testar

### 1. Listar todas as musicas
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
SELECT ?ano ?titulo WHERE {
    ?edicao :editionYear ?ano .
    ?concorrente :belongsToEdition ?edicao .
    ?concorrente :performsSong ?musica .
    ?musica :songTitle ?titulo .
}
```

### 2. Lista de Músicas por Compositor
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
SELECT ?nomeCompositor (GROUP_CONCAT(?tituloMusica; separator=" | ") AS ?listaMusicas) WHERE {
    ?musica a :Song ;
            :songTitle ?tituloMusica ;
            :hasComposer ?compositor .
    ?compositor :personName ?nomeCompositor .
}
GROUP BY ?nomeCompositor
ORDER BY ?nomeCompositor
```

### 3. Lista de Vencedores
```sparql
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>

SELECT ?ano ?titulo ?resultado WHERE {
    ?edicao :editionYear ?ano .
    ?edicao :hasWinner ?musica .
    
    ?musica :songTitle ?titulo ;
            :eurovisionResult ?resultado .
}
```

### 4. Lista de Compositores e Letristas
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
SELECT ?titulo 
       (GROUP_CONCAT(DISTINCT ?nomeCompositor; separator=" | ") AS ?listaCompositores)
       (GROUP_CONCAT(DISTINCT ?nomeLetrista; separator=" | ") AS ?listaLetristas) WHERE {
    ?musica a :Song ;
            :songTitle ?titulo .
    OPTIONAL {
        ?musica :hasComposer ?c .
        ?c :personName ?nomeCompositor .
    }
    OPTIONAL {
        ?musica :hasLyricist ?l .
        ?l :personName ?nomeLetrista .
    }
}
GROUP BY ?titulo
ORDER BY ?titulo
```

### 5. Lista de anos
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
SELECT DISTINCT ?ano WHERE {
    ?edicao a :FestivalEdition ;
            :editionYear ?ano .
}
ORDER BY DESC(?ano)
```

### 6. Top 5 compositores
```sparql
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
SELECT ?nomeCompositor (COUNT(?musica) AS ?totalMusicas) WHERE {
    ?musica :hasComposer ?compositor .
    ?compositor :personName ?nomeCompositor .
}
GROUP BY ?nomeCompositor
ORDER BY DESC(?totalMusicas)
LIMIT 5
```

### 7. Lugar e Apresentadores de cada Final e SemiFinal
```sparql
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX : <http://www.semanticweb.org/utilizador/ontologies/2026/festival_da_cancao/>
SELECT ?f ?venue ?cidade (GROUP_CONCAT(?nomePres; separator=", ") AS ?apresentadores) WHERE {
    ?edicao :editionYear ?ano .
    OPTIONAL {
        ?edicao :hasPhase ?f .
        ?f :heldAt ?v .
        ?v :venueName ?venue .
        ?v :locatedIn ?c .
        ?c :cityName ?cidade .
    }
    OPTIONAL {
        ?edicao :hasPhase ?f .
        ?f :hasPresenter ?p .
        ?p :personName ?nomePres .
    }
}
GROUP BY ?f ?venue ?cidade
```