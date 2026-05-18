import json

def limpa_string(texto):
    if not texto:
        return ""
    return texto.replace('"', '\\"')

def limpa_id(identificador):
    if not identificador:
        return ""
    return identificador.replace('-', '_')

def duplicar_e_acrescentar_editoras(json_path, ttl_anterior_path, ttl_output_path):
    with open(ttl_anterior_path, 'r', encoding='utf-8') as f_anterior:
        conteudo_acumulado = f_anterior.read()
        
    with open(json_path, 'r', encoding='utf-8') as f_json:
        editoras = json.load(f_json)
        
    ttl_individuos = "\n#################################################################\n"
    ttl_individuos += "#    Indivíduos - Editoras\n"
    ttl_individuos += "#################################################################\n\n"
    
    for e in editoras:
        editora_id = limpa_id(e['id'])
        nome = limpa_string(e['name'])
        pais = limpa_string(e['country'])
        
        ttl_individuos += f"###  http://www.di.uminho.pt/rpcw2026/A104448#{editora_id}\n"
        ttl_individuos += f":{editora_id} rdf:type owl:NamedIndividual , :Editora ;\n"
        ttl_individuos += f"    :nome \"{nome}\" ;\n"
        ttl_individuos += f"    :pais \"{pais}\""
        
        if "publishedGames" in e and e["publishedGames"]:
            jogos_links = []
            for j_id in e["publishedGames"]:
                jogos_links.append(f":{limpa_id(j_id)}")
            
            ttl_individuos += " ;\n    :publicou " + " , ".join(jogos_links)
            
        ttl_individuos += " .\n\n"
        
    with open(ttl_output_path, 'w', encoding='utf-8') as f_out:
        f_out.write(conteudo_acumulado + ttl_individuos)

    print(f"Sucesso! Criado o ficheiro '{ttl_output_path}' com a estrutura anterior + {len(editoras)} editoras.")

if __name__ == "__main__":
    duplicar_e_acrescentar_editoras("editoras.json", "boardgames_autores.ttl", "boardgames_editoras.ttl")