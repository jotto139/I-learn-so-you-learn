"""Build the notes website: python build.py."""
from pathlib import Path
import html
import json
import re
import shutil
import markdown

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
esc = html.escape


def read_note(path):
    text = path.read_text(encoding='utf-8')
    meta = {}
    if text.startswith('---\n'):
        _, header, text = text.split('---', 2)
        for line in header.strip().splitlines():
            key, value = line.split(':', 1)
            meta[key.strip()] = value.strip()
    meta.setdefault('title', path.stem)
    meta.setdefault('description', '')
    meta.setdefault('status', 'In progress')
    return meta, text


def page(title, content, prefix='./', crumbs='', sidebar='', description='A growing collection of study notes and explanations.'):
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)} · Study Notes</title><meta name="description" content="{esc(description, quote=True)}">
<link rel="icon" href="{prefix}favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="{prefix}style.css">
<script>window.MathJax={{tex:{{inlineMath:[['$', '$'],['\\\\(', '\\\\)']]}}}};</script>
<script defer src="https://cdn.jsdelivr.net/npm/mathjax@3.2.2/es5/tex-mml-chtml.js"></script>
</head><body><a class="skip" href="#main">Skip to content</a>
<header><a class="brand" href="{prefix}index.html"><span class="mark">N</span> Study Notes</a><a class="library-link" href="{prefix}index.html">Course library</a></header>
<div class="shell">{crumbs}<div class="{'reading-layout' if sidebar else ''}"><main id="main">{content}</main>{sidebar}</div></div>
<footer><span>Study Notes</span><span>A little clearer, one concept at a time.</span></footer></body></html>'''


def write(path, content):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding='utf-8')


def build():
    OUT.mkdir(exist_ok=True)
    # Clear generated HTML only, so deleted notes do not remain published.
    for old in OUT.rglob('*.html'):
        old.unlink()
    courses = []
    for folder in sorted((ROOT / 'courses').iterdir()):
        if not folder.is_dir() or not (folder / 'course.json').exists():
            continue
        if not re.fullmatch(r'[a-z0-9-]+', folder.name):
            raise ValueError('Use lowercase letters, numbers, and hyphens for course folders.')
        course = json.loads((folder / 'course.json').read_text(encoding='utf-8'))
        notes = []
        for path in sorted(folder.glob('*.md')):
            if not re.fullmatch(r'[a-z0-9-]+', path.stem):
                raise ValueError('Use lowercase letters, numbers, and hyphens for note filenames.')
            meta, body = read_note(path)
            notes.append((path.stem, meta, body))
        courses.append((folder.name, course, notes))
        dest = OUT / 'courses' / folder.name
        assets = folder / 'images'
        if assets.exists():
            shutil.copytree(assets, dest / 'images', dirs_exist_ok=True)
        rows = ''.join(f'<a class="topic-row" href="{slug}.html"><span class="number">{i:02d}</span><span><h2>{esc(meta["title"])}</h2><p>{esc(meta["description"])}</p></span><span class="status">{esc(meta["status"])}</span></a>' for i, (slug, meta, _) in enumerate(notes, 1))
        intro = f'<p class="eyebrow">COURSE NOTES / {esc(course.get("label", "Study"))}</p><h1>{esc(course["title"])}</h1><p class="intro">{esc(course["description"])}</p><div class="section-label"><h2>Topics</h2><span>{len(notes)} {"note" if len(notes) == 1 else "notes"}</span></div><div class="topic-list">{rows or "<p>No notes yet.</p>"}</div>'
        crumbs = '<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../../index.html">All courses</a><span>/</span><span>Course overview</span></nav>'
        write(dest / 'index.html', page(course['title'], intro, '../../', crumbs, description=course['description']))
        for i, (slug, meta, body) in enumerate(notes):
            md = markdown.Markdown(extensions=['extra', 'toc', 'sane_lists'], extension_configs={'toc': {'permalink': False}})
            rendered = md.convert(body)
            content = f'<p class="eyebrow">{esc(course["title"])}</p><h1>{esc(meta["title"])}</h1><p class="intro">{esc(meta["description"])}</p><div class="note-meta"><span class="status">{esc(meta["status"])}</span><a href="{slug}.md" download>Download note</a></div><article>{rendered}</article>'
            adjacent = []
            if i > 0:
                adjacent.append(f'<a href="{notes[i-1][0]}.html">Previous: {esc(notes[i-1][1]["title"])}</a>')
            if i+1 < len(notes):
                adjacent.append(f'<a href="{notes[i+1][0]}.html">Next: {esc(notes[i+1][1]["title"])}</a>')
            content += '<nav class="adjacent" aria-label="Other notes">' + ''.join(adjacent) + '</nav>'
            side = f'<aside><p class="eyebrow">IN THIS NOTE</p>{md.toc}<a class="back-course" href="index.html">All course topics</a></aside>'
            crumbs = f'<nav class="breadcrumbs" aria-label="Breadcrumb"><a href="../../index.html">All courses</a><span>/</span><a href="index.html">{esc(course["title"])}</a><span>/</span><span>Note {i+1:02d}</span></nav>'
            write(dest / f'{slug}.html', page(meta['title'], content, '../../', crumbs, side, meta['description']))
            shutil.copyfile(folder / f'{slug}.md', dest / f'{slug}.md')
    cards = ''.join(f'<a class="course-card" href="courses/{slug}/index.html"><div class="card-top"><span class="eyebrow">{esc(course.get("label", "Course"))}</span><span class="course-index">{i:02d}</span></div><h2>{esc(course["title"])}</h2><p>{esc(course["description"])}</p><div class="card-bottom"><span>{len(notes)} {"note" if len(notes) == 1 else "notes"}</span><span class="open-course">Open course</span></div></a>' for i, (slug, course, notes) in enumerate(courses, 1))
    home = f'<div class="home-intro"><p class="eyebrow">THE NOTEBOOK</p><h1>Learning, in<br>my own words.</h1><p class="intro">A growing collection of explanations, connections, and worked examples. Written to understand. Kept to return to.</p></div><div class="section-label"><h2>Course library</h2><span>{len(courses):02d} {"course" if len(courses) == 1 else "courses"}</span></div><div class="course-grid">{cards}</div>'
    write(OUT / 'index.html', page('Course library', home))
    for name in ['style.css', 'favicon.svg']:
        shutil.copyfile(ROOT / 'assets' / name, OUT / name)
    write(OUT / '.nojekyll', '')
    print(f'Built {len(courses)} course(s), {sum(len(c[2]) for c in courses)} note(s) in {OUT}')


if __name__ == '__main__':
    build()
