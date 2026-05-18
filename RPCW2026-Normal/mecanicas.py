import json

def limpa_string(texto):
    if not texto:
        return ""
    return texto.replace('"', '\\"')

def limpa_id(identificador):
    if not identificador:
        return ""
    return identificador.replace('-', '_')

def duplicar_e_acrescentar_mecanicas(json_path, ttl_anterior_path, ttl_output_path):
    with open(ttl_anterior_path, 'r', encoding='utf-8') as f_anterior:
        conteudo_acumulado = f_anterior.read()
        
    with open(json_path, 'r', encoding='utf-8') as f_json:
        mecanicas = json.load(f_json)
        
    ttl_individuos = "\n#################################################################\n"
    ttl_individuos += "#    Indivíduos - Mecânicas\n"
    ttl_individuos += "#################################################################\n\n"
    
    for m in mecanicas:
        mecanica_id = limpa_id(m['id'])
        nome = limpa_string(m['name'])
        
        ttl_individuos += f"###  http://www.di.uminho.pt/rpcw2026/A104448#{mecanica_id}\n"
        ttl_individuos += f":{mecanica_id} rdf:type owl:NamedIndividual , :Mecanica ;\n"
        
        if "usedInGames" not in m or not m["usedInGames"]:
            ttl_individuos += f"    :nome \"{nome}\" .\n\n"
        else:
            ttl_individuos += f"    :nome \"{nome}\" ;\n"
            
            jogos = m["usedInGames"]
            for i, j_id in enumerate(jogos):
                jogo_limpo = limpa_id(j_id)
                if i == len(jogos) - 1:
                    ttl_individuos += f"    :usadaEm :{jogo_limpo} .\n\n"
                else:
                    ttl_individuos += f"    :usadaEm :{jogo_limpo} ;\n"
        
    with open(ttl_output_path, 'w', encoding='utf-8') as f_out:
        f_out.write(conteudo_acumulado + ttl_individuos)

    print(f"Sucesso! Criado o ficheiro '{ttl_output_path}' com a estrutura anterior + {len(mecanicas)} mecânicas.")

if __name__ == "__main__":
    duplicar_e_acrescentar_mecanicas("mecanicas.json", "boardgames_editoras.ttl", "boardgames_mecanicas.ttl")