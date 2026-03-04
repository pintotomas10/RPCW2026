# Manifesto: TPC4 - Ontologia Da Biblioteca Temporal

**Data:** 2026-03-04

## Resumo
Neste trabalho foi desenvolvida uma ontologia completa sobre uma biblioteca temporal, começando pela análise e modelação da ontologia base no Protégé (com exportação para Turtle), seguindo-se a população da ontologia com dados provenientes de dois ficheiros JSON através de um script Python. Posteriormente, foram executadas 14 queries SPARQL (10 principais + 4 bónus) para responder a questões sobre livros por timeline, autores prolíficos, inconsistências semânticas e relações entre entidades. Os resultados foram processados e salvos num script Python que permite visualizar os resultados de forma formatada.

## Tarefas

### 1. Modelação da Ontologia no Protégé
A ontologia foi criada e editada no Protégé, definindo a estrutura conceptual da biblioteca temporal.
**Estrutura da Ontologia:**
- **Classes principais:** Livro, LivroHistórico, LivroFiccional, LivroParodoxal, Autor, Leitor, Bibliotecário, Evento, EventoHistórico, EventoFuturo, LinhaTemporal, LinhaOriginal, LinhaAlternativa, Biblioteca
- **Propriedades de Objeto:** éEscritoPor, existeEm, pertenteA, refere, trabalhaEm, OcorreEm, requisita
- **Propriedade de Dados:** nome (string)
- **Indivíduos base:** Cronos (Autor e Bibliotecário), Biblioteca_Entre_Ontem_e_Amanha, Linha_T0 (LinhaOriginal), Linha_T1 (LinhaAlternativa)

A ontologia foi exportada para formato Turtle e guardada em: [bibliotecaTemporal.ttl](bibliotecaTemporal.ttl)

### 2. Conversão de Dados JSON para Ontologia Populada
Criou-se um script Python ([json_para_ttl.py](json_para_ttl.py)) que converte dados de dois ficheiros JSON para instâncias RDF, populando a ontologia base com:
- **Entrada:** `dataset_temporal_100.json` e `dataset_temporal_v2_100.json`
- **Processamento:**
  - Mapeamento de tipos JSON para classes OWL (ex: "Bibliotecario" → "Bibliotecário")
  - Mapeamento de propriedades JSON para propriedades OWL (ex: "pertenceA" → "pertenteA")
  - Normalização de IDs para garantir compatibilidade com RDF
  - Agregação de 200 recursos (103 livros + autores, bibliotecários, leitores, eventos, linhas temporais, bibliotecas)
- **Saída:** [bibliotecaTemporal_povoada.ttl](bibliotecaTemporal_povoada.ttl)

**Comando de execução:**
```bash
python .\json_para_ttl.py
```

**Resultado:** Sucesso - Ontologia povoada com 200 recursos adicionados/atualizados

### 3. Queries SPARQL Executadas
Foram criadas e executadas 14 queries SPARQL (10 principais + 4 bónus) para responder a questões sobre a biblioteca temporal. As queries foram armazenadas em [Queries.md](Queries.md) e executadas contra a ontologia populada.

### 4. Script de Execução de Queries
Criou-se um script Python ([Queries.py](Queries.py)) que executa todas as 14 queries SPARQL sobre a ontologia populada, exibindo os resultados de forma clara e estruturada.

**Funcionalidades:**
- Carrega a ontologia `bibliotecaTemporal_povoada.ttl`
- Executa todas as queries SPARQL com prefixos definidos
- Extrai nomes locais das URIs para apresentação clara
- Suporta encoding UTF-8 para caracteres especiais portugueses
- Permite guardar os resultados num ficheiro de texto com encoding UTF-8

**Comandos de execução:**
Para visualizar resultados no terminal:
```bash
python .\Queries.py
```

Para guardar resultados num ficheiro:
```bash
python .\Queries.py queries.txt
```

**Ficheiros de saída:**
- [queries.txt](queries.txt) - Resultados formatados de todas as queries

### 5. Resumo de Dados
| Métrica | Valor |
|---------|-------|
| Livros na linha original | 70 |
| Livros em múltiplas linhas | 39 |
| Livros paradoxais | 39 |
| Livros históricos | 31 |
| Inconsistências semânticas | 0 |
| Total de autores | 20 |
| Autores de paradoxais | 19 |
| Bibliotecários | 12 |
| Livros sem eventos | 0 |
| Livros sem timeline | 0 |
| Pessoas Autor+Leitor | 0 |
| Total de recursos populados | 200 |

## Ficheiros Gerados
- `bibliotecaTemporal.ttl` - Ontologia base em Turtle
- `bibliotecaTemporal_povoada.ttl` - Ontologia populada com dados dos JSONs
- `json_para_ttl.py` - Script para converter JSONs e popular ontologia
- `Queries.md` - Documento com todas as 14 queries
- `Queries.py` - Script para executar queries SPARQL
- `queries.txt` - Resultados das queries

## Autor

> **Nome:** Tomás Pinto Rodrigues

> **ID:** A104448

> **Foto:**

>![Foto Perfil](https://github.com/user-attachments/assets/93c3244b-7485-481b-8ae0-d92d039f5cf2)
