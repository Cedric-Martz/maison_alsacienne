from __future__ import annotations

import argparse
import html
import json
import re
import shutil
from collections import Counter
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
PUBLIC_DIRECTORIES = ("assets", "de", "en", "es")
PUBLIC_FILES = (
    ".nojekyll",
    "404.html",
    "CNAME",
    "favicon.ico",
    "robots.txt",
    "site.webmanifest",
    "sitemap.xml",
)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def escape(value: object) -> str:
    return html.escape(str(value or ""), quote=True)


def load_json(path: Path, expected: type) -> object:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise RuntimeError(f"Contenu invalide dans {path.relative_to(ROOT)} : {error}") from error
    if not isinstance(value, expected):
        raise TypeError(f"{path.relative_to(ROOT)} doit contenir un {expected.__name__}")
    return value


def required(data: dict, key: str) -> str:
    value = str(data.get(key, "")).strip()
    if not value:
        raise RuntimeError(f"Champ obligatoire absent : {key}")
    return value


def safe_url(value: object) -> str:
    url = str(value or "").strip()
    if not url:
        return ""
    parsed = urlsplit(url)
    if parsed.scheme and parsed.scheme not in {"http", "https", "mailto", "tel"}:
        raise RuntimeError(f"Adresse interdite dans le contenu : {url}")
    if not parsed.scheme and not re.fullmatch(r"[A-Za-z0-9_./#?=&%+~-]+", url):
        raise RuntimeError(f"Adresse relative invalide dans le contenu : {url}")
    return url


def lines(value: str) -> str:
    return "<br>".join(escape(line) for line in value.splitlines() if line.strip())


def price(value: str) -> str:
    match = re.match(r"^(.+?€)(?:\s+|$)(.*)$", value)
    if not match:
        return escape(value)
    suffix = f" {escape(match.group(2))}" if match.group(2) else ""
    return f"<strong>{escape(match.group(1))}</strong>{suffix}"


def replace_once(path: Path, pattern: str, replacement: str) -> None:
    source = path.read_text(encoding="utf-8")
    updated, count = re.subn(pattern, lambda _match: replacement, source, count=1, flags=re.DOTALL)
    if count != 1:
        raise RuntimeError(f"Zone de génération introuvable dans {path.name} : {pattern[:60]}")
    path.write_text(updated, encoding="utf-8")


def copy_public(output: Path) -> None:
    if output.exists():
        shutil.rmtree(output)
    output.mkdir(parents=True)
    for source in ROOT.glob("*.html"):
        shutil.copy2(source, output / source.name)
    for name in PUBLIC_FILES:
        source = ROOT / name
        if source.exists():
            shutil.copy2(source, output / name)
    for name in PUBLIC_DIRECTORIES:
        shutil.copytree(ROOT / name, output / name)


def render_information(output: Path, info: dict) -> None:
    presentation = required(info, "presentation")
    season = required(info, "saison")
    weekdays = required(info, "horaires_semaine")
    sunday = required(info, "horaires_dimanche")
    schedule_note = required(info, "note_horaires")
    individual = required(info, "tarif_individuel")
    group = required(info, "tarif_groupe")
    school = required(info, "tarif_scolaire")
    free = required(info, "gratuite")
    phone = required(info, "telephone_affiche")
    phone_link = re.sub(r"[^+0-9]", "", required(info, "telephone_lien"))
    email = required(info, "email")
    postal = required(info, "adresse_courrier")
    park = required(info, "adresse_parc")
    route = safe_url(required(info, "itineraire"))
    instagram_url = safe_url(info.get("instagram_url"))
    instagram_name = str(info.get("instagram_nom", "")).strip()

    index = output / "index.html"
    source = index.read_text(encoding="utf-8")
    source, count = re.subn(
        r'(<h1 id="hero-title">.*?</h1>\s*<p>).*?(</p>)',
        lambda match: match.group(1) + escape(presentation) + match.group(2),
        source,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise RuntimeError("Présentation de l’accueil introuvable")
    index.write_text(source, encoding="utf-8")

    quick = f'''<section class="quick" aria-label="Informations essentielles">
      <div class="wrap quick-grid">
        <div><span class="icon papicon papicon-clock" aria-hidden="true"></span><p><small>{escape(season)}</small><strong>{escape(weekdays)}</strong><span>{escape(sunday)}</span></p></div>
        <div><span class="icon papicon papicon-card" aria-hidden="true"></span><p><small>Entrée individuelle</small><strong>{escape(individual.split(" par ", 1)[0])}</strong><span>{escape(free)}</span></p></div>
        <div><span class="icon papicon papicon-map-pin" aria-hidden="true"></span><p><small>À 10 km de Strasbourg</small><strong>{escape(park.replace(chr(10), ", "))}</strong><a href="{escape(route)}" rel="noopener">Voir l’itinéraire →</a></p></div>
      </div>
    </section>'''
    replace_once(index, r'<section class="quick".*?</section>', quick)

    visit_home = f'''<section class="visit section" id="visiter">
      <div class="wrap"><p class="eyebrow">Préparer votre venue</p><div class="section-head"><h2>Une visite simple,<br>à votre rythme.</h2><p>Avec ou sans visite guidée. Les groupes et les classes sont accueillis sur rendez-vous.</p></div>
        <div class="cards">
          <article><span>01</span><h3>Horaires</h3><p>{escape(season)} :</p><ul><li>{escape(weekdays)}</li><li>{escape(sunday)}</li><li>{escape(schedule_note)}</li></ul></article>
          <article><span>02</span><h3>Tarifs</h3><ul><li>{price(individual)}</li><li>{price(group)}</li><li>{price(school)}</li></ul></article>
          <article><span>03</span><h3>Visites scolaires</h3><p>Rallye découverte, habitat rural, œufs colorés naturellement : des activités concrètes adaptées aux enfants.</p><a href="mailto:{escape(email)}?subject=Visite%20scolaire">Organiser une visite →</a></article>
        </div>
      </div>
    </section>'''
    replace_once(index, r'<section class="visit section" id="visiter">.*?</section>', visit_home)

    visit = output / "visite.html"
    practical = f'''<section class="editorial wrap" id="horaires"><div><p class="eyebrow red">Informations pratiques</p><h2>Bienvenue au cœur de l’Alsace.</h2><p class="lead">Le parc se visite librement ou avec un guide. Les groupes et les classes sont accueillis sur rendez-vous.</p></div><div class="info-panels"><article><h3>Horaires d’ouverture</h3><p><strong>{escape(season)}</strong><br>{escape(weekdays)}<br>{escape(sunday)}<br>{escape(schedule_note)}</p></article><article><h3>Tarifs</h3><p>{price(individual)}<br>{price(group)}<br>{price(school)}<br>{escape(free)}</p></article></div></section>'''
    replace_once(visit, r'<section class="editorial wrap" id="horaires">.*?</section>', practical)
    access = f'''<section class="editorial wrap" id="acces"><div><p class="eyebrow red">Venir au parc</p><h2>Au centre de Reichstett</h2><p>Le parc se trouve rue du Terrain, dans le prolongement du parc à cigognes, à environ 10 km au nord de Strasbourg.</p><div class="actions dark-actions"><a class="button primary" href="{escape(route)}" rel="noopener">Ouvrir l’itinéraire</a><a class="button outline-dark" href="contact.html">Nous contacter</a></div></div><a class="map-card" href="{escape(route)}" rel="noopener"><span class="papicon papicon-map-pin" aria-hidden="true"></span><strong>Parc de la Maison Alsacienne</strong><small>{lines(park)}</small><b>Afficher sur OpenStreetMap →</b></a></section>'''
    replace_once(visit, r'<section class="editorial wrap" id="acces">.*?</section>', access)

    contact = output / "contact.html"
    instagram = ""
    if instagram_url and instagram_name:
        instagram = f'<a href="{escape(instagram_url)}" rel="noopener"><small>Instagram</small><strong>{escape(instagram_name)}</strong></a>'
    contact_section = f'''<section class="editorial wrap"><div><p class="eyebrow red">Nous écrire</p><h2>À bientôt au parc.</h2><p class="lead">Pour une visite de groupe, une activité scolaire, un chantier ou une publication, contactez directement l’association.</p></div><div class="contact-sheet"><a href="tel:{escape(phone_link)}"><small>Téléphone</small><strong>{escape(phone)}</strong></a><a href="mailto:{escape(email)}"><small>E-mail</small><strong>{escape(email)}</strong></a><div><small>Courrier</small><strong>{lines(postal)}</strong></div><div><small>Adresse du parc</small><strong>{lines(park)}</strong></div>{instagram}</div></section>'''
    replace_once(contact, r'<section class="editorial wrap">.*?</section>', contact_section)

    programme = output / "programme.html"
    notice = f'''<aside class="notice wrap"><strong>Avant de vous déplacer</strong><p>Le programme peut évoluer. Confirmez une date au <a href="tel:{escape(phone_link)}">{escape(phone)}</a> ou par <a href="mailto:{escape(email)}">e-mail</a>.</p></aside>'''
    replace_once(programme, r'<aside class="notice wrap">.*?</aside>', notice)

    for page in output.rglob("*.html"):
        source = page.read_text(encoding="utf-8")
        source = source.replace("livia.kuhn-poteur@orange.fr", escape(email))
        source = source.replace("+33388205990", escape(phone_link))
        source = source.replace("03 88 20 59 90", escape(phone))
        page.write_text(source, encoding="utf-8")


def render_events(output: Path) -> None:
    events = []
    for path in (ROOT / "content" / "evenements").glob("*.json"):
        event = load_json(path, dict)
        event_date = required(event, "date")
        if not DATE_RE.fullmatch(event_date):
            raise RuntimeError(f"Date invalide dans {path.relative_to(ROOT)}")
        events.append(event)
    events.sort(key=lambda event: (event["date"], event["title"]))
    if not events:
        raise RuntimeError("Le programme doit contenir au moins un événement")
    articles = []
    for event in events:
        link = safe_url(event.get("lien"))
        link_html = ""
        if link:
            label = str(event.get("libelle_lien") or "En savoir plus")
            link_html = f'<a href="{escape(link)}">{escape(label)} →</a>'
        articles.append(
            f'<article><time datetime="{escape(event["date"])}">{escape(required(event, "date_affichee"))}</time><div><h2>{escape(required(event, "title"))}</h2><p>{escape(required(event, "resume"))}</p>{link_html}</div></article>'
        )
    timeline = '<section class="timeline wrap" id="calendrier">' + "".join(articles) + "</section>"
    programme = output / "programme.html"
    replace_once(programme, r'<section class="timeline wrap" id="calendrier">.*?</section>', timeline)

    years = sorted({event["date"][:4] for event in events})
    programme_title = f"Programme {years[0]}" if len(years) == 1 else "Programme"
    source = programme.read_text(encoding="utf-8")
    source = re.sub(r'<title>Programme(?: \d{4})? \|', f'<title>{programme_title} |', source, count=1)
    source = re.sub(r'<h1>Programme(?: \d{4})?</h1>', f'<h1>{programme_title}</h1>', source, count=1)
    source = re.sub(r'>Calendrier(?: \d{4})?</a>', f'>Calendrier {years[0] if len(years) == 1 else ""}</a>', source, count=1)
    programme.write_text(source, encoding="utf-8")

    today = date.today().isoformat()
    featured = [event for event in events if event["date"] >= today][:2]
    if not featured:
        featured = events[-2:]
    months = ("janv.", "févr.", "mars", "avr.", "mai", "juin", "juil.", "août", "sept.", "oct.", "nov.", "déc.")
    home_events = []
    for index, event in enumerate(featured):
        _year, month, day = (int(part) for part in event["date"].split("-"))
        link = safe_url(event.get("lien"))
        arrow = f'<a href="{escape(link)}" aria-label="{escape(event["title"])}">→</a>' if link else ""
        css = "event feature" if index == 0 else "event"
        home_events.append(
            f'<div class="{css}"><time datetime="{escape(event["date"])}"><b>{day:02d}</b><span>{months[month - 1]}</span></time><div><p class="tag">{escape(required(event, "date_affichee"))}</p><h3>{escape(required(event, "title"))}</h3><p>{escape(required(event, "resume"))}</p></div>{arrow}</div>'
        )
    agenda = f'''<section class="agenda section wrap" id="agenda"><div class="section-head"><div><p class="eyebrow red">À noter</p><h2>La vie du parc</h2></div><p>Le programme est mis à jour par l’association. Contactez-nous pour confirmer une date avant votre venue.</p></div>{"".join(home_events)}</section>'''
    replace_once(output / "index.html", r'<section class="agenda section wrap" id="agenda">.*?</section>', agenda)


def render_news(output: Path) -> None:
    news = []
    for path in (ROOT / "content" / "actualites").glob("*.json"):
        item = load_json(path, dict)
        date = required(item, "date")
        if not DATE_RE.fullmatch(date):
            raise RuntimeError(f"Date invalide dans {path.relative_to(ROOT)}")
        news.append(item)
    news.sort(key=lambda item: (item["date"], item["title"]), reverse=True)
    if not news:
        raise RuntimeError("La page Actualités doit contenir au moins une actualité")
    cards = []
    for index, item in enumerate(news):
        image = safe_url(required(item, "image"))
        link = safe_url(item.get("lien"))
        link_html = ""
        if link:
            label = str(item.get("libelle_lien") or "En savoir plus")
            link_html = f'<a class="text-link" href="{escape(link)}">{escape(label)} <span>→</span></a>'
        reverse = " reverse" if index % 2 else ""
        cards.append(
            f'<section class="split-feature{reverse}"><img src="{escape(image)}" alt="{escape(required(item, "image_alt"))}" loading="lazy"><div><p class="eyebrow red">{escape(required(item, "categorie"))}</p><h2>{escape(required(item, "title"))}</h2><p>{escape(required(item, "resume"))}</p>{link_html}</div></section>'
        )
    replacement = '<div class="page-content cms-news">' + "".join(cards) + "</div></main><footer>"
    replace_once(output / "actualites.html", r'<div class="page-content">.*</div></main><footer>', replacement)


def render_gallery(output: Path) -> None:
    gallery = load_json(ROOT / "content" / "galerie.json", list)
    if not gallery:
        raise RuntimeError("La galerie doit contenir au moins une photo")
    cards = []
    years = Counter()
    for item in gallery:
        if not isinstance(item, dict):
            raise TypeError("Chaque photo de la galerie doit être un objet")
        image = safe_url(required(item, "image"))
        caption = required(item, "legende")
        year = required(item, "annee")
        if not re.fullmatch(r"\d{4}", year):
            raise RuntimeError(f"Année invalide pour {caption}")
        years[year] += 1
        image_path = Path(urlsplit(image).path)
        thumbnail = image
        if image_path.parent.name == "media":
            candidate = ROOT / "assets" / "thumbs" / f"{image_path.stem}.webp"
            if candidate.exists():
                thumbnail = f"/assets/thumbs/{candidate.name}"
        cards.append(
            f'<figure class="archive-card" data-year="{escape(year)}"><a aria-label="Agrandir : {escape(caption)}" class="archive-link" data-lightbox href="{escape(image)}"><img alt="{escape(caption)}" decoding="async" loading="lazy" src="{escape(thumbnail)}"><span aria-hidden="true" class="zoom">↗</span></a><figcaption>{escape(caption)}<small>Archive {escape(year)}</small></figcaption></figure>'
        )
    page = output / "galerie.html"
    source = page.read_text(encoding="utf-8")
    source = re.sub(r'<strong>\d+<small>photographies</small></strong>', f'<strong>{len(gallery)}<small>photographies</small></strong>', source, count=1)
    filters = [f'<button class="active" data-filter="all">Toutes <span>{len(gallery)}</span></button>']
    for year in sorted(years, reverse=True):
        filters.append(f'<button data-filter="{year}">{year} <span>{years[year]}</span></button>')
    source, filter_count = re.subn(r'<div aria-label="Filtrer par année" class="filters">.*?</div>', '<div aria-label="Filtrer par année" class="filters">' + "".join(filters) + "</div>", source, count=1, flags=re.DOTALL)
    source, grid_count = re.subn(r'<div class="archive-grid">.*?</div>', '<div class="archive-grid">' + "".join(cards) + "</div>", source, count=1, flags=re.DOTALL)
    if filter_count != 1 or grid_count != 1:
        raise RuntimeError("Structure de la galerie introuvable")
    page.write_text(source, encoding="utf-8")


def verify(output: Path) -> None:
    errors = []
    for page in output.rglob("*.html"):
        source = page.read_text(encoding="utf-8")
        for url in re.findall(r'(?:href|src)=["\']([^"\']+)', source, re.IGNORECASE):
            if url.startswith(("http://", "https://", "mailto:", "tel:", "#", "data:")):
                continue
            path = urlsplit(url).path
            target = output / path.lstrip("/") if path.startswith("/") else page.parent / path
            if target.is_dir():
                target = target / "index.html"
            if path and not target.exists():
                errors.append(f"{page.relative_to(output)} → {url}")
    if errors:
        raise RuntimeError("Références absentes :\n" + "\n".join(errors[:30]))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=ROOT / "_site")
    args = parser.parse_args()
    output = args.output.resolve()
    if output == ROOT or ROOT not in output.parents:
        parser.error("Le dossier de sortie doit rester dans le dépôt")
    copy_public(output)
    info = load_json(ROOT / "content" / "informations.json", dict)
    render_information(output, info)
    render_events(output)
    render_news(output)
    render_gallery(output)
    verify(output)
    files = sum(path.is_file() for path in output.rglob("*"))
    print(f"Site généré : {files} fichiers dans {output.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
