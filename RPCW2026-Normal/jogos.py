import json

def limpa_string(texto):
    if not texto:
        return ""
    return texto.replace('"', '\\"')

def limpa_id(identificador):
    if not identificador:
        return ""
    return identificador.replace('-', '_')

def duplicar_e_acrescentar_jogos(json_path, ttl_base_path, ttl_output_path):
    with open(ttl_base_path, 'r', encoding='utf-8') as f_base:
        conteudo_base = f_base.read()
        
    with open(json_path, 'r', encoding='utf-8') as f_json:
        jogos = json.load(f_json)
        
    ttl_individuos = "\n#################################################################\n"
    ttl_individuos += "#    Indivíduos - Jogos\n"
    ttl_individuos += "#################################################################\n\n"
    
    for j in jogos:
        jogo_id = limpa_id(j['id'])
        nome = limpa_string(j['name'])
        categoria = limpa_string(j['category'])
        min_p = j['minPlayers']
        max_p = j['maxPlayers']
        tempo = j['playingTimeMinutes']
        descricao = j['descriptionEN'].replace('"', '\\"')
        
        ttl_individuos += f"###  http://www.di.uminho.pt/rpcw2026/A104448#{jogo_id}\n"
        ttl_individuos += f":{jogo_id} rdf:type owl:NamedIndividual , :Jogo ;\n"
        ttl_individuos += f"    :nome \"{nome}\" ;\n"
        ttl_individuos += f"    :categoria \"{categoria}\" ;\n"
        ttl_individuos += f"    :minJogadores {min_p} ;\n"
        ttl_individuos += f"    :maxJogadores {max_p} ;\n"
        ttl_individuos += f"    :tempoJogoMin {tempo} ;\n"
        ttl_individuos += f"    :descricao \"{descricao}\" .\n\n"
        
    with open(ttl_output_path, 'w', encoding='utf-8') as f_out:
        f_out.write(conteudo_base + ttl_individuos)

    print(f"Sucesso! Criado o ficheiro '{ttl_output_path}' com IDs corrigidos (hífens para underscores).")

if __name__ == "__main__":
    duplicar_e_acrescentar_jogos("jogos.json", "boardgames_base.ttl", "boardgames_jogos.ttl")