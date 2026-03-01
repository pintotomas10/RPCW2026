# Manifesto: TPC3 - Ontologia Do Polvo Filosófico 

**Data:** 2026-03-01

## Resumo
Neste trabalho foi criado um repositório para alojar a ontologia O_Polvo_Filosófico. A ontologia foi analisada e corrigida no Protégé, resolvendo inconsistências identificadas. Posteriormente, foram executadas queries SPARQL para responder às questões propostas, nomeadamente a identificação de clientes, pratos servidos, ingredientes necessários e a verificação de indivíduos que acumulam os papéis de cliente e funcionário.

## Tarefas

### Preparação
1. Criar repositório para o O_Polvo_Filosófico <br>
Repositório criado no GraphDB 

2. Carregar a Ontologia, resolvendo problemas se existirem... (mostrar o que foi alterado) <br>
    A ontologia foi carregada no Protégé, onde foram identificadas e corrigidas as seguintes inconsistências:
    - Remoção dos pratos associados ao Polvo Aristóteles que continham polvo como ingrediente, uma vez que o indivíduo não pode consumir pratos com esse ingrediente.
    - Correção da classificação de Schrödinger, que se encontrava simultaneamente como Cliente e Funcionário, passando a estar apenas classificado como Funcionário.

    O resultado final foi guardado no ficheiro: [polvo_filosofico_corrigido.ttl](polvo_filosofico_corrigido.ttl)

### Queries
1. Quem foram os clientes?
```SPARQL
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://example.org/polvo-filosofico#>
select ?nomeCliente where {
    ?nomeCliente rdf:type :Cliente .
} 
```

2. Que pratos serve o restaurante?
```SPARQL
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://example.org/polvo-filosofico#>
select ?prato where {
    ?prato rdf:type :Prato .
} 
```

3. Quais os Ingredientes necessários à confeção dos pratos?
```SPARQL
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://example.org/polvo-filosofico#>
SELECT ?prato ?Nomeingredientes WHERE {
    ?prato rdf:type :Prato .
    ?prato :temIngrediente ?Nomeingredientes .
}
```

4. Há funcionários que sejam também clientes? 
```SPARQL
PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
PREFIX : <http://example.org/polvo-filosofico#>
SELECT ?pessoa WHERE {
    ?pessoa rdf:type :Cliente .
    ?pessoa rdf:type :Funcionario .
}
```

## Autor

> **Nome:** Tomás Pinto Rodrigues

> **ID:** A104448

> **Foto:**

>![Foto Perfil](https://github.com/user-attachments/assets/93c3244b-7485-481b-8ae0-d92d039f5cf2)