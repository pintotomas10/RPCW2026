# Manifesto: TPC2 - Ontologia de Cinema (Cinema Ontology)

**Data:** 2026-02-04

## Resumo
Este trabalho consistiu na criação de uma ontologia sobre produções cinematográficas, com o objetivo de modelar e estruturar o conhecimento associado a filmes, realizadores, atores e géneros. A ontologia estabelece relações entre estas entidades, permitindo representar de forma organizada os diferentes elementos que compõem uma produção cinematográfica. Graças à integração de lógica descritiva, o modelo possibilita a realização de inferências automáticas, como por exemplo classificar uma Pessoa como Ator caso esta atue num filme, sem que essa classificação tenha de ser explicitamente declarada.

## Estrutura da Ontologia


### 1. Estrutura de Classes

* **Filme**: Classe central que representa as obras cinematográficas. Inclui subclasses definidas por condições lógicas, tais como:
  * `longasMetragens` – filmes com duração superior a 60 minutos;
  * `FilmesInteressantes` – obras associadas a dois ou mais géneros;
  * Subclasses por género, como `FilmeAventura`, `FilmeComedia`, `FilmeMusical`, `FilmeDramático`,`FilmeRomântico` e `FilmeInfantil`.

* **Pessoa**: Classe genérica para indivíduos envolvidos nas produções, com subclasses inferidas automaticamente:
  * `Ator` – pessoa que possui a propriedade `atuou` associada a um Filme;
  * `Realizador` – pessoa que realizou uma obra;
  * `Escritor` e `Músico` – responsáveis por argumentos, obras literárias adaptadas ou bandas sonoras.

* **Género**: Classe definida através de enumeração, incluindo categorias como G_Ação, G_Aventura, G_Comédia, G_Drama, G_Ficção, G_Infantil, G_Romance, G_Terror e G_Thriller.

* **Personagem**: Entidade que representa os papéis interpretados pelos atores nos filmes.

### 2. Propriedades Definidas

* **Propriedades de Objeto:**
  * `atuou` / `temAtor` – estabelecem a relação entre atores e filmes;
  * `realizou` / `foiRealizado` – indicam a direção da obra;
  * `representa` – associa um ator à personagem que interpreta;
  * `temGénero` – liga um filme à sua categoria temática.

* **Propriedades de Dados:**
  * `titulo` – designação textual do filme;
  * `duracao` – duração da obra em minutos (valor inteiro);
  * `data` – data de lançamento;
  * `temSexo` – identificador biográfico (“M” ou “F”).


## Casos de Estudo (Exemplos Reais)

Para validar o modelo ontológico, foram integrados dados concretos relativos a três produções cinematográficas conhecidas, permitindo testar as relações entre filmes, realizadores, géneros e personagens.

| Obra                 | Direção                   | Categorias                 | Personagens Principais        |
| :------------------- | :------------------------ | :------------------------- | :---------------------------- |
| **Madagascar 2**     | Tom McGrath, Eric Darnell | Aventura, Infantil         | Alex, Marty, Melman, Gloria   |
| **Teen Beach Movie** | Jeffrey Hornaday          | Comédia, Infantil, Musical | Brady, McKenzie, Lela, Tanner |
| **Twilight**         | Catherine Hardwicke       | Drama, Romance, Thriller   | Bella Swan, Edward Cullen     |


## Instruções de Utilização

1. Instalar a ferramenta Protégé.
2. Abrir o ficheiro cinema.ttl na aplicação.
3. Executar um reasoner (por exemplo, HermiT ou Pellet) para permitir a geração de classes e relações inferidas automaticamente.
4. Aceder ao separador DL Query para realizar consultas à ontologia, como por exemplo: `Pessoa and Atuou some FilmeInfantil`


## Autor

> **Nome:** Tomás Pinto Rodrigues

> **ID:** A104448

> **Foto:**

>![Foto Perfil](https://github.com/user-attachments/assets/93c3244b-7485-481b-8ae0-d92d039f5cf2)