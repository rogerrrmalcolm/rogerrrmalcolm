"""Generate the profile's monochrome typography and project illustrations."""

import argparse
from html import escape
from pathlib import Path
from xml.etree import ElementTree

PALETTES = {
    "light": {"bg": "#fafafa", "ink": "#131313", "muted": "#5a5a5a", "line": "#d7d7d7", "soft": "#eeeeee"},
    "dark": {"bg": "#111111", "ink": "#f1f1f1", "muted": "#a0a0a0", "line": "#373737", "soft": "#1c1c1c"},
}
FONT = "'Arial Black','Segoe UI',Arial,sans-serif"
MONO = "ui-monospace,Consolas,monospace"
PROJECTS = [
    {"slug": "physics", "number": "01", "title": "BLACK HOLE SIMULATION", "tech": "C++20 / PYTHON",
     "desktop": "Kerr geodesics, Penrose splits, scalar / AVX2 physics checks.",
     "mobile": ["Kerr geodesics and Penrose splits.", "Scalar / AVX2 physics checks."], "art": "orbit"},
    {"slug": "heart", "number": "02", "title": "HEART RATE MONITOR", "tech": "ESP32 / C++ / PYTHON",
     "desktop": "ESP32 sensing with live Python signal visualization over UART.",
     "mobile": ["ESP32 sensing with live Python", "signal visualization over UART."], "art": "heart"},
    {"slug": "bastion", "number": "03", "title": "BASTION", "tech": "PYTHON / LANGGRAPH / FASTAPI",
     "desktop": "Stateful research, PDF retrieval, and evidence-linked reports.",
     "mobile": ["Stateful research and PDF retrieval.", "Reports with traceable evidence."], "art": "nodes"},
]


def text(x, y, value, size, color, weight=400, mono=False, length=None, spacing=None):
    extra = f' textLength="{length}" lengthAdjust="spacingAndGlyphs"' if length else ""
    if spacing is not None:
        extra += f' letter-spacing="{spacing}"'
    font = MONO if mono else FONT if weight >= 700 else "'Segoe UI',Arial,sans-serif"
    return f'<text x="{x}" y="{y}" fill="{color}" font-family="{font}" font-size="{size}" font-weight="{weight}"{extra}>{escape(value)}</text>'


def wrap(title, description, width, height, c, content):
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-labelledby="title desc">
<title id="title">{escape(title)}</title>
<desc id="desc">{escape(description)}</desc>
<style>.still{{display:none}}@media(prefers-reduced-motion:reduce){{.motion{{display:none}}.still{{display:inline}}}}</style>
<rect x=".5" y=".5" width="{width-1}" height="{height-1}" fill="{c['bg']}" stroke="{c['line']}"/>
{content}
</svg>
'''
    ElementTree.fromstring(svg)
    return svg


def orbit(x, y, scale, c):
    return f'''<g transform="translate({x} {y}) scale({scale})" fill="none">
<circle r="100" stroke="{c['line']}" stroke-width=".8"/>
<circle r="83" stroke="{c['line']}" stroke-width=".8"/>
<ellipse rx="128" ry="40" transform="rotate(-23)" stroke="{c['ink']}" stroke-width="1.2"/>
<ellipse rx="115" ry="34" transform="rotate(-23)" stroke="{c['ink']}" stroke-width=".7" opacity=".5"/>
<circle r="58" fill="#050505" stroke="{c['ink']}" stroke-width="1.2"/>
<path d="M-115 49Q-8-48 116-49" stroke="{c['ink']}" stroke-width="2.5"/>
<path d="M-115 51Q-8-43 116-47" stroke="{c['bg']}" stroke-width="1"/>
<g class="motion"><circle r="100" stroke="{c['ink']}" stroke-width="1.4" stroke-dasharray="3 36"/>
<circle cx="100" r="4" fill="{c['ink']}"/><animateTransform attributeName="transform" type="rotate" from="0" to="360" dur="24s" repeatCount="indefinite"/></g>
<g class="still"><circle cx="100" r="4" fill="{c['ink']}"/></g>
</g>'''


def heart(x, y, scale, c):
    shape = "M-105 2H-68L-57-12-44 2H-27L-13-45 3 42 16-22 28 2H105"
    return f'''<g transform="translate({x} {y}) scale({scale})" fill="none">
<path d="M-111-47V47M-55-47V47M0-47V47M55-47V47M111-47V47M-111-40H111M-111 0H111M-111 40H111" stroke="{c['line']}" stroke-width=".8"/>
<path d="{shape}" stroke="{c['muted']}" stroke-width="2" stroke-linejoin="round"/>
<path class="motion" d="{shape}" stroke="{c['ink']}" stroke-width="3" stroke-linejoin="round" stroke-dasharray="75 360"><animate attributeName="stroke-dashoffset" from="435" to="0" dur="3.5s" repeatCount="indefinite"/></path>
</g>'''


def nodes(x, y, scale, c):
    points = [(-96, 18), (-48, -18), (0, 18), (48, -18), (96, 18)]
    polyline = " ".join(f"{a},{b}" for a, b in points)
    body = f'<polyline points="{polyline}" fill="none" stroke="{c["muted"]}" stroke-width="1.3"/>'
    for index, (a, b) in enumerate(points):
        body += f'<rect x="{a-10}" y="{b-10}" width="20" height="20" fill="{c["bg"]}" stroke="{c["ink"]}" stroke-width="1.2"/>'
        body += f'<circle class="motion" cx="{a}" cy="{b}" r="4" fill="{c["ink"]}"><animate attributeName="opacity" values=".1;1;.1" dur="4s" begin="{index*.6}s" repeatCount="indefinite"/></circle>'
    return f'<g transform="translate({x} {y}) scale({scale})">{body}</g>'


def hero(theme, mobile):
    c = PALETTES[theme]
    if mobile:
        width, height = 360, 242
        body = text(18, 23, "@ROGERRRMALCOLM", 10.5, c['muted'], mono=True, spacing=.7)
        body += orbit(309, 57, .28, c)
        body += text(18, 94, "ROGER", 64, c['ink'], 900)
        body += text(18, 157, "MALCOLM", 54, c['ink'], 900)
        body += f'<path d="M18 187H342" stroke="{c["ink"]}" stroke-width="1.4"/>'
        body += text(18, 217, "COMPUTER ENGINEERING / TMU", 11.5, c['muted'], mono=True)
    else:
        width, height = 1000, 270
        body = text(34, 28, "COMPUTER ENGINEERING / TMU", 12, c['muted'], mono=True, spacing=1.2)
        body += text(30, 120, "ROGER", 107, c['ink'], 900)
        body += text(27, 213, "MALCOLM", 105, c['ink'], 900)
        body += text(34, 248, "@rogerrrmalcolm", 12, c['muted'], mono=True)
        body += orbit(826, 135, .9, c)
        body += f'<path d="M684 25h20M694 15v20M948 236h20M958 226v20" stroke="{c["muted"]}"/>'
    return wrap("Roger Malcolm", "Computer Engineering at Toronto Metropolitan University. A monochrome orbital illustration accompanies the name.", width, height, c, body)


def project_card(project, theme, mobile):
    # The last panel reverses the paper and ink for a deliberate visual break.
    c = PALETTES[('dark' if theme == 'light' else 'light') if project['slug'] == 'bastion' else theme]
    width, height = (360, 158) if mobile else (1000, 144)
    x = 18 if mobile else 32
    body = text(x, 28, f"{project['number']} / {project['tech']}", 10.5 if mobile else 11.5, c['muted'], mono=True)
    title_size = (21.5 if project['slug'] == 'physics' else 25 if project['slug'] == 'heart' else 30) if mobile else 33
    body += text(x, 78 if mobile else 77, project['title'], title_size, c['ink'], 800)
    if mobile:
        for index, line in enumerate(project['mobile']):
            body += text(x, 108 + index * 22, line, 14, c['muted'])
        art_x, art_y, scale = 321, 24, .16
    else:
        body += text(x, 114, project['desktop'], 15, c['muted'])
        art_x, art_y, scale = 852, 77, .62
        body += text(958, 28, "↗", 18, c['ink'])
    body += {"orbit": orbit, "heart": heart, "nodes": nodes}[project['art']](art_x, art_y, scale, c)
    return wrap(project['title'], project['desktop'] + " Open the project repository.", width, height, c, body)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, default=Path('dist'))
    args = parser.parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    count = 0
    for theme in PALETTES:
        for mobile in [False, True]:
            suffix = theme + ('-mobile' if mobile else '')
            (args.out / f'profile-hero-{suffix}.svg').write_text(hero(theme, mobile), encoding='utf-8')
            count += 1
            for project in PROJECTS:
                (args.out / f'project-{project["slug"]}-{suffix}.svg').write_text(project_card(project, theme, mobile), encoding='utf-8')
                count += 1
    print(f'Generated {count} monochrome profile assets.')


if __name__ == '__main__':
    main()
