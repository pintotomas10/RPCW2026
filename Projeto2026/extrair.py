import requests
from bs4 import BeautifulSoup
import json
import time
import re

BASE_URL = "https://pt.wikipedia.org/wiki/Festival_RTP_da_Can%C3%A7%C3%A3o_{}"
years = range(1964, 2027)
session = requests.Session()

headers = {
    "User-Agent": "Mozilla/5.0"
}

# ----------- Eurovision Place ---------- #

def get_eurovision_results_map():
    url_geral = "https://pt.wikipedia.org/wiki/Festival_RTP_da_Can%C3%A7%C3%A3o"
    try:
        res = requests.get(url_geral, headers=headers)
        soup_geral = BeautifulSoup(res.text, "html.parser")
        results_map = {}

        # Procura a tabela que contém a classificação na Eurovisão
        for table in soup_geral.find_all("table", class_="wikitable"):
            if "Classificação na Eurovisão" in table.get_text():
                for row in table.find_all("tr")[1:]: 
                    cols = row.find_all(["td", "th"])
                    if len(cols) >= 5:
                        ano_text = cols[1].get_text(strip=True)
                        classif = cols[-1].get_text(strip=True)
                        
                        ano_match = re.search(r"\d{4}", ano_text)
                        if ano_match:
                            ano = int(ano_match.group())
                            results_map[ano] = classif
        return results_map
    except:
        return {}

EURO_MAP = get_eurovision_results_map()

# ---------------- LIMPEZA ---------------- #

def clean(text):
    if not text:
        return None
    
    text = re.sub(r"\[\s*.*?\s*\]", "", text)
    text = re.sub(r"^\*\s*", "", text)
    text = re.sub(r"\s*\((cantor|duo|banda|grupo|cantora|canção|portuguesa|português).*?\)", "", text, flags=re.IGNORECASE)
    text = re.sub(r"\(tradução.*?\)", "", text, flags=re.IGNORECASE)
    text = text.replace("''", "").replace('"', '').replace('“', '').replace('”', '')
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"^\*\s*", "", text)
    text = text.strip().rstrip(',')
    return text.strip()

def clean_date(text):
    if not text:
        return None
    text = re.sub(r"\[\s*\d+\s*\]", "", text)
    text = re.sub(r"\[\d+\]", "", text)
    text = text.replace("\xa0", " ")
    return text.strip()

def clean_presenter_name(name):
    """Limpa conectores, parênteses e espaços residuais."""
    name = re.sub(r"^(e\s+|&\s+)", "", name, flags=re.IGNORECASE)
    name = re.sub(r"\((semi|meia|final|eliminatória|1º|2º)[^)]*\)", "", name, flags=re.IGNORECASE)
    name = re.sub(r"^[^:]*:\s*", "", name)
    
    cleaned = clean(name)
    
    if cleaned and cleaned.lower() in ["e", "&"]:
        return None
        
    return cleaned

EXCECOES_NOMES = [
    "Nóbrega e Sousa", 
    "Andrade e Silva", 
    "Carlos Nóbrega, Sousa",
    "Filipe de Andrade e Silva",
    "Andrade, Silva",
    "José Campos, Sousa",
    "Maria Emauz e Silva",
    "Maria da Conceição e Silva"
]

NORMALIZACAO_NOMES = {
    "Nóbrega e Sousa": "Carlos Nóbrega e Sousa",
    "Andrade e Silva": "Filipe de Andrade e Silva",
    "Campos, Sousa": "José Campos e Sousa"
}

def split_names(text):
    if not text:
        return []
    
    normalized = text.replace('&amp;', '&').strip()

    for nome in EXCECOES_NOMES:
        if nome.lower() in normalized.lower():
            pattern = re.compile(re.escape(nome), re.IGNORECASE)
            normalized = pattern.sub(
                nome.replace(" e ", "###").replace(", ", "###"),
                normalized
            )

    normalized = normalized.replace("\n", ", ")
    normalized = re.sub(r'\s+\be\b\s+', ', ', normalized)

    parts = [n.strip() for n in re.split(r',|&', normalized)]

    temp_list = []
    i = 0

    while i < len(parts):
        current = re.sub(r'\(.*?\)', '', parts[i]).strip()

        if current == "José Campos" and (i + 1) < len(parts):
            next_part = re.sub(r'\(.*?\)', '', parts[i+1]).strip()

            if next_part == "Sousa":
                temp_list.append("José Campos e Sousa")
                i += 2
                continue

        temp_list.append(parts[i])
        i += 1

    clean_list = []

    for n in temp_list:
        recuperado = n.replace("###", " e ")
        recuperado = re.sub(r'\(.*?\)', '', recuperado).strip()

        if recuperado:

            if recuperado in NORMALIZACAO_NOMES:
                clean_list.append(NORMALIZACAO_NOMES[recuperado])
            else:
                clean_list.append(recuperado)

    return list(dict.fromkeys(clean_list))

# ---------------- SAFE ROW EXTRACTION ---------------- #

def extract_row_value(soup, keywords):
    rows = soup.find_all("tr")

    for row in rows:
        cols = row.find_all(["th", "td"])
        if len(cols) < 2:
            continue

        key = cols[0].get_text(" ", strip=True).lower()
        value = cols[-1].get_text(" ", strip=True)

        for k in keywords:
            if key.strip() == k.lower():
                return clean_date(value)

    return None


# ---------------- VENCEDOR ---------------- #

def extract_winner(soup):
    winner_label = soup.find("td", string=re.compile(r"vencedor", re.IGNORECASE))

    if winner_label:
        cell = winner_label.find_next_sibling("td")
        if cell:
            items = cell.find_all("li")
            if len(items) >= 2:
                text_1 = items[0].get_text(" ", strip=True)
                text_2 = items[1].get_text(" ", strip=True)
                
                if items[0].find(['i', 'em', 'cite']) or '"' in text_1 or '“' in text_1:
                    song = clean(text_1).replace('"', '').replace('“', '').replace('”', '')
                    artist = clean(text_2)
                else:
                    artist = clean(text_1)
                    song = clean(text_2).replace('"', '').replace('“', '').replace('”', '')

                # Regra especial 1967
                if "vento mudou" in artist.lower():
                    return {"artist": song, "song": artist}
                return {"artist": artist, "song": song}

            full_text = cell.get_text(" ", strip=True)
            if "," in full_text:
                parts = [clean(p) for p in full_text.split(",")]
                if len(parts) >= 2:
                    if '"' in full_text or '“' in full_text:
                        return {
                            "artist": parts[1],
                            "song": parts[0].replace('"', '').replace('“', '').replace('”', '')
                        }
                    return {"artist": parts[0], "song": parts[1]}

    for table in soup.find_all("table", class_="wikitable"):
        caption = table.find("caption")
        cap_text = caption.get_text().lower() if caption else ""
        
        if any(x in cap_text for x in ["votação", "online", "on-line"]):
            continue

        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all(["td", "th"])
            if len(cols) < 3:
                continue
            
            last_cols_text = " ".join([c.get_text().lower() for c in cols[-2:]])
            
            if "1º" in last_cols_text or "1.º" in last_cols_text or "vencedor" in row.get_text().lower():
                return {
                    "artist": clean(cols[1].get_text(" ", strip=True)),
                    "song": clean(cols[2].get_text(" ", strip=True))
                }

    return None

# ---------------- INFORMAÇÃO DE CADA ANO ---------------- #

def extract_info(soup):
    infobox = soup.find("table", class_=re.compile(r"infobox|vcard"))
    target = infobox if infobox else soup

    final_date = None
    semi_finals_dates = []
    p_final = []
    p_semis_map = {}
    music_director = None
    location = {"venue": None, "city": None}

    def is_actual_date(text):
        if not text or "%" in text:
            return False

        meses = [
            "janeiro", "fevereiro", "março", "abril", "maio", "junho",
            "julho", "agosto", "setembro", "outubro", "novembro", "dezembro"
        ]

        return any(m in text.lower() for m in meses)

    def clean_presenter_name(name):
        name = re.sub(r"^(e\s+|&\s+)", "", name, flags=re.IGNORECASE)
        name = re.sub(
            r"\((semi|meia|final|eliminatória|1º|2º)[^)]*\)",
            "",
            name,
            flags=re.IGNORECASE
        )
        name = re.sub(r"^[^:]*:\s*", "", name)

        cleaned = clean(name)

        if cleaned and (cleaned.lower() in ["e", "&"] or len(cleaned) < 3):
            return None

        return cleaned

    for row in target.find_all("tr"):
        cols = row.find_all(["th", "td"])
        if len(cols) < 2:
            continue

        key = cols[0].get_text(" ", strip=True).lower()
        val_cell = cols[-1]
        val_text = val_cell.get_text(" ", strip=True)

        # ---------------- DATAS ---------------- #
        if key == "final" and is_actual_date(val_text):
            final_date = clean_date(val_text)

        elif any(k in key for k in ["semi", "qualificação", "eliminatória", "meia"]):
            if is_actual_date(val_text):
                cleaned_date = clean_date(val_text)
                if cleaned_date not in semi_finals_dates:
                    semi_finals_dates.append(cleaned_date)

        # ---------------- APRESENTADORES ---------------- #
        if "apresentador" in key:

            bold_blocks = val_cell.find_all("b")

            labels = [
                b.get_text(" ", strip=True).lower()
                for b in bold_blocks
            ]
            is_structured = any(
                ("semi" in l or "final" in l) and "green room" not in l
                for l in labels
            )

            if is_structured:
                for b in bold_blocks:
                    label = b.get_text(" ", strip=True).lower()
                    if "green room" in label:
                        continue
                    text = ""
                    sibling = b.next_sibling
                    while sibling:
                        if getattr(sibling, "name", None) == "b":
                            break
                        if getattr(sibling, "name", None) in ["sup", "p"]:
                            sibling = sibling.next_sibling
                            continue
                        if hasattr(sibling, "get_text"):
                            text += " " + sibling.get_text(" ", strip=True)
                        else:
                            text += " " + str(sibling)
                        sibling = sibling.next_sibling
                    text = re.sub(r"<.*?>", "", text).strip()
                    raw_names = re.split(r',|\s+e\s+|\s+&\s+', text)
                    clean_names = [
                        clean_presenter_name(n)
                        for n in raw_names
                        if clean_presenter_name(n)
                    ]
                    if not clean_names:
                        continue
                    if "semi" in label:
                        if "1" in label:
                            p_semis_map.setdefault(0, []).extend(clean_names)
                        elif "2" in label:
                            p_semis_map.setdefault(1, []).extend(clean_names)
                        else:
                            p_semis_map.setdefault("all", []).extend(clean_names)
                    elif "final" in label:
                        for n in clean_names:
                            if n not in p_final:
                                p_final.append(n)
                continue 

            blocks = []
            current = []
            for elem in val_cell.children:
                elem_name = getattr(elem, "name", None)
                if elem_name == "br":
                    if current:
                        blocks.append(" ".join(current).strip())
                        current = []
                    continue
                if hasattr(elem, "get_text"):
                    text = elem.get_text(" ", strip=True)
                else:
                    text = str(elem).strip()
                if not text:
                    continue
                if elem_name == "b":
                    if current:
                        blocks.append(" ".join(current).strip())
                    current = [text]
                elif elem_name == "small":
                    if not current and blocks:
                        blocks[-1] += " " + text
                    else:
                        current.append(text)
                else:
                    current.append(text)
            if current:
                blocks.append(" ".join(current).strip())
            for line in blocks:
                low_line = line.lower()
                if "green room" in low_line:
                    continue
                is_semi = "semi" in low_line or "meia" in low_line
                is_final = "final" in low_line
                semi_index = None
                if is_semi:
                    if "1" in low_line:
                        semi_index = 0
                    elif "2" in low_line:
                        semi_index = 1
                cleaned_line = re.sub(
                    r"\(.*?(semi|final|meia).*?\)",
                    "",
                    line,
                    flags=re.IGNORECASE
                )
                cleaned_line = re.sub(
                    r"^(semi[- ]?final\s*\d*|semifinal\s*\d*|final)[\s:,-]*",
                    "",
                    cleaned_line,
                    flags=re.IGNORECASE
                ).strip()
                raw_names = re.split(r',|\s+e\s+|\s+&\s+', cleaned_line)
                clean_names = [
                    clean_presenter_name(n)
                    for n in raw_names
                    if clean_presenter_name(n)
                ]
                if not clean_names:
                    continue
                if is_semi:
                    if semi_index is not None:
                        p_semis_map.setdefault(semi_index, []).extend(clean_names)
                    else:
                        p_semis_map.setdefault("all", []).extend(clean_names)
                elif is_final:
                    for n in clean_names:
                        if n not in p_final:
                            p_final.append(n)
                else:
                    for n in clean_names:
                        if n not in p_final:
                            p_final.append(n)

        # ---------------- DIRETOR MUSICAL ---------------- #
        if "diretor musical" in key:
            music_director = clean(val_text)

       # ---------------- LOCAL ---------------- #
        if "local" in key:
        
            raw_text_spaces = val_cell.get_text(" ", strip=True)
            has_multi_stage_pattern = re.search(r"\(.*?semi.*?\).*?\(.*?final.*?\)", raw_text_spaces, re.IGNORECASE)
            has_explicit_label_pattern = re.search(r"(Meias-finais:|Final:)", raw_text_spaces, re.IGNORECASE)

            def build_loc(parts_list):
                venue = None
                city = None

                if len(parts_list) >= 2:
                    venue = parts_list[0]
                    city = parts_list[1]

                    if year == 1992 and venue and "rtp" in venue.lower() and len(parts_list) >= 3:
                        city = parts_list[1]

                elif len(parts_list) == 1:
                    val = parts_list[0]
                    venue = val

                return {
                    "venue": clean(venue) if venue else None,
                    "city": clean(city) if city else None
                }

            loc_final = {"venue": None, "city": None}
            loc_semis_map = {}

            if has_multi_stage_pattern:
                blocks = []
                current = []

                for child in val_cell.children:
                    if getattr(child, "name", None) == "br":
                        block_text = " ".join(
                            part.get_text(" ", strip=True) if hasattr(part, "get_text") else str(part).strip()
                            for part in current
                            if str(part).strip()
                        ).strip()
                        if block_text:
                            blocks.append(block_text)
                        current = []
                    else:
                        current.append(child)

                if current:
                    block_text = " ".join(
                        part.get_text(" ", strip=True) if hasattr(part, "get_text") else str(part).strip()
                        for part in current
                        if str(part).strip()
                    ).strip()
                    if block_text:
                        blocks.append(block_text)

                for block in blocks:
                    block = block.strip()
                    if not block:
                        continue

                    low = block.lower()
                    is_semi = "semi" in low
                    is_final = "final" in low

                    cleaned_block = re.sub(r"\(.*?\)", "", block)
                    cleaned_block = re.sub(r"portugal", "", cleaned_block, flags=re.IGNORECASE)

                    loc = build_loc([p.strip() for p in cleaned_block.split(",") if p.strip()])

                    if loc["venue"] and not loc["city"] and "rtp" in loc["venue"].lower():
                        loc["city"] = "Lisboa"

                    if year in [1979, 1980] and loc["venue"] and not loc["city"] and "villaret" in loc["venue"].lower():
                        loc["city"] = "Lisboa"

                    if loc["venue"] and not loc["city"] and "lumiar" in loc["venue"].lower():
                        loc["city"] = "Lisboa"

                    if is_semi:
                        if "1" in low:
                            loc_semis_map[0] = loc
                        elif "2" in low:
                            loc_semis_map[1] = loc
                        else:
                            loc_semis_map["all"] = loc

                    if is_final:
                        loc_final = loc

                    else:
                        if loc["venue"] or loc["city"]:
                            loc_final = loc
            elif has_explicit_label_pattern:
                blocks = []
                current = []

                for child in val_cell.children:
                    if getattr(child, "name", None) == "br":
                        block_text = " ".join(
                            part.get_text(" ", strip=True) if hasattr(part, "get_text") else str(part).strip()
                            for part in current
                            if str(part).strip()
                        ).strip()
                        if block_text:
                            blocks.append(block_text)
                        current = []
                    else:
                        current.append(child)

                if current:
                    block_text = " ".join(
                        part.get_text(" ", strip=True) if hasattr(part, "get_text") else str(part).strip()
                        for part in current
                        if str(part).strip()
                    ).strip()
                    if block_text:
                        blocks.append(block_text)

                for block in blocks:
                    block = block.strip()
                    if not block:
                        continue

                    low = block.lower()
                    is_semi = "meias-finais" in low
                    is_final = "final" in low and "meias" not in low

                    cleaned_block = re.sub(r"^(Meias-finais:|Final:)\s*", "", block, flags=re.IGNORECASE)
                    cleaned_block = re.sub(r"\(.*?\)", "", cleaned_block)
                    cleaned_block = re.sub(r"portugal", "", cleaned_block, flags=re.IGNORECASE)

                    loc = build_loc([p.strip() for p in cleaned_block.split(",") if p.strip()])

                    if loc["venue"] and not loc["city"] and "rtp" in loc["venue"].lower():
                        loc["city"] = "Lisboa"

                    if is_semi:
                        loc_semis_map["all"] = loc

                    if is_final:
                        loc_final = loc
            else:
                raw_text = raw_text_spaces

                raw_text = re.sub(r"\(.*?\)", "", raw_text)
                raw_text = re.sub(r"portugal", "", raw_text, flags=re.IGNORECASE)

                for block in raw_text.split("\n"):
                
                    block = block.strip()
                    if not block:
                        continue
                    
                    low = block.lower()

                    is_semi = "semi" in low
                    is_final = "final" in low

                    loc = build_loc([p.strip() for p in block.split(",") if p.strip()])

                    if loc["venue"] and not loc["city"] and "rtp" in loc["venue"].lower():
                        loc["city"] = "Lisboa"

                    if is_semi:
                        if "1" in low:
                            loc_semis_map[0] = loc
                        elif "2" in low:
                            loc_semis_map[1] = loc
                        else:
                            loc_semis_map["all"] = loc

                    if is_final:
                        loc_final = loc

                    else:
                        if loc["venue"] or loc["city"]:
                            loc_final = loc

            semi_finals_locs = []

            for i in range(len(semi_finals_dates)):
                semi_finals_locs.append(
                    loc_semis_map.get(i)
                    or loc_semis_map.get("all")
                    or loc_final
                )

            location = {
                "final": loc_final,
                "semi_finals": semi_finals_locs
            }


    # ---------------- ORGANIZAÇÃO FINAL ---------------- #
    p_final = list(dict.fromkeys(p_final))

    final_p_semi = []
    for i in range(len(semi_finals_dates)):
        if i in p_semis_map:
            names = p_semis_map[i]
        elif "all" in p_semis_map:
            names = p_semis_map["all"]
        else:
            names = p_final
        final_p_semi.append(list(dict.fromkeys(names)))

    return {
        "dates": {
            "final": final_date,
            "semi_finals": semi_finals_dates
        },
        "presenters": {
            "final": p_final,
            "semi_finals": final_p_semi
        },
        "music_director": music_director,
        "location": location,
        "format": {
            "has_semi_finals": len(semi_finals_dates) > 0,
            "semi_finals_count": len(semi_finals_dates)
        }
    }
# ---------------- CONTESTANTS  ---------------- #

def parse_contestants(table, year):
    contestants = []

    current_stage = None
    rows = table.find_all("tr")

    for row in rows:
        text = row.get_text(" ", strip=True).lower()

        # detectar fases
        if "semifinal" in text or "semi-final" in text:
            if "1" in text:
                current_stage = "semi_final_1"
            elif "2" in text:
                current_stage = "semi_final_2"
        else:
            current_stage = "final"

        cols = row.find_all("td")

        if len(cols) < 3:
            continue

        song = clean(cols[0].get_text(" ", strip=True))
        artist = clean(cols[1].get_text(" ", strip=True))
        composer = clean(cols[2].get_text(" ", strip=True)) if len(cols) > 2 else None
        lyricist = clean(cols[3].get_text(" ", strip=True)) if len(cols) > 3 else None


        if not song or not artist:
            continue

        if song.lower() in ["canção", "cançao", "cançao "] or artist.lower() == "intérprete":
            continue

        contestants.append({
            "id": f"{year}_{len(contestants)+1}",
            "artist": artist,
            "title": song,
            "composer": split_names(composer),
            "lyricist": split_names(lyricist)
        })

    return contestants

# ----------------- CONTESTANTS 1976  ---------------- #

def parse_contestants_1976(table, year):
    contestants = []
    rows = table.find_all("tr")
    current_artist = "Carlos do Carmo"
    seen_songs = set()

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 3: 
            continue

        if len(cols) >= 6:
            song_idx, credits_idx = 2, 3
        else:
            song_idx, credits_idx = 1, 2

        song = clean(cols[song_idx].get_text(strip=True)).replace('"', '')
        credits_raw = clean(cols[credits_idx].get_text(strip=True))

        if not song or song.lower() in ["canção", "cançao"]: 
            continue
        if song in seen_songs: 
            continue
        seen_songs.add(song)

        composer, lyricist = None, None
        
        if credits_raw:
            credits_raw = credits_raw.replace("&amp;", "&")
            
            if "(m & l)" in credits_raw.lower() or "(m&l)" in credits_raw.lower() or "(m e l)" in credits_raw.lower():
                name = credits_raw.split('(')[0].strip()
                composer = lyricist = name
            else:
                parts = [p.strip() for p in re.split(r',| e ', credits_raw)]
                for p in parts:
                    name = re.sub(r'\(.*?\)', '', p).strip()
                    p_lower = p.lower()
                    
                    if "(m)" in p_lower:
                        composer = name
                    elif "(l)" in p_lower:
                        lyricist = name
                    elif any(x in p_lower for x in ["(m & l)", "(m&l)", "(m e l)"]):
                        composer = lyricist = name

        contestants.append({
            "id": f"{year}_{len(contestants)+1}",
            "artist": current_artist,
            "title": song,
            "composer": split_names(composer),
            "lyricist": split_names(lyricist)
        })
        
    return contestants

# -------------------- CONTESTANTS 1977  ---------------- #

def parse_contestants_1977(table, year):
    contestants = []
    rows = table.find_all("tr")
    
    last_song = None
    last_credits = None
    seen_pairs = set()

    for row in rows:
        cols = row.find_all(["td", "th"])
        if len(cols) < 3:
            continue

        first_col_text = cols[0].get_text(strip=True)
        
        if "º" in first_col_text or (first_col_text.isdigit() and len(cols) > 5):
            last_song = clean(cols[1].get_text(strip=True)).replace('"', '')
            last_credits = clean(cols[2].get_text(strip=True))
            current_artist = clean(cols[4].get_text(strip=True))
        else:
            if len(cols) >= 2:
                current_artist = clean(cols[1].get_text(strip=True))
            else:
                continue

        if not last_song or not current_artist:
            continue

        key = (current_artist, last_song)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)

        composer, lyricist = None, None
        if last_credits:
            txt = last_credits.replace("&amp;", "&")
            if any(x in txt.lower() for x in ["(m & l)", "(m&l)", "(m e l)"]):
                name = txt.split('(')[0].strip()
                composer = lyricist = name
            else:
                parts = [p.strip() for p in re.split(r',| e ', txt)]
                for p in parts:
                    clean_name = re.sub(r'\(.*?\)', '', p).strip()
                    if "(m)" in p.lower(): composer = clean_name
                    elif "(l)" in p.lower(): lyricist = clean_name
                    elif any(x in p.lower() for x in ["(m & l)", "(m&l)", "(m e l)"]):
                        composer = lyricist = clean_name

        contestants.append({
            "id": f"{year}_{len(contestants)+1}",
            "artist": current_artist,
            "title": last_song,
            "composer": split_names(composer),
            "lyricist": split_names(lyricist)
        })

    return contestants

# ---------------- CONTESTANTS 1969–1978 ---------------- #

def parse_contestants_69_78(table, year):
    contestants = []
    rows = table.find_all("tr")
    current_artist = None
    seen_songs = set()

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 3:
            continue

        # ---------------- ARTISTA ---------------- #
        artist_cell = row.find("td", rowspan=True)
        if artist_cell:
            current_artist = clean(artist_cell.get_text(" ", strip=True))
        else:
            possible_artist = clean(cols[1].get_text(" ", strip=True))
            if possible_artist and not possible_artist.isdigit() and "º" not in possible_artist:
                current_artist = possible_artist

        # ---------------- CANÇÃO ---------------- #
        song = clean(cols[2].get_text(" ", strip=True)) if len(cols) > 2 else None
        credits_raw = clean(cols[3].get_text(" ", strip=True)) if len(cols) > 3 else None

        if not song or not current_artist:
            continue

        key = (current_artist, song)
        if key in seen_songs:
            continue
        seen_songs.add(key)

        composer_list = []
        lyricist_list = []

        if credits_raw:
            text = credits_raw.replace("&amp;", "&").strip()
            text = text.replace(" e ", ", ")
            
            tag_pattern = r"\((?=[^)]*[ml])\s*(m|l|m\s*&\s*l|m\s*e\s*l|m&l)\s*\)"
            
            parts = [p.strip() for p in text.split(',')]
            temp_names = []

            for p in parts:
                if not p: continue
                
                tag_match = re.search(tag_pattern, p, re.IGNORECASE)
                name_only = re.sub(r"\(.*?\)", "", p).strip()
                temp_names.append(name_only)

                if tag_match:
                    tags = tag_match.group(1).lower()
                    for n in temp_names:
                        if any(x in tags for x in ["m & l", "m&l", "m e l"]):
                            composer_list.append(n)
                            lyricist_list.append(n)
                        else:
                            if "m" in tags: composer_list.append(n)
                            if "l" in tags: lyricist_list.append(n)
                    temp_names = []

        composer = ", ".join(dict.fromkeys(composer_list)) if composer_list else None
        lyricist = ", ".join(dict.fromkeys(lyricist_list)) if lyricist_list else None
        
        contestants.append({
            "id": f"{year}_{len(contestants)+1}",
            "artist": current_artist,
            "title": song,
            "composer": split_names(composer),
            "lyricist": split_names(lyricist)
        })

    return contestants

# ----------------- CONTESTANTS 1979-1980 --------------------- #

def parse_contestants_79_80(soup, year):
    contestants = []
    seen = set()

    tables = soup.find_all("table", class_="wikitable")

    for table in tables:
        caption = table.find("caption")
        if not caption:
            continue

        caption_text = caption.get_text(" ", strip=True).lower()

        if "semi-final" not in caption_text:
            continue

        rows = table.find_all("tr")

        for row in rows:
            cols = row.find_all("td")
            if len(cols) < 4:
                continue

            pos = cols[0].get_text(strip=True)
            if not any(c.isdigit() for c in pos):
                continue

            artist = clean(cols[1].get_text(" ", strip=True))
            song = clean(cols[2].get_text(" ", strip=True)).replace('"', '')
            credits = clean(cols[3].get_text(" ", strip=True))

            if not artist or not song:
                continue

            key = (artist, song)
            if key in seen:
                continue
            seen.add(key)

            composer = None
            lyricist = None
            lyricist_list = []

            if credits:
                credits = credits.replace("&amp;", "&")

                parts = [p.strip() for p in credits.split(",") if p.strip()]

                composers = []
                lyricists = []

                for p in parts:
                    p_lower = p.lower()

                    name = re.sub(r"\(.*?\)", "", p).strip()

                    if any(x in p_lower for x in ["(m & l)", "(m&l)", "(m e l)"]):
                        composers.append(name)
                        lyricists.append(name)

                    elif "(m)" in p_lower:
                        composers.append(name)

                    elif "(l)" in p_lower:
                        lyricists.append(name)

                composer = ", ".join(dict.fromkeys(composers)) if composers else None
                lyricist = ", ".join(dict.fromkeys(lyricists)) if lyricists else None

            contestants.append({
                "id": f"{year}_{len(contestants)+1}",
                "artist": artist,
                "title": song,
                "composer": split_names(composer),
                "lyricist": split_names(lyricist)
            })

    return contestants

# ----------------- CONTESTANT 1986 --------------------- #

def parse_contestants_1986(table, year=1986):
    contestants = []
    seen_songs = set()

    rows = table.find_all("tr")

    for row in rows:
        cols = row.find_all("td")

        if len(cols) < 4:
            continue

        rank = clean(cols[0].get_text(" ", strip=True))
        artist = clean(cols[1].get_text(" ", strip=True))
        song = clean(cols[2].get_text(" ", strip=True))
        credits = cols[3].get_text(" ", strip=True)

        if not artist or not song:
            continue

        composer_list = []
        lyricist_list = []

        if credits:
            credits = credits.replace("&amp;", "&")

            parts = re.split(r"\s*,\s*|\s+e\s+", credits)

            for part in parts:
                part = part.strip()
                if not part:
                    continue

                name = re.sub(r"\(.*?\)", "", part).strip()
                if not name:
                    continue

                p_lower = part.lower()

                if "(m & l)" in p_lower or "(m&l)" in p_lower or "(m e l)" in p_lower:
                    composer_list.append(name)
                    lyricist_list.append(name)

                elif "(m)" in p_lower:
                    composer_list.append(name)

                elif "(l)" in p_lower:
                    lyricist_list.append(name)

                else:
                    composer_list.append(name)
                    lyricist_list.append(name)

        composer = list(dict.fromkeys(composer_list))
        lyricist = list(dict.fromkeys(lyricist_list))

        song_norm = re.sub(r"[^\w]", "", song.lower())
        if song_norm in seen_songs:
            continue
        seen_songs.add(song_norm)

        contestants.append({
            "id": f"{year}_{len(contestants)+1}",
            "artist": artist,
            "title": song,
            "composer": split_names(", ".join(composer)) if composer else [],
            "lyricist": split_names(", ".join(lyricist)) if lyricist else []
        })

    return contestants

# ----------------- CONTESTANT 1992-1993 ---------------- #

def parse_contestants_92_93(table, year):
    contestants = []
    rows = table.find_all("tr")

    current_semi = None
    seen_titles = set()

    for row in rows:
        cols = row.find_all("td")

        # ---------------- SEMIFINAL ------------------- #
        header = row.find("th")
        if header:
            text = header.get_text(" ", strip=True)
            match = re.search(r"Semifinal\s*(\d+)", text, re.IGNORECASE)
            if match:
                current_semi = int(match.group(1))
            continue

        if len(cols) < 4:
            continue

        artist = clean(cols[1].get_text(" ", strip=True))
        song = clean(cols[2].get_text(" ", strip=True))
        credits_raw = clean(cols[3].get_text(" ", strip=True)) if len(cols) > 3 else None

        if not artist or not song:
            continue

        song_norm = re.sub(r'[^\w]', '', song.lower())
        
        if song_norm in seen_titles:
            continue
        seen_titles.add(song_norm)

        composer_list = []
        lyricist_list = []

        if credits_raw:
            text = credits_raw.replace("&amp;", "&")
            
            parts = []
            start = 0
            for match in re.finditer(r"\(.*?\)", text):
                end = match.end()
                parts.append(text[start:end].strip().strip(','))
                start = end
            
            if start < len(text):
                remaining = text[start:].strip().strip(',')
                if remaining: parts.append(remaining)

            temp_names = []
            for p in parts:
                p = p.strip()
                if not p: continue

                tags = re.findall(r"\((m|l|m\s*&\s*l|m\s*e\s*l)\)", p.lower())
                
                names_blob = re.sub(r"\(.*?\)", "", p).strip()
                
                if "," in names_blob:
                    current_names = [n.strip() for n in re.split(r",| e ", names_blob) if n.strip()]
                else:
                    current_names = [names_blob]

                if tags:
                    for tag in tags:
                        for n in current_names:
                            if "m" in tag: composer_list.append(n)
                            if "l" in tag: lyricist_list.append(n)
                else:
                    temp_names.extend(current_names)
        composer = ", ".join(dict.fromkeys(composer_list)) if composer_list else None
        lyricist = ", ".join(dict.fromkeys(lyricist_list)) if lyricist_list else None
                
        contestants.append({
            "id": f"{year}_{len(contestants)+1}",
            "artist": artist,
            "title": song,
            "composer": split_names(composer),
            "lyricist": split_names(lyricist)
        })

    return contestants

# ------------------ CONTESTANTS 1995 ------------------ #

def parse_contestants_1995(table, year):
    contestants = []
    rows = table.find_all("tr")
    seen_songs = set()

    for row in rows:
        cols = row.find_all(["td", "th"])
        
        if len(cols) < 4:
            continue
            
        if "Artista" in cols[1].get_text():
            continue

        artist = clean(cols[1].get_text(" ", strip=True))
        song = clean(cols[2].get_text(" ", strip=True)).replace('"', '')
        credits_raw = clean(cols[3].get_text(" ", strip=True))

        if not artist or not song or "vencedor" in artist.lower():
            continue

        song_norm = re.sub(r'[^\w]', '', song.lower())
        if song_norm in seen_songs: continue
        seen_songs.add(song_norm)

        composer_list = []
        lyricist_list = []

        if credits_raw:
            text = credits_raw.replace("&amp;", "&")
            parts = []
            start = 0
            for match in re.finditer(r"\(.*?\)", text):
                end = match.end()
                parts.append(text[start:end].strip().strip(','))
                start = end

            for p in parts:
                tags = re.findall(r"\((m|l|m\s*&\s*l|m\s*e\s*l)\)", p.lower())
                names_blob = re.sub(r"\(.*?\)", "", p).strip()
                
                if "," in names_blob:
                    current_names = [n.strip() for n in re.split(r",| e ", names_blob) if n.strip()]
                else:
                    current_names = [names_blob]

                if tags:
                    for tag in tags:
                        for n in current_names:
                            if "m" in tag: composer_list.append(n)
                            if "l" in tag: lyricist_list.append(n)

        raw_composer = ", ".join(dict.fromkeys(composer_list)) if composer_list else None
        raw_lyricist = ", ".join(dict.fromkeys(lyricist_list)) if lyricist_list else None

        contestants.append({
            "id": f"{year}_{len(contestants)+1}",
            "artist": artist,
            "title": song,
            "composer": split_names(raw_composer),
            "lyricist": split_names(raw_lyricist)
        })

    return contestants

# ---------------- CONTESTANTS 1997-2001 ----------------- #

def parse_contestants_97_01(soup, year):
    contestants = []
    seen_songs = set() 
    
    all_tables = soup.find_all("table", class_="wikitable")
    
    for table in all_tables:
        headers_text = table.get_text().lower()
        if "canção" not in headers_text or "artista" not in headers_text:
            continue
            
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all(["td", "th"])
            
            if len(cols) < 4:
                continue
            
            if "artista" in cols[1].get_text().lower():
                continue

            artist = clean(cols[1].get_text(" ", strip=True))
            song = clean(cols[2].get_text(" ", strip=True)).replace('"', '')
            credits_raw = clean(cols[3].get_text(" ", strip=True))

            if not artist or not song:
                continue

            song_norm = re.sub(r'[^\w]', '', song.lower())
            if song_norm in seen_songs:
                continue
            seen_songs.add(song_norm)

            composer_list = []
            lyricist_list = []

            if credits_raw:
                text = credits_raw.replace("&amp;", "&").replace(" e ", ", ")
                
                tag_pattern = r"\((?=[^)]*[ml])\s*(m|l|m\s*&\s*l|m\s*e\s*l|m&l)\s*\)"
                
                parts = [p.strip() for p in text.split(',') if p.strip()]

                temp_names = []
                for p in parts:
                    tag_match = re.search(tag_pattern, p, re.IGNORECASE)
                    
                    name_only = re.sub(r"\(.*?\)", "", p).strip()
                    temp_names.append(name_only)

                    if tag_match:
                        tags = tag_match.group(1).lower()
                        for n in temp_names:
                            if any(x in tags for x in ["m & l", "m&l", "m e l"]):
                                composer_list.append(n)
                                lyricist_list.append(n)
                            else:
                                if "m" in tags: composer_list.append(n)
                                if "l" in tags: lyricist_list.append(n)
                        temp_names = [] 

            contestants.append({
                "id": f"{year}_{len(contestants)+1}",
                "artist": artist,
                "title": song,
                "composer": split_names(", ".join(dict.fromkeys(composer_list))) if composer_list else None,
                "lyricist": split_names(", ".join(dict.fromkeys(lyricist_list))) if lyricist_list else None
            })

    return contestants

# -------------- CONTESTANTS 2003 --------------- #

def parse_contestants_2003(table, year):
    contestants = []
    rows = table.find_all("tr")
    seen_songs = set()

    for row in rows:
        cols = row.find_all(["td", "th"])
        
        if len(cols) < 5 or "Música" in cols[1].get_text():
            continue

        song = clean(cols[1].get_text(" ", strip=True)).replace('"', '')
        credits_raw = clean(cols[2].get_text(" ", strip=True))
        
        if not song:
            continue

        song_norm = re.sub(r'[^\w]', '', song.lower())
        if song_norm in seen_songs:
            continue
        seen_songs.add(song_norm)

        artist = "Rita Guerra" 
        composer_list = []
        
        if credits_raw:
            text = credits_raw.replace(" e ", ", ")
            names = [n.strip() for n in text.split(",") if n.strip()]
            composer_list = names

        contestants.append({
            "id": f"{year}_{len(contestants)+1}",
            "artist": artist, 
            "title": song,
            "composer": split_names(", ".join(dict.fromkeys(composer_list))) if composer_list else None,
            "lyricist": split_names(", ".join(dict.fromkeys(composer_list))) if composer_list else None
        })

    return contestants

# -------------- CONTESTANTS 2008 --------------- #

def parse_contestants_2008(table, year):
    contestants = []
    rows = table.find_all("tr")
    seen_songs = set()

    for row in rows:
        cols = row.find_all(["td", "th"])
        
        if len(cols) < 4 or "artista" in cols[1].get_text().lower():
            continue

        artist = clean(cols[1].get_text(" ", strip=True))
        song = clean(cols[2].get_text(" ", strip=True)).replace('"', '')
        credits_raw = clean(cols[3].get_text(" ", strip=True))

        if not artist or not song:
            continue

        song_norm = re.sub(r'[^\w]', '', song.lower())
        if song_norm in seen_songs:
            continue
        seen_songs.add(song_norm)

        composer_list = []
        lyricist_list = []

        if credits_raw:
            text = credits_raw.replace("&amp;", "&").replace(" e ", ", ")
            
            tag_pattern = r"\((?=[^)]*[ml])\s*(m|l|m\s*&\s*l|m\s*e\s*l|m&l)\s*\)"
            
            parts = [p.strip() for p in text.split(',')]
            temp_names = []

            for p in parts:
                if not p: continue
                
                tag_match = re.search(tag_pattern, p, re.IGNORECASE)
                name_only = re.sub(r"\(.*?\)", "", p).strip()
                temp_names.append(name_only)

                if tag_match:
                    tags = tag_match.group(1).lower()
                    for n in temp_names:
                        if any(x in tags for x in ["m & l", "m&l", "m e l"]):
                            composer_list.append(n)
                            lyricist_list.append(n)
                        else:
                            if "m" in tags: composer_list.append(n)
                            if "l" in tags: lyricist_list.append(n)
                    temp_names = [] 

        composer = ", ".join(dict.fromkeys(composer_list)) if composer_list else None
        lyricist = ", ".join(dict.fromkeys(lyricist_list)) if lyricist_list else None

        contestants.append({
            "id": f"{year}_{len(contestants)+1}",
            "artist": artist,
            "title": song,
            "composer": split_names(composer),
            "lyricist": split_names(lyricist)
        })

    return contestants

# -------------------- CONTESTANST 2010 ---------------------- #

def parse_contestants_2010(soup, year):
    contestants = []
    seen_songs = set()
    
    all_tables = soup.find_all("table", class_="wikitable")
    
    for table in all_tables:
        caption = table.find("caption")
        header_text = ""
        
        if caption:
            header_text = caption.get_text().lower()
        else:
            first_row = table.find("tr")
            if first_row:
                header_text = first_row.get_text().lower()

        if "semifinal" not in header_text or "votação" in header_text or "online" in header_text:
            continue

        rows = table.find_all("tr")

        for row in rows:
            cols = row.find_all(["td", "th"])
            
            if len(cols) < 4:
                continue

            if "artista" in cols[1].get_text().lower():
                continue

            artist = clean(cols[1].get_text(" ", strip=True))
            song = clean(cols[2].get_text(" ", strip=True)).replace('"', '')
            credits_raw = clean(cols[3].get_text(" ", strip=True))

            if not artist or not song:
                continue

            if "convertido" in artist.lower() or "televoto" in song.lower():
                continue

            song_key = re.sub(r'[^\w]', '', song.lower())
            song_key = song_key.replace('à','a').replace('á','a').replace('ã','a').replace('é','e').replace('ç','c')

            if song_key in seen_songs:
                continue
            seen_songs.add(song_key)

            composer_list = []
            lyricist_list = []
            
            if credits_raw:
                text = credits_raw.replace("&amp;", "&")
            
                matches = list(re.finditer(r"([^()]+?)\s*\((m|l|m\s*&\s*l|m\s*e\s*l|m&l)\)", text, re.IGNORECASE))
            
                for match in matches:
                    names_part = match.group(1).strip()
                    tag = match.group(2).lower()
            
                    names = re.split(r", | & ", names_part)
                    names = [n.strip() for n in names if n.strip()]
            
                    for n in names:
                        if any(x in tag for x in ["m & l", "m&l", "m e l"]):
                            composer_list.append(n)
                            lyricist_list.append(n)
                        else:
                            if "m" in tag:
                                composer_list.append(n)
                            if "l" in tag:
                                lyricist_list.append(n)

            contestants.append({
                "id": f"{year}_{len(contestants)+1}",
                "artist": artist,
                "title": song,
                "composer": split_names(", ".join(dict.fromkeys(composer_list))) if composer_list else None,
                "lyricist": split_names(", ".join(dict.fromkeys(lyricist_list))) if lyricist_list else None
            })

    return contestants[:24]

# ---------------- CONTESTANTS 2011 ------------------- #

def parse_contestants_2011(soup, year):
    contestants = []
    seen_songs = set()
    all_tables = soup.find_all("table", class_="wikitable")
    
    for table in all_tables:
        header_row = table.find("tr")
        if not header_row: continue
        header_text = header_row.get_text().lower()

        if "televoto" not in header_text or "online" in header_text:
            continue
        
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all(["td", "th"])
            if len(cols) < 5: continue
            if "artista" in cols[1].get_text().lower(): continue

            artist = clean(cols[1].get_text(" ", strip=True))
            song = clean(cols[2].get_text(" ", strip=True)).replace('"', '')
            credits_raw = clean(cols[3].get_text(" ", strip=True))

            if not artist or not song or "total" in artist.lower():
                continue

            song_key = re.sub(r'[^\w]', '', song.lower()).translate(str.maketrans("áàãâéêíóôõúç", "aaaaeeiooouc"))
            if song_key in seen_songs: continue
            seen_songs.add(song_key)

            composer_list, lyricist_list = [], []
            if credits_raw:
                text = credits_raw.replace("&amp;", "&")
                
                tag_pattern = r"\((m|l|m\s*&\s*l|m\s*e\s*l|m&l)\)"
                
                parts = [p.strip() for p in re.split(r',| e ', text) if p.strip()]
                temp_names = []

                for p in parts:
                    tag_match = re.search(tag_pattern, p, re.IGNORECASE)
                    
                    name_only = re.sub(r"\(.*?\)", "", p).strip()
                    if name_only:
                        temp_names.append(name_only)

                    if tag_match:
                        tag_content = tag_match.group(1).lower()
                        
                        for n in temp_names:
                            if 'm' in tag_content:
                                composer_list.append(n)
                            if 'l' in tag_content:
                                lyricist_list.append(n)
                        
                        temp_names = []
                        
            contestants.append({
                "id": f"{year}_{len(contestants)+1}",
                "artist": artist,
                "title": song,
                "composer": split_names(", ".join(dict.fromkeys(composer_list))) if composer_list else None,
                "lyricist": split_names(", ".join(dict.fromkeys(lyricist_list))) if lyricist_list else None
            })
    return contestants

# ------------------- CONTESTANTS 2017 ------------------- #

def parse_contestants_2017(soup, year):
    contestants = []
    seen_songs = set()
    
    all_tables = soup.find_all("table", class_="wikitable")
    
    for table in all_tables:
        header_text = table.get_text().lower()
        if "compositore(s)" not in header_text or "artista" not in header_text:
            continue
            
        rows = table.find_all("tr")
        for row in rows:
            num_col = row.find("th")
            cols = row.find_all("td")
            
            if not num_col or not num_col.get_text(strip=True).isdigit() or len(cols) < 3:
                continue

            artist = clean(cols[0].get_text(" ", strip=True))
            song = clean(cols[1].get_text(" ", strip=True)).replace('"', '')
            composer_raw = clean(cols[2].get_text(" ", strip=True))

            if not artist or not song:
                continue

            song_norm = re.sub(r'[^\w]', '', song.lower())
            if song_norm in seen_songs:
                continue
            seen_songs.add(song_norm)

            composer_name = re.sub(r"\(.*?\)", "", composer_raw).strip()

            contestants.append({
                "id": f"{year}_{len(contestants)+1}",
                "artist": artist,
                "title": song,
                "composer": split_names(composer_name),
                "lyricist": split_names(composer_name)
            })

    return contestants

# ------------------ CONTESTANTS 2018 -------------------- #

def parse_contestants_2018(soup, year):
    contestants = []
    seen_songs = set()

    all_tables = soup.find_all("table", class_="wikitable")
    
    for table in all_tables:
        header_text = table.get_text().lower()

        if "autor da letra" not in header_text or "compositor" not in header_text:
            continue
            
        rows = table.find_all("tr")

        for row in rows:

            if row.find("th", colspan="6") or row.find("th", width="5%"):
                continue

            num_col = row.find("th")
            cols = row.find_all("td")
            
            if not num_col or not cols:
                continue

            song = clean(
                cols[0].get_text(" ", strip=True)
            ).replace('"', '')

            if cols[1].has_attr('colspan') and int(cols[1]['colspan']) == 3:

                names = [
                    clean(a.get_text(strip=True))
                    for a in cols[1].find_all("a")
                ]

                if names:
                    val = "\n".join(names)
                else:
                    val = clean(cols[1].get_text("\n", strip=True))

                artist = lyricist = composer = val

            elif cols[1].has_attr('colspan') and int(cols[1]['colspan']) == 2:

                artist_names = [
                    clean(a.get_text(strip=True))
                    for a in cols[1].find_all("a")
                ]

                composer_names = [
                    clean(a.get_text(strip=True))
                    for a in cols[2].find_all("a")
                ]

                artist = (
                    "\n".join(artist_names)
                    if artist_names
                    else clean(cols[1].get_text("\n", strip=True))
                )

                lyricist = artist

                composer = (
                    "\n".join(composer_names)
                    if composer_names
                    else clean(cols[2].get_text("\n", strip=True))
                )

            elif len(cols) > 2 and cols[2].has_attr('colspan') and int(cols[2]['colspan']) == 2:

                artist_names = [
                    clean(a.get_text(strip=True))
                    for a in cols[1].find_all("a")
                ]

                shared_names = [
                    clean(a.get_text(strip=True))
                    for a in cols[2].find_all("a")
                ]

                artist = (
                    "\n".join(artist_names)
                    if artist_names
                    else clean(cols[1].get_text("\n", strip=True))
                )

                shared = (
                    "\n".join(shared_names)
                    if shared_names
                    else clean(cols[2].get_text("\n", strip=True))
                )

                lyricist = composer = shared

            elif len(cols) >= 4:

                artist_names = [
                    clean(a.get_text(strip=True))
                    for a in cols[1].find_all("a")
                ]

                lyricist_names = [
                    clean(a.get_text(strip=True))
                    for a in cols[2].find_all("a")
                ]

                composer_names = [
                    clean(a.get_text(strip=True))
                    for a in cols[3].find_all("a")
                ]

                artist = (
                    "\n".join(artist_names)
                    if artist_names
                    else clean(cols[1].get_text("\n", strip=True))
                )

                lyricist = (
                    "\n".join(lyricist_names)
                    if lyricist_names
                    else clean(cols[2].get_text("\n", strip=True))
                )

                composer = (
                    "\n".join(composer_names)
                    if composer_names
                    else clean(cols[3].get_text("\n", strip=True))
                )

            else:
                continue

            if not artist or not song:
                continue

            song_norm = re.sub(r'[^\w]', '', song.lower())

            if song_norm in seen_songs:
                continue

            seen_songs.add(song_norm)

            contestants.append({
                "id": f"{year}_{len(contestants)+1}",
                "artist": artist,
                "title": song,
                "composer": split_names(composer),
                "lyricist": split_names(lyricist)
            })

    return contestants

# ------------------ CONTESTANS 2019 -------------------- #

def parse_contestants_2019(soup, year):
    contestants = []
    seen_songs = set()
    all_tables = soup.find_all("table", class_="wikitable")
    
    for table in all_tables:
        header_text = table.get_text().lower()
        if "música e letra" not in header_text or "intérprete" not in header_text:
            continue
            
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if not cols or len(cols) < 4:
                continue

            artist = clean(cols[0].get_text(" ", strip=True))
            song = clean(cols[1].get_text(" ", strip=True)).replace('"', '')
            credits_raw = clean(cols[3].get_text(" ", strip=True))

            if not artist or not song:
                continue

            song_norm = re.sub(r'[^\w]', '', song.lower())
            if song_norm in seen_songs:
                continue
            seen_songs.add(song_norm)

            composer_list = []
            lyricist_list = []

            if credits_raw:
                text = credits_raw.replace("&amp;", "&").replace(" e ", ", ").replace(" & ", ", ")
                
                if not re.search(r"\(.*?[ml].*?\)", text.lower()):
                    names = [n.strip() for n in text.split(',') if n.strip()]
                    composer_list = names
                    lyricist_list = names
                else:
                    pattern = r"([^,()]+)\s*\(([^)]*[ml][^)]*)\)"
                    matches = list(re.finditer(pattern, text, re.IGNORECASE))
                    
                    if matches:
                        for match in matches:
                            name_part = match.group(1).strip()
                            tags = match.group(2).lower()
                            
                            names = [n.strip() for n in re.split(r',|&', name_part) if n.strip()]
                            
                            for n in names:
                                if 'm' in tags: composer_list.append(n)
                                if 'l' in tags: lyricist_list.append(n)
                    else:
                        names = [n.strip() for n in text.split(',') if n.strip()]
                        composer_list = names
                        lyricist_list = names

            contestants.append({
                "id": f"{year}_{len(contestants)+1}",
                "artist": artist,
                "title": song,
                "composer": split_names(", ".join(dict.fromkeys(composer_list))) if composer_list else None,
                "lyricist": split_names(", ".join(dict.fromkeys(lyricist_list))) if lyricist_list else None
            })

    return contestants

# ----------------- CONTESTANTS 2020 ------------------ #

def parse_contestants_2020(soup, year):
    contestants = []
    seen_songs = set()
    all_tables = soup.find_all("table", class_="wikitable")
    
    for table in all_tables:
        header_text = table.get_text().lower()
        if "música e letra" not in header_text or "intérprete" not in header_text:
            continue
            
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if not cols or len(cols) < 4:
                continue

            artist = clean(cols[0].get_text(" ", strip=True))
            song_raw = cols[1].get_text(" ", strip=True)
            song = clean(re.sub(r"\(.*?\)", "", song_raw)) 
            
            credits_raw = clean(cols[3].get_text(" ", strip=True))

            if not artist or not song:
                continue

            song_norm = re.sub(r'[^\w]', '', song.lower())
            if song_norm in seen_songs:
                continue
            seen_songs.add(song_norm)

            composer_list = []
            lyricist_list = []


            if credits_raw:
            
                text = credits_raw.replace("&amp;", "&")
                text = text.replace(";", ",")
                text = re.sub(r"\s+e\s+", ", ", text)
                text = re.sub(r"\s*&\s*", ", ", text)

                if not re.search(r"\(([^)]*[ml/][^)]*)\)", text.lower()):
                
                    names = [
                        re.sub(r"\*", "", n).strip()
                        for n in text.split(",")
                        if n.strip()
                    ]

                    composer_list.extend(names)
                    lyricist_list.extend(names)

                else:
                
                    parts = [p.strip() for p in text.split(",") if p.strip()]

                    temp_names = []

                    for p in parts:
                    
                        tag_match = re.search(
                            r"\(([^)]*[ml/][^)]*)\)",
                            p,
                            re.IGNORECASE
                        )

                        if tag_match:
                        
                            name_only = re.sub(r"\(.*?\)", "", p)
                            name_only = re.sub(r"\*", "", name_only).strip()

                            if name_only:
                                temp_names.append(name_only)

                            tags = tag_match.group(1).lower()

                            for n in temp_names:
                            
                                if "m" in tags:
                                    composer_list.append(n)

                                if "l" in tags:
                                    lyricist_list.append(n)

                            temp_names = []

                        else:
                            clean_name = re.sub(r"\*", "", p).strip()

                            if clean_name:
                                temp_names.append(clean_name)
                                
            contestants.append({
                "id": f"{year}_{len(contestants)+1}",
                "artist": artist,
                "title": song,
                "composer": split_names(", ".join(dict.fromkeys(composer_list))) if composer_list else None,
                "lyricist": split_names(", ".join(dict.fromkeys(lyricist_list))) if lyricist_list else None
            })

    return contestants

# ------------------ CONTESTANTS 2024 -------------------- #

def parse_contestants_2024(soup, year):
    contestants = []
    seen_songs = set()
    
    all_tables = soup.find_all("table", class_="wikitable")
    
    for table in all_tables:
        header_text = table.get_text().lower()
        
        if "semifinal" not in header_text or "intérprete" not in header_text:
            continue
            
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all(["td", "th"])
            
            if len(cols) < 10:
                continue
                
            pos_text = cols[0].get_text(strip=True)
            if not pos_text.isdigit():
                continue

            artist = clean(cols[1].get_text(" ", strip=True))
            
            song_raw = cols[2].get_text(" ", strip=True)
            song = clean(re.sub(r"\(.*?\)", "", song_raw)).replace('"', '')

            if not artist or not song:
                continue

            song_norm = re.sub(r'[^\w]', '', song.lower())
            if song_norm in seen_songs:
                continue
            seen_songs.add(song_norm)

            contestants.append({
                "id": f"{year}_{len(contestants)+1}",
                "artist": artist,
                "title": song,
                "composer": split_names(artist),
                "lyricist": split_names(artist)
            })

    return contestants

# ------------------ CONTESTANTS 2026 -------------------- #

def parse_contestants_2026(soup, year):
    contestants = []
    seen_songs = set()
    all_tables = soup.find_all("table", class_="wikitable")
    
    for table in all_tables:
        header_text = table.get_text().lower()
        if "composição" not in header_text or "intérprete" not in header_text:
            continue
            
        rows = table.find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            
            if not cols or len(cols) < 3:
                continue

            artist = clean(cols[0].get_text(" ", strip=True))
            song = clean(cols[1].get_text(" ", strip=True)).replace('"', '')
            
            if not artist or not song:
                continue

            song_norm = re.sub(r'[^\w]', '', song.lower())
            if song_norm in seen_songs:
                continue
            seen_songs.add(song_norm)

            if cols[2].has_attr('colspan') and int(cols[2]['colspan']) == 2:
                val = clean(cols[2].get_text(" ", strip=True))
                lyricist = val
                composer = val
            
            elif len(cols) >= 4:
                lyricist = clean(cols[2].get_text(" ", strip=True))
                composer = clean(cols[3].get_text(" ", strip=True))
            
            else:
                val = clean(cols[2].get_text(" ", strip=True))
                lyricist = val
                composer = val

            contestants.append({
                "id": f"{year}_{len(contestants)+1}",
                "artist": artist,
                "title": song,
                "composer": split_names(composer),
                "lyricist": split_names(lyricist)
            })

    return contestants

# ---------------- FIND TABLE ---------------- #

def get_contestants_tables(soup):
    tables = soup.find_all("table", class_="wikitable")
    valid = []

    for table in tables:
        text = table.get_text(" ", strip=True).lower()
        if "canção" in text and "intérprete" in text and "música" in text and "letra" in text:
            valid.append(table)

    return valid

def get_table_69_78(soup):
    tables = soup.find_all("table", class_="wikitable")

    for t in tables:
        if "Pontuação" in t.get_text():
            return t

    return None

# ---------------- RUN ---------------- #

data = []

for year in years:
    print(f"A processar {year}...")

    url = BASE_URL.format(year)

    try:
        html = session.get(url, headers=headers).text
        soup = BeautifulSoup(html, "html.parser")

        info = extract_info(soup)

        contestants = []

        if year <= 1968:
            tables = get_contestants_tables(soup)
            for t in tables:
                contestants.extend(parse_contestants(t, year))
        elif year == 1976:
            table = get_table_69_78(soup)
            if table: contestants = parse_contestants_1976(table, year)
        elif year == 1977:
            table_77 = None
            all_tables = soup.find_all("table", {"class": "wikitable"})
            for t in all_tables:
                if "Final" in t.get_text():
                    table_77 = t
                    break
            
            if not table_77:
                table_77 = get_table_69_78(soup)
                
            if table_77:
                contestants = parse_contestants_1977(table_77, year)
        elif 1969 <= year <= 1975 or year == 1978 or 1981 <= year <= 1985 or year == 1987 or 1989 <= year <= 1991 or year == 1996 or 1998 <= year <= 2000 or year == 2004 or 2006 <= year <= 2007:
            table = get_table_69_78(soup)
            if table: contestants = parse_contestants_69_78(table, year)
        elif year == 1979 or year == 1980:
            contestants = parse_contestants_79_80(soup, year)
        elif year == 1986:
            contestants = parse_contestants_1986(soup, year)
        elif year in [1988,2002,2005,2013,2016]:
            print(f"⚠️ {year} ignorado (sem Festival da Canção)")
            continue
        elif year in [1992, 1993, 1994]:
            contestants = parse_contestants_92_93(soup, year)
        elif year == 1995:
            t_95 = None
            all_tables = soup.find_all("table", class_="wikitable")
            for t in all_tables:
                headers_text = t.get_text().lower()
                if "música (m)" in headers_text and "artista" in headers_text:
                    t_95 = t
                    break
            
            if t_95:
                contestants = parse_contestants_1995(t_95, year)
            else:
                t_95 = get_table_69_78(soup)
                if t_95: contestants = parse_contestants_1995(t_95, year)
        elif year in [1997,2001,2009,2014,2015]:
            contestants = parse_contestants_97_01(soup, year)
        elif year == 2003:
            t_03 = None
            for t in soup.find_all("table", class_="wikitable"):
                if "Compositor" in t.get_text():
                    t_03 = t
                    break
            if t_03:
                contestants = parse_contestants_2003(t_03, year)
        elif year == 2008:
            t_08 = None
            all_tables = soup.find_all("table", class_="wikitable")
            for t in all_tables:
                headers_text = t.get_text().lower()
                if "votos" in headers_text and "música (m)" in headers_text:
                    t_08 = t
                    break
            
            if t_08:
                contestants = parse_contestants_2008(t_08, year)
            else:
                print(f"⚠️ Não foi possível encontrar a tabela de competição de {year}")
        elif year == 2010:
            contestants = parse_contestants_2010(soup, year)
        elif year in [2011,2012]:
            contestants = parse_contestants_2011(soup, year)
        elif year == 2017:
            contestants = parse_contestants_2017(soup, year)
        elif year == 2018:
            contestants = parse_contestants_2018(soup, year)
        elif year == 2019:
            contestants = parse_contestants_2019(soup, year)
        elif year in [2020,2021,2022,2023]:
            contestants = parse_contestants_2020(soup, year)
        elif year in [2024,2025]:
            contestants = parse_contestants_2024(soup, year)
        elif year == 2026:
            contestants = parse_contestants_2026(soup, year)
                
        # ---------------- fallback ---------------- #
        else:
            tables = get_contestants_tables(soup)
            for t in tables:
                contestants.extend(parse_contestants(t, year))

        winner = extract_winner(soup)
        
        # Ajustes Manuais necessários
        if year == 2003:
            winner = {"artist": "Rita Guerra", "song": "Deixa-me sonhar (só mais uma vez)"}
        if year == 2012:
            winner = {"artist": "Filipa Sousa", "song": "Vida minha"}

        if winner:
            resultado = EURO_MAP.get(year)
            if resultado:
                resultado = re.sub(r"\[.*?\]", "", resultado).strip()
                if "não participou" in resultado.lower():
                    resultado = "Não participou"
            
            winner["eurovision_result"] = resultado if resultado else "N/A"

        data.append({
            "year": year,
            "entries_count": len(contestants),
            "dates": info["dates"],
            "presenters": info["presenters"],
            "music_director": info["music_director"],
            "location": info["location"],
            "format": {
                "has_semi_finals": len(info["dates"]["semi_finals"]) > 0,
                "semi_finals_count": len(info["dates"]["semi_finals"])
            },
            "winner": winner,
            "contestants": contestants
        })

        time.sleep(1)

    except Exception as e:
        print(f"❌ Erro em {year}: {e}")


with open("festival_cancao.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ DONE")