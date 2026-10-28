"""Build the project case-study pages from _build/projects/*.json.

Usage (from the repo root):  python3 _build/build_projects.py

Writes projects/index.html and projects/<slug>.html. GitHub Pages runs Jekyll,
which skips folders starting with "_", so nothing in _build/ is published.
"""
import json
import pathlib
import sys
from html import escape

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / "_build" / "projects"
OUT = ROOT / "projects"

THEMES = [
    ("freight", "Freight & Logistics AI", "Agents and services for a freight brokerage's back office: verification, calls, email and carrier vetting."),
    ("platforms", "Platforms & Products", "Full-stack products with real users, queues, mobile apps and integrations."),
    ("ml", "Applied ML & AI Infrastructure", "Serving models in production: speech, vision, retrieval, and privacy tooling."),
]
THEME_NAME = {k: n for k, n, _ in THEMES}

MERMAID_INIT = """
  import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@10.9.1/dist/mermaid.esm.min.mjs";
  mermaid.initialize({
    startOnLoad: true,
    securityLevel: "strict",
    theme: "base",
    flowchart: { curve: "basis", htmlLabels: true },
    themeVariables: {
      fontFamily: "Schibsted Grotesk, Helvetica Neue, Arial, sans-serif",
      fontSize: "15px",
      background: "#faedda",
      primaryColor: "#fffdf9",
      primaryBorderColor: "#1c1a17",
      primaryTextColor: "#1c1a17",
      lineColor: "#a51c30",
      secondaryColor: "#faedda",
      tertiaryColor: "#fffbf4",
      clusterBkg: "#fffbf4",
      clusterBorder: "#b9b8ad",
      edgeLabelBackground: "#faedda"
    }
  });
"""


def rich(s):
    """Escape text but keep the <b> tags the content files are allowed to use."""
    return escape(s).replace("&lt;b&gt;", "<b>").replace("&lt;/b&gt;", "</b>")


def head(title, desc, canonical, depth):
    up = "../" * depth
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{escape(title)}</title>
  <meta name="description" content="{escape(desc)}">
  <meta name="author" content="Kartikey Shaurya">
  <link rel="canonical" href="https://kartikeyshaurya.github.io/{canonical}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{escape(title)}">
  <meta property="og:description" content="{escape(desc)}">
  <meta property="og:url" content="https://kartikeyshaurya.github.io/{canonical}">
  <meta name="twitter:card" content="summary">
  <link rel="icon" href="{up}assets/favicon.svg" type="image/svg+xml">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Newsreader:ital,opsz,wght@0,6..72,400;0,6..72,500;0,6..72,600;1,6..72,400;1,6..72,500&family=Schibsted+Grotesk:ital,wght@0,400;0,500;0,700;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{up}assets/css/site.css">
</head>
<body>
<a class="skip" href="#main">Skip to content</a>
"""


def header(depth, active=""):
    up = "../" * depth
    home = f"{up}index.html"
    items = [
        (home, "Front page", ""),
        (f"{up}projects/index.html", "Projects", "projects"),
        (f"{home}#experience", "Experience", ""),
        (f"{home}#about", "About", ""),
    ]
    current = ' class="is-active" aria-current="page"'
    nav = "\n".join(
        f'      <li><a href="{h}"{current if k and k == active else ""}>{t}</a></li>'
        for h, t, k in items
    )
    return f"""<header>
  <div class="wrap util">
    <ul>
      <li>Chandigarh, India</li>
    </ul>
    <ul>
      <li><a href="mailto:kartikeyshaurya@gmail.com">Email</a></li>
      <li><a href="https://github.com/kartikeyshaurya" target="_blank" rel="noopener">GitHub</a></li>
      <li><a href="https://www.linkedin.com/in/kartikey-shaurya-3bb776109/" target="_blank" rel="noopener">LinkedIn</a></li>
      <li><a class="pdf" href="{up}Kartikey_Shaurya_ML_Engineer.pdf" target="_blank" rel="noopener">Résumé, PDF</a></li>
    </ul>
  </div>

  <div class="wrap masthead masthead--slim">
    <a class="logo" href="{home}">Kartikey Shaurya</a>
    <p class="tag"><b>Machine Learning Engineer.</b> Production AI, reported from the inside.</p>
  </div>

  <nav class="primary" aria-label="Sections">
    <ul>
{nav}
      <li><a class="cta" href="{home}#hire">Hire me</a></li>
    </ul>
  </nav>
</header>
"""


def footer(depth):
    up = "../" * depth
    return f"""<footer class="foot">
  <div class="wrap">
    <div>
      <p class="logo">Kartikey Shaurya</p>
      <a class="email" href="mailto:kartikeyshaurya@gmail.com">kartikeyshaurya@gmail.com</a>
    </div>
    <div>
      <h4>Sections</h4>
      <ul>
        <li><a href="{up}index.html">Front page</a></li>
        <li><a href="{up}projects/index.html">All projects</a></li>
        <li><a href="{up}index.html#experience">Experience</a></li>
      </ul>
    </div>
    <div>
      <h4>Elsewhere</h4>
      <ul>
        <li><a href="https://github.com/kartikeyshaurya" target="_blank" rel="noopener">GitHub</a></li>
        <li><a href="https://www.linkedin.com/in/kartikey-shaurya-3bb776109/" target="_blank" rel="noopener">LinkedIn</a></li>
        <li><a href="{up}Kartikey_Shaurya_ML_Engineer.pdf" target="_blank" rel="noopener">Résumé, PDF</a></li>
      </ul>
    </div>
    <p class="fine">
      <span>© 2026 Kartikey Shaurya</span>
      <span>Most client names and internal details are withheld. Architecture is shown at the component level.</span>
    </p>
  </div>
</footer>
"""


def paras(items):
    return "\n".join(f"<p>{rich(p)}</p>" for p in items)


def project_page(p, prev, nxt):
    a = p["architecture"]
    comps = "\n".join(
        f"<div><dt>{escape(c['name'])}</dt><dd>{rich(c['desc'])}</dd></div>" for c in a["components"]
    )
    built = "\n".join(f"<li>{rich(b)}</li>" for b in p["built"])
    steps = "\n".join(f"<li>{rich(s)}</li>" for s in p["flow"]["steps"])
    decisions = "\n".join(
        f"""<article class="decision">
  <h3>{rich(d['decision'])}</h3>
  <dl>
    <dt>Why</dt><dd>{rich(d['why'])}</dd>
    <dt>Instead of</dt><dd>{rich(d['alternative'])}</dd>
    <dt>The cost</dt><dd>{rich(d['tradeoff'])}</dd>
  </dl>
</article>"""
        for d in p["decisions"]
    )
    challenges = "\n".join(
        f"<li><h3>{rich(c['title'])}</h3><p>{rich(c['body'])}</p></li>" for c in p["challenges"]
    )
    nexts = "\n".join(f"<li>{rich(n)}</li>" for n in p["next"])
    stack = ", ".join(escape(s) for s in p["stack"])

    pager = []
    if prev:
        pager.append(f'<a class="prev" href="{prev["slug"]}.html"><span>Previous</span>{escape(prev["headline"])}</a>')
    if nxt:
        pager.append(f'<a class="next" href="{nxt["slug"]}.html"><span>Next</span>{escape(nxt["headline"])}</a>')

    return (
        head(f"{p['title']}: {p['headline']} | Kartikey Shaurya", p["dek"], f"projects/{p['slug']}.html", 1)
        + header(1, "projects")
        + f"""
<main id="main" class="case">
  <section class="wrap case-head">
    <p class="kicker"><a href="index.html">Projects</a> <span class="fmt">{escape(THEME_NAME[p['theme']])}</span></p>
    <h1>{escape(p['headline'])}</h1>
    <p class="dek">{rich(p['dek'])}</p>
    <p class="byline">By <b>Kartikey Shaurya</b> · {escape(p['title'])} · {escape(p['client'])}</p>
  </section>

  <div class="wrap case-grid">
    <div class="case-body">

      <section aria-labelledby="problem-h">
        <h2 id="problem-h">The problem</h2>
        <div class="prose">{paras(p['problem'])}</div>
      </section>

      <section aria-labelledby="approach-h">
        <h2 id="approach-h">How I thought about it</h2>
        <div class="prose prose--lead">{paras(p['approach'])}</div>
      </section>

      <section aria-labelledby="built-h">
        <h2 id="built-h">What I built</h2>
        <ul class="ticks">{built}</ul>
      </section>

      <section aria-labelledby="arch-h">
        <h2 id="arch-h">How it fits together</h2>
        <figure class="diagram">
          <pre class="mermaid">{escape(a['mermaid'])}</pre>
          <figcaption>{rich(a['caption'])}</figcaption>
        </figure>
        <dl class="components">{comps}</dl>
      </section>

      <section aria-labelledby="flow-h">
        <h2 id="flow-h">{escape(p['flow']['title'])}</h2>
        <ol class="steps">{steps}</ol>
      </section>

      <section aria-labelledby="dec-h">
        <h2 id="dec-h">Decisions and trade-offs</h2>
        <div class="decisions">{decisions}</div>
      </section>

      <section aria-labelledby="hard-h">
        <h2 id="hard-h">The hard parts</h2>
        <ul class="hard">{challenges}</ul>
      </section>

      <section aria-labelledby="next-h">
        <h2 id="next-h">What I'd do next</h2>
        <ul class="ticks ticks--plain">{nexts}</ul>
      </section>

      <blockquote class="takeaway">
        <p class="kicker">What I took away</p>
        <p>{rich(p['lesson'])}</p>
      </blockquote>
    </div>

    <aside class="case-side">
      <dl class="facts">
        <dt>Role</dt><dd>{escape(p['role'])}</dd>
        <dt>Context</dt><dd>{escape(p['client'])}</dd>
        <dt>Status</dt><dd>{escape(p['status'])}</dd>
        <dt>Stack</dt><dd>{stack}</dd>
      </dl>
      <nav class="toc" aria-label="On this page">
        <p class="kicker">On this page</p>
        <ul>
          <li><a href="#problem-h">The problem</a></li>
          <li><a href="#approach-h">How I thought about it</a></li>
          <li><a href="#built-h">What I built</a></li>
          <li><a href="#arch-h">Architecture</a></li>
          <li><a href="#flow-h">Key flow</a></li>
          <li><a href="#dec-h">Decisions</a></li>
          <li><a href="#hard-h">Hard parts</a></li>
        </ul>
      </nav>
    </aside>
  </div>

  <nav class="wrap pager" aria-label="More projects">
    {''.join(pager)}
  </nav>
</main>
"""
        + footer(1)
        + f'<script type="module">{MERMAID_INIT}</script>\n</body>\n</html>\n'
    )


def index_page(by_theme):
    cols = []
    for key, name, blurb in THEMES:
        items = "\n".join(
            f"""<li>
  <p class="kicker">{escape(p['title'])}</p>
  <h4><a href="{p['slug']}.html">{escape(p['headline'])}</a></h4>
  <p>{escape(p['summary'])}</p>
</li>"""
            for p in by_theme.get(key, [])
        )
        cols.append(f"""<div class="col" id="{key}">
  <h3>{escape(name)}</h3>
  <p class="col-blurb">{escape(blurb)}</p>
  <ul>{items}</ul>
</div>""")

    return (
        head(
            "Projects: how I build systems | Kartikey Shaurya",
            "Case studies of production AI systems: what I built, how I thought about it, and the trade-offs I made.",
            "projects/",
            1,
        )
        + header(1, "projects")
        + f"""
<main id="main">
  <section class="wrap case-head case-head--index">
    <p class="kicker">Projects <span class="fmt">Case studies</span></p>
    <h1>How I build systems, one decision at a time</h1>
    <p class="dek">Each page covers the problem, how I reasoned about it, the architecture I chose, and the trade-offs I accepted. Most client names and internal details are withheld, but the reasoning is all here.</p>
  </section>

  <section class="band" aria-labelledby="principles-h">
    <div class="wrap">
      <p class="kicker" id="principles-h">Principles that keep showing up <span class="fmt">Across these projects</span></p>
      <dl class="principles">
        <div><dt>The model advises. Code decides.</dt><dd>Where money, credit or identity is at stake, an LLM gives an opinion and a deterministic, testable rule makes the call.</dd></div>
        <div><dt>People approve risky actions.</dt><dd>Writes to customer systems go through review queues, approval gates or two-person rules.</dd></div>
        <div><dt>Queues over hope.</dt><dd>Slow or flaky work runs in background workers with retries, so the user-facing path stays fast.</dd></div>
        <div><dt>Degrade, don't break.</dt><dd>Circuit breakers, caches and switches let one failing provider slow a system down instead of stopping it.</dd></div>
        <div><dt>Spend compute where it's uncertain.</dt><dd>CPU models handle the common case; the expensive model sees only what the cheap one can't settle.</dd></div>
      </dl>
    </div>
  </section>

  <section class="wrap section" aria-labelledby="all-h">
    <div class="sec-h">
      <h2 id="all-h">All projects</h2>
      <a href="../index.html">Front page ↑</a>
    </div>
    <div class="cols cols--3 hl">
{''.join(cols)}
    </div>
  </section>
</main>
"""
        + footer(1)
        + "</body>\n</html>\n"
    )


REQUIRED = ["slug", "theme", "order", "title", "headline", "dek", "summary", "client", "role", "status",
            "stack", "problem", "approach", "built", "architecture", "flow", "decisions", "challenges", "next", "lesson"]


def main():
    projects = []
    for f in sorted(SRC.glob("*.json")):
        p = json.loads(f.read_text())
        missing = [k for k in REQUIRED if k not in p]
        if missing:
            sys.exit(f"{f.name}: missing {missing}")
        if p["theme"] not in THEME_NAME:
            sys.exit(f"{f.name}: unknown theme {p['theme']!r}")
        projects.append(p)

    by_theme = {}
    for p in projects:
        by_theme.setdefault(p["theme"], []).append(p)
    ordered = []
    for key, _, _ in THEMES:
        by_theme.get(key, []).sort(key=lambda p: p["order"])
        ordered += by_theme.get(key, [])

    OUT.mkdir(exist_ok=True)
    for i, p in enumerate(ordered):
        prev = ordered[i - 1] if i > 0 else None
        nxt = ordered[i + 1] if i + 1 < len(ordered) else None
        (OUT / f"{p['slug']}.html").write_text(project_page(p, prev, nxt))
    (OUT / "index.html").write_text(index_page(by_theme))
    update_front_page(by_theme)
    print(f"built {len(ordered)} project pages + index")


def update_front_page(by_theme):
    """Write every project into the Experience section, between the PROJECTS markers in index.html."""
    page = ROOT / "index.html"
    html = page.read_text()
    start = html.index("<!-- PROJECTS:START")
    start = html.index("-->", start) + 3
    end = html.index("<!-- PROJECTS:END -->")
    groups = []
    for key, name, _ in THEMES:
        items = "\n".join(f"""        <li>
          <details>
            <summary><b>{escape(p["title"])}</b> — {rich(p["summary"])} <span class="status">{escape(p["status"])}</span></summary>
            <div class="deep">
              <h4>Problem</h4>
              <p>{rich(p["problem"][0])}</p>
              <h4>Approach</h4>
              <p>{rich(p["approach"][0])}</p>
              <p class="stack"><b>For:</b> {escape(p["client"])} · <b>Role:</b> {escape(p["role"])}<br><b>Stack:</b> {escape(", ".join(p["stack"]))} · <a href="projects/{p["slug"]}.html">Case study →</a></p>
            </div>
          </details>
        </li>"""
            for p in by_theme.get(key, [])
        )
        groups.append(f"""      <h4>{escape(name)}</h4>
      <ol class="points">
{items}
      </ol>""")
    block = ('\n    <div class="work">\n      <p>Projects, 2025 to present. Open any one for the problem and approach; the case study has the architecture and trade-offs.</p>\n'
             + "\n".join(groups)
             + "\n    </div>\n")
    page.write_text(html[:start] + block + html[end:])


if __name__ == "__main__":
    main()
