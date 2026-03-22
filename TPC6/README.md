# Manifesto: TPC6 - Biblioteca Temporal - Aplicação Web

**Data:** 2026-03-22

## Resumo
Neste trabalho foi desenvolvida uma aplicação web em Flask para exploração de uma ontologia OWL de Biblioteca Temporal, com dados armazenados no GraphDB e consultados por SPARQL. O sistema permite:
- Listar livros do catálogo, consultar o detalhe de cada livro (autor, país, linha temporal e evento associado)
- Visualizar os eventos existentes com ligação aos livros que os referenciam
- Listar todas as linhas temporais, consultar o detalhe de cada linha (com todos os livros nela existentes)

---

## Estrutura do Projeto

```text
TPC6/
|- app.py                  # Rotas Flask e transformação dos resultados SPARQL
|- mquery.py               # Módulo auxiliar para executar queries SPARQL no GraphDB
|- templates/
|  |- layout.html          # Template base com navbar e footer
|  |- lista.html           # Página de catálogo de livros
|  |- livro.html           # Página de detalhe de um livro
|  |- eventos.html         # Página de listagem de eventos
|  |- linhas.html          # Página de listagem de linhas temporais
|  |- linha.html           # Página de detalhe de uma linha temporal
|  |- index.html           # Template auxiliar (não usado nas rotas atuais)
|- static/
|  |- livro.png            # Ícone da aplicação usado no layout
```

---

## Ontologia

A aplicação consulta a ontologia no namespace:

- `http://example.org/biblioteca-temporal#`

Pelos dados e queries implementadas, as entidades centrais são:

- `Livro` (incluindo `LivroHistorico`, `LivroFiccional`, `LivroParadoxal`)
- `Autor`
- `Evento`
- `LinhaTemporal`

Relações utilizadas pela aplicação:

- `:escritoPor` - livro -> autor
- `:titulo` - titulo do livro
- `:paisOrigem` - pais do autor
- `:refereEvento` - livro -> evento
- `:designacao` e `:descricao` - metadados do evento
- `:existeEm` - livro -> linha temporal

---

## Rotas Implementadas

### `GET /`
Lista os livros do catálogo, filtrando os tipos `LivroHistorico`, `LivroFiccional` e `LivroParadoxal`, ordenados por título.

Para cada livro são apresentados:

- Título (com link para detalhe)
- Tipo
- Autor
- País de origem do autor

### `GET /livro/<id_livro>`
Mostra o detalhe de um livro específico, identificado pelo fragmento do URI (ID local).

Inclui:

- ID
- Título
- Tipo
- Autor
- País
- Linha temporal (quando existe)
- Evento relacionado (ID, nome e descrição, quando existe)

### `GET /eventos`
Lista todos os eventos (`:Evento`) ordenados por designação.

Para cada evento mostra:

- ID
- Designação
- Descrição
- IDs dos livros que referem o evento (com links para o detalhe de cada livro)

### `GET /linhas`
Mostra todas as linhas temporais existentes.

- Para cada linha, apresenta o seu ID (como link para a página da linha) e a lista dos IDs dos livros que nela existem (cada um como link para a página do livro).

### `GET /linha/<id_linha>`
Mostra o detalhe de uma linha temporal específica, identificada pelo seu ID.

Inclui:
- ID da linha
- Tabela com todos os livros dessa linha (ID do livro como link, título e tipo de livro)

---

## Como Executar

1. Garantir que o GraphDB está a correr localmente na porta `7200`.

2. Criar (ou usar) um repositório chamado `biblioteca_temporal`.

3. Carregar no repositório a ontologia/dados `.ttl` correspondentes ao domínio da Biblioteca Temporal.

4. Instalar as dependências Python:

```bash
pip install flask SPARQLWrapper
```

5. Iniciar a aplicação:

```bash
python app.py
```

6. Abrir no browser:

- `http://localhost:5000/`

--- 

## Autor

> **Nome:** Tomás Pinto Rodrigues

> **ID:** A104448

> **Foto:**

>![Foto Perfil](https://github.com/user-attachments/assets/93c3244b-7485-481b-8ae0-d92d039f5cf2)

