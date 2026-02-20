# Manifesto: TPC1 - Ontologia da História e Dataset de Compras

**Data:** 2026-02-04

## Resumo
Este trabalho consistiu na criação de uma ontologia baseada numa história sobre a aprendizagem de línguas na Universidade do Minho. O objetivo foi modelar classes, propriedades e indivíduos no software **Protégé** e exportar o resultado no formato Turtle (TTL). Adicionalmente, foi explorada a geração automática de ontologias a partir de datasets JSON.

## 1. Modelação Ontológica

Foi criada uma ontologia para representar a história de Eduardo, estudante de 21 anos natural do Porto.

Foram definidas as classes `Pessoa`, `Lingua`, `Curso`, `Universidade` e `Cidade`, bem como propriedades de objeto (`falaLingua`, `naturalDe`, `inscritoEm`, `parceiroDe`, `leciona`) e propriedades de dados (`temIdade`, `diaAula`, `temNome`).

Foram ainda instanciados os indivíduos Eduardo, Carlos, Ana, Helmut Ratz e Hanna, juntamente com as respetivas entidades associadas.

## 2. Consultas com DL Query

Após a execução do *reasoner* no Protégé, foi possível responder a questões como:

* As línguas faladas por Eduardo (Português, Espanhol, Inglês e Alemão);
* Os estudantes inscritos no curso de Alemão (Eduardo, Carlos e Ana);
* A caracterização de Hanna como estudante alemã de Biotecnologia e parceira de aprendizagem de Eduardo.

## 3. Dataset de Compras

Foi analisado um ficheiro JSON com listas de compras e definida uma estrutura ontológica com as classes `Lista`, `Produto`, `Categoria` e `Quantidade`.

Foi também preparado um script em Python para gerar automaticamente indivíduos a partir do dataset.

## Autor

> **Nome:** Tomás Pinto Rodrigues

> **ID:** A104448

> **Foto:**

>![Foto Perfil](https://github.com/user-attachments/assets/93c3244b-7485-481b-8ae0-d92d039f5cf2)
