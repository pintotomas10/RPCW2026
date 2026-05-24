# Relatório de Projeto: Ontologia do Festival da Canção

Este relatório descreve a metodologia utilizada para a especificação, povoamento e disponibilização da ontologia sobre o **Festival da Canção**, servindo como documentação de suporte ao sistema Web desenvolvido em Flask.

---

## Metodologia para Especificação de Ontologias

### 1. Especificar o Domínio

#### a. Para que é que vamos usá-la?
A ontologia foi desenhada para centralizar, estruturar e interligar todo o conhecimento histórico relativo ao **Festival RTP da Canção** (desde a sua primeira edição em 1964 até à atualidade). O objetivo principal é servir como a base de dados semântica (armazenada no GraphDB) que alimenta uma aplicação Web, permitindo aos utilizadores navegar de forma inteligente pelas edições, fases (semifinais e finais), músicas, intérpretes, compositores e letristas, além de registar e consultar o resultado obtido da musica vencedora no festival da Eurovisão.

#### b. A que perguntas deve dar resposta?
A ontologia e o endpoint SPARQL configurado respondem com precisão a perguntas de competência complexas, tais como:
* Quais foram todas as músicas concorrentes numa determinada edição do festival?
* Quem foi o artista vencedor de um determinado ano e qual foi a sua classificação na Eurovisão (`:eurovisionResult`)?
* Que fases (Semifinais ou Finais) existiram num determinado ano, quando ocorreram (`:phaseDate`), onde (`:venueName`) e quem foram os seus apresentadores?
* Quais as músicas escritas por um compositor ou letrista específico ao longo da história do festival?
* Quem são os top 5 compositores com maior volume de participações?

#### c. Quem vai usá-la e mantê-la?
* **Utilizadores:** Entusiastas do festival, historiadores de música, jornalistas e o público geral que utilize a plataforma Web para explorar a árvore cronológica do certame.
* **Administradores:** Administradores do sistema através do painel de gestão da aplicação Flask (rotas de inserção de novas fases, músicas e consagração de vencedores), que traduz formulários Web comuns em operações semânticas `INSERT DATA` e `DELETE/INSERT` via SPARQL sem necessidade de manipular os ficheiros Turtle (`.ttl`) manualmente.

---

### 2. Considerar a Utilização de Ontologias Já Existentes
Para este domínio específico e de âmbito académico, optou-se pela especificação de uma ontologia nativa e customizada de raiz, de forma a mapear de modo direto e sem sobrecarga conceptual a estrutura de dados extraída da Wikipédia. No entanto, o desenho conceptual inspirou-se e respeitou os bons princípios de vocabulários globais e maduros, nomeadamente:
* **FOAF (Friend of a Friend) e Schema.org:** No mapeamento de indivíduos humanos (classe `:Person`, `:Artist`), utilizando propriedades que mimetizam dados biográficos essenciais.
* **Dublin Core (`dc:`):** Na atribuição de metadados textuais e títulos das faixas musicais.

---

### 3. Enumerar os Termos mais Importantes do Domínio
Os conceitos nucleares identificados que compõem o ecossistema do festival são:
* *Festival da Canção, Edição, Ano, Concorrente/Participante, Música, Canção, Faixa, Intérprete, Artista, Compositor, Liricistas, Fase do Festival, Semifinal, Final, Local, Cidade, Apresentador, Resultado da Eurovisão.*

---

### 4. Definir as Classes e a sua Hierarquia
A taxonomia foi modelada em OWL utilizando uma estrutura clara de classes e subclasses, de forma a segmentar as entidades por papéis e tipologias:

* **`:FestivalEdition`** – Representa o evento macro de um ano específico.
* **`:Contestant`** – Instância intermédia que liga um artista e a sua canção a uma edição específica (a participação em si).
* **`:Song`** – Representa a obra musical concorrente.
* **`:Person`** – Superclasse de todos os seres humanos envolvidos no festival.
  * **`:Artist`** – Subclasse de Person; o intérprete que executa a canção.
  * **`:Composer`** – Subclasse de Person; o criador da melodia.
  * **`:Lyricist`** – Subclasse de Person; o autor do poema/letra.
  * **`:Presenter`** – Subclasse de Person; o anfitrião do espetáculo.
  * **`:MusicDirector`** – Subclasse de Person; o maestro ou diretor musical.
* **`:FestivalPhase`** – Representa os eventos constituintes de uma edição.
  * **`:SemiFinal`** – Subclasse de fase; eliminatória por votação.
  * **`:Final`** – Subclasse de fase; a gala de decisão do vencedor.
* **`:Venue`** – O espaço físico ou estúdio televisivo onde a fase ocorreu.
* **`:City`** – A cidade geográfica onde o recinto se localiza.

---

### 5. Definir os Atributos de cada Classe (Datatype Properties)
As propriedades de dados definem as características literais primitivas das nossas instâncias:

* **`rdfs:domain :FestivalEdition`**
  * `:editionYear` (tipo: `xsd:int`) – O ano numérico de realização.
* **`rdfs:domain :Song`**
  * `:songTitle` (tipo: `xsd:string`) – O nome da canção.
  * `:eurovisionResult` (tipo: `xsd:string`) – O resultado classificativo na Eurovisão.
* **`rdfs:domain :Person`**
  * `:personName` (tipo: `xsd:string`) – O nome completo da pessoa.
* **`rdfs:domain :Contestant`**
  * `:contestantId` (tipo: `xsd:string`) – O identificador único do participante.
  * `:artistName` (tipo: `xsd:string`) – Cópia textual do nome do artista para agilização semântica.
* **`rdfs:domain :FestivalPhase `**
  * `:phaseDate` (tipo: `xsd:string`) – A data em que o espetáculo foi para o ar.
  * `:phaseType` (tipo: `xsd:string`) – A categoria da fase ("Final" ou "SemiFinal").
* **`rdfs:domain :Venue`**
  * `:venueName` (tipo: `xsd:string`) – O nome do pavilhão ou estúdio (ex: "MEO Arena").
* **`rdfs:domain :City`**
  * `:cityName` (tipo: `xsd:string`) – O nome da cidade (ex: "Lisboa").

---

### 6. Definir Restrições sobre os Atributos: Vocabulários Controlados
* **Tipos de Dados Fortes:** Restrição de valores usando tipos nativos do XML Schema (XSD), como garantir que `:editionYear` é estritamente interpretado como `xsd:int` e não como texto de modo a permitir filtros numéricos (`xsd:integer(?y) = Ano`).
* **Categorização Controlada:** Restrição ao nível da aplicação sobre o campo `:phaseType` do formulário de criação de fases, forçando o input a assumir apenas os valores validados pela ontologia (`"SemiFinal"` ou `"Final"`).

---

### 7. Definir as Relações entre Indivíduos (Object Properties)
As ligações orientadas entre os objetos (indivíduos) da ontologia mapeiam o fluxo de conhecimento da seguinte forma:

* **`:hasContestant`** (Inversa: `:belongsToEdition`)
  * Origem: `:FestivalEdition` $\rightarrow$ Destino: `:Contestant`
* **`:performsSong`** (Inversa: `:performedBy`)
  * Origem: `:Contestant` $\rightarrow$ Destino: `:Song`
* **`:hasComposer`**
  * Origem: `:Song` $\rightarrow$ Destino: `:Composer`
* **`:hasLyricist`**
  * Origem: `:Song` $\rightarrow$ Destino: `:Lyricist`
* **`:hasMusicDirector`**
  * Origem: `:FestivalEdition` $\rightarrow$ Destino: `MusicDirector`
* **`:hasPhase`**
  * Origem: `:FestivalEdition` $\rightarrow$ Destino: `:FestivalPhase`
* **`:heldAt`**
  * Origem: `:FestivalPhase` $\rightarrow$ Destino: `:Venue`
* **`:locatedIn`**
  * Origem: `:Venue` $\rightarrow$ Destino: `:City`
* **`:hasPresenter`**
  * Origem: `:FestivalPhase` $\rightarrow$ Destino: `:Presenter`
* **`:hasWinner`**
  * Origem: `:FestivalEdition` $\rightarrow$ Destino: `:Contestant` (Indica o participante que ganhou a respetiva edição).

---

### 8. Definir quem são ou serão os Indivíduos
Os indivíduos são gerados dinamicamente seguindo uma nomenclatura padronizada e limpa  para garantir URIs legíveis e evitar duplicações de recursos comuns:

* **Edições:** Criados sob o padrão numérico direto, ex: `:Edition_1964`, `:Edition_2024`, `:Edition_2027`.
* **Músicas:** Nomeadas com base no ano e no slug do título, ex: `:Song_2017_amar_pelos_dois`.
* **Participantes (Contestants):** Agrupados pelo ano e slug do intérprete, ex: `:Contestant_2017_salvador_sobral`.
* **Pessoas (Artistas, Compositores, Letristas, Apresentadores):** Indexados de forma única pelo seu nome próprio de modo a permitir a reutilização histórica do mesmo indivíduo em múltiplos anos, ex: `:Person_luisa_sobral`, `:Person_salvador_sobral`, `:Person_vasco_palmeirim`.
* **Locais e Cidades:** Mapeados de forma unívoca, ex: `:City_lisboa`, `:Venue_estudios_do_lumiar`.

---

## Processo de Desenvolvimento e Implementação

O projeto foi dividido em fases lógicas, assegurando que a qualidade dos dados e a validação da ontologia serviam de fundação estável antes da construção da interface web.

### 1ª Fase: Engenharia de Dados, Extração e Povoamento Semântico

Após a especificação e desenho conceptual da ontologia base no Protégé, a primeira fase focou-se na aquisição automatizada de conhecimento, tratamento de dados estruturados e validação semântica. Esta fase dividiu-se em três etapas fundamentais:

#### 1. Extração Dinâmica e Limpeza de Dados (`extrair.py`)
Devido à ausência de uma API oficial com o histórico do Festival RTP da Canção, foi desenvolvido um script de *web scraping* em Python [extrair.py](extrair.py) utilizando a biblioteca **BeautifulSoup** e o módulo **Requests** para minerar os dados diretamente das páginas da Wikipédia.
* **Desafio e Solução:** Ao longo das suas mais de seis décadas, o formato e a estrutura das páginas da Wikipédia variam drasticamente (por exemplo, edições antigas contavam apenas com uma Grande Final direta, enquanto edições recentes contêm múltiplas semifinais e tabelas com designs distintos). Para contornar isto, foram programadas funções de parsing condicional capazes de identificar o layout específico de cada era do festival.
* **Limpeza de Dados:** O script implementou expressões regulares (Regex) para remover notas de rodapé de texto (ex: `[1]`, `[nota 2]`), normalizar datas escritas, e mapear as classificações da Eurovisão (como lidar de forma limpa com strings como "não participou" ou "finalista"). O resultado final deste pipeline foi a exportação de um ficheiro perfeitamente estruturado em formato JSON: [festival_cancao.json](festival_cancao.json).

#### 2. Povoamento Automatizado da Ontologia (`povoar_ttl.py`)
Com o conhecimento estruturado em JSON, foi desenvolvido um script de povoamento semântico (`povoar_ttl.py`) baseado na biblioteca **RDFLib**. 
* **Conversão de Dados em Triplos:** O script lê o ficheiro JSON e traduz cada entrada num conjunto de triplos RDF (`Sujeito - Predicado - Objeto`).
* **Algoritmos de Normalização (Slugify):** De forma a garantir a integridade referencial e evitar a duplicação de entidades comuns (como por exemplo, o mesmo compositor ou letrista ter o seu nome escrito de formas ligeiramente diferentes ao longo dos anos), o script aplica uma função de *slugify* e remoção de diacríticos (acentos). Isto permitiu que indivíduos como `:Person_luisa_sobral` ou `:City_lisboa` fossem criados uma única vez e interligados corretamente a múltiplas músicas e edições ao longo do grafo. O output gerado foi o ficheiro de produção [festival_povoado.ttl](festival_povoado.ttl).

#### 3. Testes de Consistência e Queries de Validação (`queries.md`)
Antes de avançar para o desenvolvimento da aplicação Web, foi necessário garantir que o grafo gerado no GraphDB respeitava as regras da ontologia e que os dados estavam acessíveis de forma performativa. Para isso, foi criado o documento [queries.md](queries.md), contendo um caderno de testes com **queries SPARQL avançadas** executadas diretamente no painel do GraphDB.

### 2ª Fase: Desenvolvimento da Aplicação Web e Integração Semântica

Com o repositório RDF devidamente povoado no GraphDB, a segunda fase consistiu no desenvolvimento de uma aplicação Web completa que funciona como interface de visualização e sistema de gestão de conteúdos semânticos.

#### 1. Arquitetura de Conexão e Comunicação (`mquery.py`)
Para estabelecer a ponte entre o servidor Web e o Triplestore, utilizou-se o módulo utilitário fornecido em contexto letivo (`mquery.py`). Este script atua como um *wrapper* baseado na biblioteca **SPARQLWrapper**, parametrizado para apontar para o endpoint local do GraphDB (`http://localhost:7200/repositories/festival`). O módulo disponibiliza duas funções fundamentais que isolam a lógica de rede do código da aplicação:
* `exec_query(query)`: Encarregue de despachar queries `SELECT`, configurando o formato de retorno em **JSON** para ser facilmente iterável pelas rotas em Python.
* `exec_update(query)`: Responsável pelas queries de mutação de dados que apontam para o endpoint de `/statements` através do método **POST**.

#### 2. Lógica de Rotas e Orquestração Semântica (`app.py`)
O servidor, desenvolvido em **Flask**, implementa rotas dinâmicas que traduzem pedidos HTTP em queries SPARQL complexas. Destacam-se as seguintes componentes do ecossistema mapeado:

* **Painel de Controlo / Dashboard (`/`)**: Mapeia a rota principal recolhendo estatísticas globais em tempo real (como a contagem total de edições e de músicas registadas no grafo) através de funções de agregação (`COUNT`) e submete queries com limites de amostragem (`LIMIT 5`) para gerar o Top de Compositores dinâmico.
* **Catálogo Cronológico (`/edicao` e `/edicao/<ano>`)**: A rota de listagem faz a leitura global de todas as edições, avaliando condicionalmente (via cláusulas `UNION` e `FILTER`) se cada ano possui ou não semifinais associadas de forma a renderizar as *tags* visuais correspondentes. A rota de detalhes do ano efetua o varrimento completo dos triplos de uma edição, agrupando os participantes (`:Contestant`), as canções (`:Song`) e os eventos/fases associados.
* **Persistência Dinâmica e Mutação Atómica**: Para além da leitura, o ficheiro `app.py` foi desenhado para suportar o ciclo de vida completo dos dados (*CRUD*). Foram desenhadas rotas para a criação de raiz de novas edições (`/nova-edicao`), e rotas de edição/remoção que recorrem a transações SPARQL robustas com blocos combinados de `DELETE { ... } INSERT { ... } WHERE { ... }`, garantindo que os dados antigos (como um vencedor ou um resultado da Eurovisão) são integralmente limpos antes de se injetarem novos triplos, evitando estados de corrupção ou triplos órfãos no grafo.

#### 3. Motor de Templates e Interface de Utilizador (Estrutura de Páginas)
A interface foi construída recorrendo ao motor de templates **Jinja2** integrado no Flask, permitindo injetar dinamicamente as respostas estruturadas em JSON do GraphDB nas páginas Web. O ecossistema visual assenta nos seguintes ficheiros:

* **`layout.html` (Template de Base)**: Garante a consistência visual de toda a aplicação ao definir a barra de navegação global e ao centralizar o carregamento da framework W3.CSS e dos ícones Font Awesome. Serve de esqueleto para que as restantes páginas injetem o seu conteúdo específico de forma modular.
* **`index.html` (Página Principal / Dashboard)**: Apresenta o painel inicial da aplicação com blocos KPI agregados em tempo real. Destaca uma edição em foco detalhando dados de contexto (local, cidade e direção musical) sem redundâncias, posiciona o último vencedor registado e organiza de forma paralela os painéis com o Top 5 de artistas e compositores, finalizando com uma linha temporal interativa por década.
* **`lista_edicoes.html` (Catálogo de Edições)**: Lista cronologicamente todas as edições do festival presentes no repositório, adaptando visualmente os cartões com cores diferentes para assinalar a presença ou ausência de semifinais nessa edição.
* **`edicao.html` (Detalhes da Edição)**: Concentra toda a informação histórica de um ano específico, agregando os dados estruturados do local, apresentadores, fases (semifinais e final) e a listagem integral de músicas concorrentes.
* **`cancoes.html` (Arquivo Global de Músicas)**: Funciona como uma tabela centralizada com todas as canções guardadas na ontologia, incluindo um script em JavaScript nativo para filtragem instantânea por ano ou por pesquisa de texto livre sem necessidade de recarregar a página.
* **`nova_edicao.html` (Criação de Edição)**: Disponibiliza um formulário simples para inicializar e persistir uma nova edição anual base no GraphDB, validando os limites temporais aceitáveis para o registo.
* **`editar_musica.html` (Gestão de Canções)**: Permite modificar os metadados de uma canção existente (título, intérprete, compositores e liricistas) numa interface perfeitamente alinhada e adaptável (Flexbox), ou efetuar a sua remoção do triplestore através de um pedido HTTP assíncrono via API `fetch`.
* **`editar_fase.html` (Gestão de Fases)**: Viabiliza a atualização de dados operacionais relativos a uma determinada semifinal ou final (como a alteração do recinto ou da equipa de apresentadores), disponibilizando também a opção de eliminação da fase.
* **`nova_musica.html` (Registo de Canções)**: Apresenta um formulário completo para introduzir uma nova canção na edição do festival corrente, aceitando múltiplos compositores e letristas separados por vírgula para mapeamento individualizado de entidades no repositório.
* **`nova_fase.html` (Criação de Eventos)**: Permite o registo estruturado de uma nova semifinal ou final associada a um ano específico, dividindo explicitamente as informações em dados cronológicos, dados geográficos (local e cidade) e membros da equipa de apresentação.
* **`novo_vencedor.html` (Consagração de Campeão)**: Disponibiliza um dropdown alimentado em tempo real com os concorrentes desse ano específico para definir o vencedor da edição, guardando ainda a respetiva classificação internacional obtida no concurso da Eurovisão.
* **`novo_diretor_musical.html` (Definição de Maestro)**: Permite associar, atualizar ou substituir dinamicamente o Diretor Musical de uma determinada edição, suportando a seleção de uma entidade existente no grafo ou a criação automatizada de uma nova instância base.
* **`pessoas.html` (Índice de Intervenientes)**: Lista de forma categorizada todos os indivíduos registados no repositório, dividindo-os em colunas autónomas (Artistas, Liricistas, Compositores e Apresentadores) com um motor de busca reativo por texto em JavaScript.
* **`pessoa.html` (Perfil e Portefólio)**: Concentra o histórico biográfico e o portefólio musical de um determinado indivíduo, discriminando através de cartões estilizados de forma visual e quantificada todas as edições e canções em que participou em cada um dos seus papéis.
* **`vencedores.html` (Galeria de Campeões)**: Reúne num painel de cartões dourados todas as canções e intérpretes consagrados como vencedores ao longo das edições do festival, destacando de forma clara a classificação final obtida por cada um no concurso da Eurovisão.


---

## Conclusão e Considerações Finais

O desenvolvimento deste projeto permitiu aplicar com sucesso os conceitos práticos da UC ao domínio histórico do Festival RTP da Canção. A transição de um ecossistema de dados não estruturados (páginas web da Wikipédia) para um modelo de conhecimento interligado e formalizado em OWL provou trazer vantagens claras:

1. **Interoperabilidade e Reutilização**: Ao contrário dos modelos relacionais rígidos, a flexibilidade do grafo RDF permitiu lidar de forma nativa com as constantes mudanças de formato que o festival sofreu ao longo de seis décadas (edições com ou sem semifinais, variação de recintos e múltiplos papéis acumulados por um único indivíduo).
2. **Integridade e Identidade Única**: A implementação de algoritmos de normalização (*slugify*) na criação de URIs garantiu que artistas, compositores e letristas mantivessem uma identidade unívoca no repositório. Isto viabilizou a extração imediata do portefólio biográfico completo de qualquer interveniente através de cruzamentos lógicos simples em SPARQL.
3. **Desempenho da Aplicação**: A arquitetura assente no Flask e no utilitário `mquery.py` demonstrou que um Triplestore (GraphDB) consegue responder de forma performativa como backend de produção de um sistema web, suportando operações dinâmicas complexas de leitura e atualizações atómicas combinadas (`DELETE/INSERT`).

Em suma, o sistema cumpre integralmente todos os requisitos estipulados, disponibilizando uma plataforma robusta, escalável e de navegação intuitiva que preserva e valoriza o património cultural da música portuguesa de forma estruturada.