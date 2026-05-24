import argparse
import json
import re
import unicodedata
from datetime import datetime
from pathlib import Path

from rdflib import Graph, Literal, Namespace, RDF, XSD

MONTHS_PT = {
    "janeiro": 1,
    "fevereiro": 2,
    "marco": 3,
    "abril": 4,
    "maio": 5,
    "junho": 6,
    "julho": 7,
    "agosto": 8,
    "setembro": 9,
    "outubro": 10,
    "novembro": 11,
    "dezembro": 12,
}

DATE_PATTERN = re.compile(
    r"(\d{1,2})\s+de\s+([a-zA-ZçÇãÃáÁàÀâÂéÉêÊíÍóÓôÔõÕúÚ]+)(?:\s+de\s+(\d{4}))?",
    re.IGNORECASE,
)


def normalize_text(text: str) -> str:
    text = unicodedata.normalize("NFD", text)
    text = "".join(ch for ch in text if unicodedata.category(ch) != "Mn")
    return text


def slugify(text: str) -> str:
    text = normalize_text(text or "")
    text = text.lower()
    text = re.sub(r"[^a-z0-9]+", "_", text)
    return text.strip("_") or "item"


def normalize_for_match(text: str) -> str:
    text = normalize_text(text or "").lower()
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def parse_first_pt_date(text: str, default_year: int | None) -> datetime | None:
    if not text:
        return None

    match = DATE_PATTERN.search(text)
    if not match:
        return None

    day = int(match.group(1))
    month_name = normalize_text(match.group(2)).lower()
    month = MONTHS_PT.get(month_name)

    year_str = match.group(3)
    year = int(year_str) if year_str else default_year

    if not month or not year:
        return None

    try:
        return datetime(year, month, day, 0, 0, 0)
    except ValueError:
        return None


def as_list(value):
    if value is None:
        return []
    if isinstance(value, list):
        return [v for v in value if v]
    return [value]


def get_base_namespace(graph: Graph) -> Namespace:
    for prefix, uri in graph.namespace_manager.namespaces():
        if prefix == "":
            return Namespace(str(uri))
    raise RuntimeError("Nao foi encontrado prefixo base ':' no TTL.")


def main():
    parser = argparse.ArgumentParser(
        description="Povoa uma ontologia TTL a partir do festival_cancao.json"
    )
    parser.add_argument("--template", default="festival.ttl", help="TTL base da ontologia")
    parser.add_argument("--json", default="festival_cancao.json", help="JSON com os dados")
    parser.add_argument("--output", default="festival_povoado.ttl", help="TTL de saida")
    args = parser.parse_args()

    template_path = Path(args.template)
    json_path = Path(args.json)
    output_path = Path(args.output)

    graph = Graph()
    graph.parse(template_path, format="turtle")

    EX = get_base_namespace(graph)

    with json_path.open("r", encoding="utf-8") as f:
        editions = json.load(f)

    city_cache = {}
    venue_cache = {}
    person_cache = {}

    def city_individual(city_name: str):
        key = city_name.strip()
        if key in city_cache:
            return city_cache[key]

        uri = EX[f"City_{slugify(key)}"]
        graph.add((uri, RDF.type, EX.City))
        graph.add((uri, EX.cityName, Literal(key)))
        city_cache[key] = uri
        return uri

    def venue_individual(venue_name: str, city_name: str | None = None):
        key = venue_name.strip()
        if key in venue_cache:
            uri = venue_cache[key]
        else:
            uri = EX[f"Venue_{slugify(key)}"]
            graph.add((uri, RDF.type, EX.Venue))
            graph.add((uri, EX.venueName, Literal(key)))
            venue_cache[key] = uri

        if city_name:
            city_uri = city_individual(city_name)
            graph.add((uri, EX.locatedIn, city_uri))

        return uri

    def person_individual(name: str, class_uri):
        key = (name.strip(), str(class_uri))
        if key in person_cache:
            return person_cache[key]

        uri = EX[f"{class_uri.split('#')[-1] if '#' in str(class_uri) else class_uri.split('/')[-1]}_{slugify(name)}"]
        graph.add((uri, RDF.type, class_uri))
        graph.add((uri, EX.personName, Literal(name.strip())))
        person_cache[key] = uri
        return uri

    for edition_data in editions:
        year = edition_data.get("year")
        if not year:
            continue

        edition_uri = EX[f"Edition_{year}"]
        graph.add((edition_uri, RDF.type, EX.FestivalEdition))
        graph.add((edition_uri, EX.editionYear, Literal(year, datatype=XSD.int)))

        # Final
        final_phase_uri = EX[f"Final_{year}"]
        graph.add((final_phase_uri, RDF.type, EX.Final))
        graph.add((edition_uri, EX.hasPhase, final_phase_uri))

        final_date = edition_data.get("dates", {}).get("final")
        final_dt = parse_first_pt_date(final_date, default_year=year)
        if final_dt:
            graph.add((final_phase_uri, EX.phaseDate, Literal(final_dt.strftime('%Y-%m-%d'), datatype=XSD.date)))

        final_loc = edition_data.get("location", {}).get("final", {})
        final_venue = final_loc.get("venue")
        final_city = final_loc.get("city")
        if final_venue:
            venue_uri = venue_individual(final_venue, final_city)
            graph.add((final_phase_uri, EX.heldAt, venue_uri))

        for presenter_name in as_list(edition_data.get("presenters", {}).get("final")):
            presenter_uri = person_individual(presenter_name, EX.Presenter)
            graph.add((final_phase_uri, EX.hasPresenter, presenter_uri))

        # Semi-finais
        semi_dates = as_list(edition_data.get("dates", {}).get("semi_finals"))
        semi_presenters = as_list(edition_data.get("presenters", {}).get("semi_finals"))
        semi_locations = as_list(edition_data.get("location", {}).get("semi_finals"))

        for idx, semi_date in enumerate(semi_dates, start=1):
            semi_uri = EX[f"SemiFinal_{year}_{idx}"]
            graph.add((semi_uri, RDF.type, EX.SemiFinal))
            graph.add((edition_uri, EX.hasPhase, semi_uri))

            semi_dt = parse_first_pt_date(str(semi_date), default_year=year)
            if semi_dt:
                graph.add((semi_uri, EX.phaseDate, Literal(semi_dt.strftime('%Y-%m-%d'), datatype=XSD.date)))

            if idx - 1 < len(semi_locations) and isinstance(semi_locations[idx - 1], dict):
                loc = semi_locations[idx - 1]
                venue_name = loc.get("venue")
                city_name = loc.get("city")
                if venue_name:
                    semi_venue_uri = venue_individual(venue_name, city_name)
                    graph.add((semi_uri, EX.heldAt, semi_venue_uri))

            presenters_block = semi_presenters[idx - 1] if idx - 1 < len(semi_presenters) else []
            for presenter_name in as_list(presenters_block):
                presenter_uri = person_individual(presenter_name, EX.Presenter)
                graph.add((semi_uri, EX.hasPresenter, presenter_uri))

        # Diretor musical
        music_director = edition_data.get("music_director")
        if music_director:
            md_uri = person_individual(music_director, EX.MusicDirector)
            graph.add((edition_uri, EX.hasMusicDirector, md_uri))

        contestants = as_list(edition_data.get("contestants"))
        contestant_uri_by_key = {}
        contestant_uri_by_norm_key = {}
        contestant_uri_by_song = {}
        contestant_uri_by_artist = {}
        contestant_records = []

        for idx, contestant in enumerate(contestants, start=1):
            contestant_id = contestant.get("id") or f"{year}_{idx}"
            contestant_uri = EX[f"Contestant_{slugify(contestant_id)}"]
            graph.add((contestant_uri, RDF.type, EX.Contestant))
            graph.add((contestant_uri, EX.contestantId, Literal(contestant_id)))
            graph.add((contestant_uri, EX.belongsToEdition, edition_uri))
            graph.add((edition_uri, EX.hasContestant, contestant_uri))

            artist_name = contestant.get("artist")
            if artist_name:
                graph.add((contestant_uri, EX.artistName, Literal(artist_name)))

            title = contestant.get("title")

            song_uri = None
            if title:
                song_uri = EX[f"Song_{slugify(contestant_id)}"]
                graph.add((song_uri, RDF.type, EX.Song))
                graph.add((song_uri, EX.songTitle, Literal(title)))
                graph.add((contestant_uri, EX.performsSong, song_uri))

            if song_uri:
                graph.add((song_uri, EX.performedBy, contestant_uri))

            for composer_name in as_list(contestant.get("composer")):
                if not song_uri:
                    continue
                composer_uri = person_individual(composer_name, EX.Composer)
                graph.add((song_uri, EX.hasComposer, composer_uri))

            for lyricist_name in as_list(contestant.get("lyricist")):
                if not song_uri:
                    continue
                lyricist_uri = person_individual(lyricist_name, EX.Lyricist)
                graph.add((song_uri, EX.hasLyricist, lyricist_uri))

            artist_exact = str(artist_name or "").strip().lower()
            title_exact = str(title or "").strip().lower()
            artist_norm = normalize_for_match(str(artist_name or ""))
            title_norm = normalize_for_match(str(title or ""))

            key = (artist_exact, title_exact)
            norm_key = (artist_norm, title_norm)

            contestant_uri_by_key[key] = contestant_uri
            contestant_uri_by_norm_key[norm_key] = contestant_uri

            if title_norm:
                contestant_uri_by_song.setdefault(title_norm, []).append(contestant_uri)
            if artist_norm:
                contestant_uri_by_artist.setdefault(artist_norm, []).append(contestant_uri)

            contestant_records.append((contestant_uri, artist_norm, title_norm))

        winner = edition_data.get("winner", {}) or {}
        winner_artist = str(winner.get("artist") or "").strip().lower()
        winner_song = str(winner.get("song") or "").strip().lower()

        winner_artist_norm = normalize_for_match(str(winner.get("artist") or ""))
        winner_song_norm = normalize_for_match(str(winner.get("song") or ""))

        winner_uri = contestant_uri_by_key.get((winner_artist, winner_song))

        if not winner_uri:
            winner_uri = contestant_uri_by_norm_key.get((winner_artist_norm, winner_song_norm))

        if not winner_uri and winner_song_norm:
            candidates = contestant_uri_by_song.get(winner_song_norm, [])
            if len(candidates) == 1:
                winner_uri = candidates[0]

        if not winner_uri and winner_artist_norm:
            candidates = contestant_uri_by_artist.get(winner_artist_norm, [])
            if len(candidates) == 1:
                winner_uri = candidates[0]

        if not winner_uri and winner_song_norm:
            fuzzy = []
            for contestant_uri, artist_norm, title_norm in contestant_records:
                if winner_artist_norm and artist_norm != winner_artist_norm:
                    continue
                if not title_norm:
                    continue
                if winner_song_norm in title_norm or title_norm in winner_song_norm:
                    fuzzy.append(contestant_uri)

            if len(fuzzy) == 1:
                winner_uri = fuzzy[0]
        if winner_uri:
            winner_contestant_uri = winner_uri
            winner_song_uri = None

            for contestant_uri, artist_norm, title_norm in contestant_records:
                if contestant_uri == winner_contestant_uri:
                    winner_song_uri = next(graph.objects(contestant_uri, EX.performsSong), None)
                    break

            if winner_song_uri:
                graph.add((edition_uri, EX.hasWinner, winner_song_uri))
                eurovision_result = winner.get("eurovision_result")
                if eurovision_result:
                    graph.add((winner_song_uri, EX.eurovisionResult, Literal(str(eurovision_result))))

    graph.serialize(destination=output_path, format="turtle")
    print(f"TTL povoado criado em: {output_path}")


if __name__ == "__main__":
    main()
