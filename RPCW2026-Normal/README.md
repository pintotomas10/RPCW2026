# RPCW2026-Normal

## Autor

> **Nome:** Tomás Pinto Rodrigues

> **ID:** A104448

---

## Exercício 1: Extração de Conhecimento de uma Fábula

Neste exercício, foi analisada a fábula "O Corvo e a Raposa" para extrair entidades, propriedades e sentimentos, vertidos numa ontologia semântica.

### 1. Criação da Ontologia (`fabula.ttl`)
* **Ferramenta:** Protégé.
* **Modelação:** * Criação das classes principais (`Animal`, `Local`, `Objeto`, `Sentimento`).
  * Definição de sub-classes (ex: `Corvo` e `Raposa` como sub-classes de `Animal`).
  * Propriedades de Objeto (Object Properties): `:enganou`, `:localizadoEm`, `:segura`, `:sente`.
  * Propriedades de Dados (Data Properties): `:nome`, `:espécie`.
  * Criação e caracterização dos indivíduos correspondentes à história (`Mestre_Corvo`, `Mestre_Raposa`, `Queijo_Apetitoso`, `Ramo_Árvore`, etc.).

### 2. Execução de Queries no GraphDB (`queries.txt`)
A ontologia foi carregada num repositório local do GraphDB, onde foram executadas e validadas as queries SPARQL correspondentes às alíneas do enunciado. O conjunto completo de queries encontra-se no ficheiro [queries.txt](queries.txt).

---

## Exercício 2: Catálogo de Boardgames

Este exercício envolveu o desenho completo de um domínio de jogos de tabuleiro, a migração incremental de dados a partir de ficheiros JSON usando scripts Python e interrogação analítica complexa.

### 1. Ontologia Base (`boardgames_base.ttl`)
Criada de raiz no Protégé com os seguintes dados:
* **Classes:** `Jogo`, `Autor`, `Editora`, `Mecanica`, `Premio`.
* **Object Properties:** `:desenhou` / `:desenhadoPor` (inversas), `:publicou`, `:usadaEm`, `:ganhoPor`.
* **Data Properties:** `:nome`, `:categoria`, `:minJogadores`, `:maxJogadores`, `:tempoJogoMin`, `:descricao`, `:pais`, `:ano`.
* **IRI Base Garantido:** `http://www.di.uminho.pt/rpcw2026/A104448#` 

### 2. Povoamento Incremental Automático (Scripts Python)
Para não corromper dados e garantir isolamento de erros, o povoamento da foi feito de forma modular e incremental através de scripts Python que leem os ficheiros `.json` e anexam os indivíduos no formato Turtle.
* **Normalização de IDs:** Todos os scripts implementam uma função `limpa_id` que converte hífens (`-`) em underscores (`_`), garantindo que URIs como `:ticket_to_ride` e `:klaus_teuber` fiquem normalizados para a ontologia e futuras rotas da aplicação web.
* **Pipeline de Execução:**
  1. `povoar_jogos.py`: Lê `jogos.json`, extrai os dados, limpa as strings e descrições, e cria o ficheiro `boardgames_jogos.ttl` combinando a base e os indivíduos dos jogos.
  2. `povoar_autores.py`: Lê `autores.json`, consome o `boardgames_jogos.ttl`, anexa os autores ligando-os aos respetivos jogos via propriedade `:desenhou`, e exporta para `boardgames_autores.ttl`.
  3. `povoar_editoras.py`: Lê `editoras.json`, consome o ficheiro anterior, injeta as editoras mapeando as propriedades `:pais` e `:publicou`, gerando o `boardgames_editoras.ttl`.
  4. `povoar_mecanicas.py`: Lê `mecanicas.json`, consome o ficheiro anterior e injeta as mecânicas associando-as aos respetivos jogos através da propriedade `:usadaEm`, gerando o ficheiro `boardgames_mecanicas.ttl`.
  5. `povoar_premios.py`: Lê `premios.json`, consome o acumulado e injeta os prémios com as propriedades `:ano` e `:ganhoPor`, gerando o **ficheiro final totalmente povoado: [boardgames_ind.ttl](boardgames_ind.ttl)**.

### 3. Ficheiro Final de Indivíduos (`boardgames_ind.ttl`)
O resultado de todo o pipeline de povoamento automático. Contém toda a ontologia original acrescida de centenas de triplos representativos de todos os jogos, autores, editoras, mecânicas e prémios interligados de forma consistente.

### 4. Queries SPARQL Analíticas (`sparql.txt`)
O ficheiro [sparql.txt](sparql.txt) contém todas as queries completas organizadas e comentadas por alínea.