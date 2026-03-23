# Ficha Medicina

## Resumo
O objetivo principal deste projeto foi povoar uma ontologia médica base (`medical.ttl`) a partir de datasets externos (em formato CSV e JSON) e, posteriormente, extrair conhecimento e inferir novos dados utilizando queries SPARQL (SELECT, CONSTRUCT e INSERT).

A resolução foi dividida em duas grandes fases: o povoamento programático utilizando Python e a biblioteca `rdflib`, e o interrogatório da ontologia com SPARQL para responder a questões estatísticas e realizar diagnósticos automáticos.

---

## Metodologia e Desenvolvimento

### 1. Povoamento da Ontologia (Python)
Para garantir uma construção segura e modular, o povoamento foi dividido em três scripts sequenciais:

* **`med_doencas.py`**: Lê os ficheiros `Disease_Syntoms.csv` (ignorando o cabeçalho) e `Disease_Description.csv`. Cria os indivíduos da classe `:Disease` e `:Symptom`, estabelece a relação `:hasSymptom` e a *data property* `:description`. O resultado é guardado em `med_doencas.ttl`.
* **`med_tratamentos.py`**: Carrega o ficheiro anterior, lê `Disease_Treatment.csv` e cria as instâncias de `:Treatment`, associando-as às doenças com a propriedade `:hasTreatment`. O resultado é guardado em `med_tratamentos.ttl`.
* **`med_doentes.py`**: Carrega o ficheiro de tratamentos, processa a lista de objetos do `doentes.json` para extrair os nomes e sintomas, criando os indivíduos da classe `:Patient` (com um ID único) e a relação `:exhibitsSymptom`. O resultado final consolidado é o `med_doentes.ttl`.

**Nota Técnica (Limpeza de URIs):** Foi implementada uma função de limpeza de texto nos scripts Python que remove parênteses.

### 2. Inferência e Interrogação (SPARQL)
As queries desenvolvidas encontram-se no ficheiro [sparql.txt](sparql.txt).

---

## Instruções de Execução

Para replicar os cenários deste projeto e obter a ontologia final:

1. **Requisitos:** Ter o Python instalado e instalar a biblioteca `rdflib` (`pip install rdflib`).
2. **Ordem de Execução dos Scripts:**
   * Executar `python med_doencas.py` (Gera `med_doencas.ttl`)
   * Executar `python med_tratamentos.py` (Gera `med_tratamentos.ttl`)
   * Executar `python med_doentes.py` (Gera `med_doentes.ttl`)
3. **Validação:** Importar o ficheiro `med_doentes.ttl` para o GraphDB (ou Protegé).
4. **SPARQL:** Correr as queries presentes no ficheiro `sparql.txt` sequencialmente. **Importante:** A query de `INSERT` do Passo 12 deve ser corrida obrigatoriamente antes das queries 13, 14 e 15 para que as distribuições reflitam os diagnósticos gerados.