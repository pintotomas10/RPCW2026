import json

def limpa_string(texto):
    if not texto:
        return ""
    return texto.replace('"', '\\"')

def limpa_id(identificador):
    if not identificador:
        return ""
    return identificador.replace('-', '_')

def duplicar_e_acrescentar_autores(json_path, ttl_anterior_path, ttl_output_path):
    with open(ttl_anterior_path, 'r', encoding='utf-8') as f_anterior:
        conteudo_acumulado = f_anterior.read()
        
    with open(json_path, 'r', encoding='utf-8') as f_json:
        autores = json.load(f_json)
        
    ttl_individuos = "\n#################################################################\n"
    ttl_individuos += "#    Indivíduos - Autores\n"
    ttl_individuos += "#################################################################\n\n"
    
    for a in autores:
        autor_id = limpa_id(a['id'])
        nome = limpa_string(a['name'])
        
        ttl_individuos += f"###  http://www.di.uminho.pt/rpcw2026/A104448#{autor_id}\n"
        ttl_individuos += f":{autor_id} rdf:type owl:NamedIndividual , :Autor ;\n"
        ttl_individuos += f"    :nome \"{nome}\""
        
        if "designedGames" in a and a["designedGames"]:
            jogos_links = []
            for j_id in a["designedGames"]:
                jogos_links.append(f":{limpa_id(j_id)}")
            
            ttl_individuos += " ;\n    :desenhou " + " , ".join(jogos_links)
            
        ttl_individuos += " .\n\n"
        
    with open(ttl_output_path, 'w', encoding='utf-8') as f_out:
        f_out.write(conteudo_acumulado + ttl_individuos)

    print(f"Sucesso! Criado o ficheiro '{ttl_output_path}' com a estrutura anterior + {len(autores)} autores.")

if __name__ == "__main__":
    duplicar_e_acrescentar_autores("autores.json", "boardgames_jogos.ttl", "boardgames_autores.ttl")