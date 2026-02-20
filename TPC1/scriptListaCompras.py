import json

compras_json = [
    {
        "designacao": "Lista de compras 1",
        "data": "2021-01-18",
        "produtos": [
            {
                "designacao": "Postas de Salmão",
                "categoria": "Peixe",
                "quantidade": {"valor": "4", "unidade": "unidade"}
            },
            {
                "designacao": "Embalagem de SKIP",
                "categoria": "Limpeza",
                "quantidade": {"valor": "3", "unidade": "unidade"}
            }
        ]
    }
]

def gera_ontologia(data):
    # Cabeçalho do ficheiro Turtle (Prefixos)
    ttl = """@prefix : <http://rpcw.di.uminho.pt/2026/compras#> .
        @prefix owl: <http://www.w3.org/2002/07/owl#> .
        @prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .
        @prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

        ### Ontologia de Compras
        """
    
    for lista in data:
        # Criar ID para a Lista (ex: Lista_de_compras_1)
        lista_id = lista['designacao'].replace(" ", "_")
        
        # Gerar a instância da Lista
        ttl += f"\n:{lista_id} rdf:type :Lista ;\n"
        ttl += f"    :data \"{lista['data']}\" .\n"
        
        for produto in lista['produtos']:
            # Criar ID para o Produto (ex: Postas_de_Salmão)
            prod_id = produto['designacao'].replace(" ", "_")
            
            # Gerar a instância do Produto e a relação com a Lista
            ttl += f"\n:{prod_id} rdf:type :Produto ;\n"
            ttl += f"    :temCategoria \"{produto['categoria']}\" ;\n"
            ttl += f"    :quantidade {produto['quantidade']['valor']} ;\n"
            ttl += f"    :unidade \"{produto['quantidade']['unidade']}\" ;\n"
            ttl += f"    :pertenceALista :{lista_id} .\n"
            
    return ttl

# 2. Executar e guardar o ficheiro
resultado_ttl = gera_ontologia(compras_json)

with open("compras.ttl", "w", encoding="utf-8") as f:
    f.write(resultado_ttl)

print("Ficheiro 'compras.ttl' gerado com sucesso!")