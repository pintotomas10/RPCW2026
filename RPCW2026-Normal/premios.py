import json

def limpa_string(texto):
    if not texto:
        return ""
    return texto.replace('"', '\\"')

def limpa_id(identificador):
    if not identificador:
        return ""
    return identificador.replace('-', '_')

def duplicar_e_acrescentar_premios(json_path, ttl_anterior_path, ttl_output_path):
    with open(ttl_anterior_path, 'r', encoding='utf-8') as f_anterior:
        conteudo_acumulado = f_anterior.read()
        
    with open(json_path, 'r', encoding='utf-8') as f_json:
        premios = json.load(f_json)
        
    ttl_individuos = "\n#################################################################\n"
    ttl_individuos += "#    Indivíduos - Prémios\n"
    ttl_individuos += "#################################################################\n\n"
    
    for p in premios:
        premio_id = limpa_id(p['id'])
        nome = limpa_string(p['name'])
        ano = p['year']
        
        ttl_individuos += f"###  http://www.di.uminho.pt/rpcw2026/A104448#{premio_id}\n"
        ttl_individuos += f":{premio_id} rdf:type owl:NamedIndividual , :Premio ;\n"
        ttl_individuos += f"    :nome \"{nome}\" ;\n"
        ttl_individuos += f"    :ano {ano}"
        
        if "wonByGame" in p and p["wonByGame"]:
            jogo_limpo = limpa_id(p["wonByGame"])
            ttl_individuos += f" ;\n    :ganhoPor :{jogo_limpo} .\n\n"
        else:
            ttl_individuos += " .\n\n"
        
    with open(ttl_output_path, 'w', encoding='utf-8') as f_out:
        f_out.write(conteudo_acumulado + ttl_individuos)

    print(f"Sucesso! Criado o ficheiro final '{ttl_output_path}' com a estrutura anterior + {len(premios)} prémios.")

if __name__ == "__main__":
    duplicar_e_acrescentar_premios("premios.json", "boardgames_mecanicas.ttl", "boardgames_ind.ttl")