import streamlit as st
import pdfplumber
import re
import json
import requests
import pandas as pd

st.set_page_config(page_title="ResuMentor", page_icon="📄", layout="wide")

# ── Global CSS ─────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Inter:wght@400;500;600&display=swap');

html, body, [class*="css"] {
    font-family: 'Inter', 'Segoe UI', sans-serif;
}
.stApp {
    background: #F7F4EE;
}

/* ── Hero header ── */
.rm-hero {
    text-align: center;
    padding: 2.5rem 1rem 2.2rem;
}
.rm-logo {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 3.6rem;
    font-weight: 900;
    color: #1A1A2E;
    letter-spacing: -1px;
    line-height: 1;
}
.rm-logo span {
    color: #D4813A;
}
.rm-tagline {
    font-size: 1.02rem;
    color: #6B6B80;
    margin-top: 0.5rem;
    font-weight: 400;
    letter-spacing: 0.01em;
}

/* ── Section cards ── */
.rm-card {
    background: #FFFFFF;
    border: 1px solid #E8E3D9;
    border-radius: 16px;
    padding: 1.3rem 1.6rem;
    margin-bottom: 1.1rem;
    box-shadow: 0 1px 6px rgba(26,26,46,0.05);
}
.rm-card-title {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.13em;
    color: #D4813A;
    margin-bottom: 0.75rem;
    border-bottom: 1.5px solid #F0EBE0;
    padding-bottom: 0.45rem;
}

/* ── Name ── */
.rm-name {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.8rem;
    font-weight: 700;
    color: #1A1A2E;
    margin: 0;
}

/* ── Contact chips ── */
.rm-contact-row { display: flex; flex-wrap: wrap; gap: 0.5rem; margin-top: 0.4rem; }
.rm-chip {
    background: #F7F4EE;
    border: 1px solid #DDD8CE;
    border-radius: 99px;
    padding: 4px 13px;
    font-size: 0.8rem;
    color: #3D3D55;
    font-weight: 500;
}

/* ── Skill tags ── */
.rm-skill {
    display: inline-block;
    background: #FFF5EC;
    color: #A0541A;
    border: 1px solid #F5D9BC;
    border-radius: 99px;
    padding: 3px 12px;
    font-size: 0.79rem;
    margin: 3px 3px;
    font-weight: 500;
}

/* ── Entry blocks ── */
.rm-entry {
    border-left: 3px solid #E8C9A0;
    padding-left: 0.9rem;
    margin-bottom: 1rem;
}
.rm-entry-title { font-weight: 600; color: #1A1A2E; font-size: 0.92rem; }
.rm-entry-sub   { color: #7A7A90; font-size: 0.8rem; margin: 0.1rem 0 0.2rem; }
.rm-entry-body  { font-size: 0.84rem; color: #3D3D55; line-height: 1.65; }

/* ── Content text ── */
.rm-content {
    font-size: 0.88rem;
    color: #3D3D55;
    white-space: pre-wrap;
    line-height: 1.75;
}

/* ── Project stat bar ── */
.rm-projbar {
    display: flex;
    gap: 0;
    background: #1A1A2E;
    border-radius: 12px;
    padding: 0.85rem 1.2rem;
    margin-bottom: 1rem;
    align-items: center;
}
.rm-projstat { text-align: center; flex: 1; }
.rm-projstat-num {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 1.7rem;
    font-weight: 700;
    color: #FFFFFF;
    line-height: 1;
}
.rm-projstat-label {
    font-size: 0.65rem;
    font-weight: 600;
    color: #8888AA;
    text-transform: uppercase;
    letter-spacing: 0.09em;
    margin-top: 3px;
}
.rm-projdiv {
    width: 1px;
    background: rgba(255,255,255,0.15);
    align-self: stretch;
    min-height: 40px;
    margin: 0 0.4rem;
}

/* ── Project list items ── */
.rm-proj-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.5rem 0.8rem;
    margin-bottom: 0.4rem;
    background: #F7F4EE;
    border-radius: 9px;
    border-left: 3px solid #D4813A;
}
.rm-proj-num { font-size: 0.75rem; font-weight: 700; color: #D4813A; min-width: 22px; }
.rm-proj-name { font-size: 0.87rem; color: #1A1A2E; font-weight: 600; }
.rm-proj-badge {
    margin-left: auto;
    font-size: 0.7rem;
    background: #FFF5EC;
    color: #A0541A;
    border-radius: 99px;
    padding: 2px 9px;
    border: 1px solid #F5D9BC;
}
.rm-gh-item {
    display: flex;
    align-items: center;
    gap: 0.6rem;
    padding: 0.5rem 0.8rem;
    margin-bottom: 0.4rem;
    background: #F0FBF6;
    border-radius: 9px;
    border-left: 3px solid #2D9E6B;
}
.rm-gh-num { font-size: 0.75rem; font-weight: 700; color: #2D9E6B; min-width: 22px; }
.rm-gh-badge {
    margin-left: auto;
    font-size: 0.7rem;
    background: #E5F7EF;
    color: #1A6B47;
    border-radius: 99px;
    padding: 2px 9px;
    border: 1px solid #B8E8D0;
}

/* ── Mentor rating button ── */
.rm-rate-btn-wrap { text-align: center; margin: 2rem 0 0.5rem; }

/* ── Star rating display ── */
.rm-rating-card {
    background: #FFFFFF;
    border: 1px solid #E8E3D9;
    border-radius: 20px;
    padding: 2rem 2rem 1.6rem;
    text-align: center;
    max-width: 520px;
    margin: 1rem auto;
    box-shadow: 0 4px 24px rgba(26,26,46,0.08);
}
.rm-rating-label {
    font-size: 0.7rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.14em;
    color: #8888AA;
    margin-bottom: 0.7rem;
}
.rm-stars {
    font-size: 2.8rem;
    line-height: 1;
    letter-spacing: 3px;
    margin: 0.3rem 0 0.5rem;
    color: #D4813A;
}
.rm-rating-score {
    font-family: 'Playfair Display', Georgia, serif;
    font-size: 2.6rem;
    font-weight: 900;
    color: #1A1A2E;
    line-height: 1;
}
.rm-rating-grade {
    font-size: 1rem;
    font-weight: 600;
    margin-top: 0.3rem;
}
.rm-rating-meta {
    font-size: 0.8rem;
    color: #9999B0;
    margin-top: 0.9rem;
    line-height: 1.7;
}
.rm-rating-pills {
    display: flex;
    justify-content: center;
    gap: 0.5rem;
    flex-wrap: wrap;
    margin-top: 0.75rem;
}
.rm-rating-pill {
    background: #F7F4EE;
    border: 1px solid #E0DAD0;
    border-radius: 99px;
    padding: 4px 14px;
    font-size: 0.78rem;
    color: #3D3D55;
    font-weight: 500;
}

/* ── Projects list: collapse Streamlit's default block spacing
   around each st.markdown() call so project rows sit tight together.
   Targets the block container directly (not nested inside a wrapper,
   since each st.markdown() call is its own sibling in the real DOM) ── */
div[data-testid="stVerticalBlock"] > div[data-testid="element-container"]:has(> div[data-testid="stMarkdownContainer"] > div.rm-proj-item),
div[data-testid="stVerticalBlock"] > div[data-testid="element-container"]:has(> div[data-testid="stMarkdownContainer"] > div.rm-gh-item) {
    margin-bottom: 0.4rem !important;
}
div[data-testid="stMarkdownContainer"]:has(> div.rm-proj-item),
div[data-testid="stMarkdownContainer"]:has(> div.rm-gh-item) {
    margin: 0 !important;
}

/* ── Github divider ── */
.rm-gh-divider {
    font-size: 0.68rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #2D9E6B;
    margin: 1rem 0 0.5rem;
    border-bottom: 1.5px solid #D0F0E4;
    padding-bottom: 0.3rem;
}

/* ── Streamlit component tweaks ── */
.stFileUploader > label { font-weight: 600; color: #1A1A2E; }
.stButton > button {
    background: #1A1A2E !important;
    color: #FFFFFF !important;
    border: none !important;
    border-radius: 10px !important;
    padding: 0.55rem 1.6rem !important;
    font-weight: 600 !important;
    font-size: 0.9rem !important;
    letter-spacing: 0.03em !important;
    transition: background 0.2s !important;
}
.stButton > button:hover {
    background: #D4813A !important;
}
div[data-testid="stExpander"] {
    background: #FFFFFF;
    border: 1px solid #E8E3D9 !important;
    border-radius: 12px !important;
    margin-bottom: 0.8rem;
}
div[data-testid="stExpander"] summary {
    color: #1A1A2E !important;
    font-weight: 600 !important;
}
div[data-testid="stExpander"] summary p,
div[data-testid="stExpander"] summary span,
div[data-testid="stExpander"] summary div {
    color: #1A1A2E !important;
}
div[data-testid="stExpander"] svg {
    fill: #1A1A2E !important;
}
div[data-testid="stExpanderDetails"] {
    background: #FFFFFF;
    color: #3D3D55 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ── Hero ───────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="rm-hero">
  <div class="rm-logo">Resu<span>Mentor</span></div>
  <p class="rm-tagline">Drop your resume — we'll handle the rest</p>
</div>
""",
    unsafe_allow_html=True,
)


# ── Text extraction ────────────────────────────────────────────────────────────
def extract_text(file) -> str:
    text = ""
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            t = page.extract_text()
            if t:
                text += t + "\n"
    return text.strip()


# ── Section splitter ───────────────────────────────────────────────────────────
HEADINGS = {
    "SUMMARY":        r"(professional summary|summary|objective|about me|profile|career objective|career profile|professional profile|about|overview)",
    "SKILLS":         r"(technical skills?|skills?|core competencies|technologies|tools|tech stack|expertise|competencies|key skills?|it skills?|programming skills?|soft skills?)",
    "EDUCATION":      r"(education|academic|qualifications|academic background|educational background|academic qualifications|degrees?)",
    "EXPERIENCE":     r"(work experience|professional experience|employment history|experience|work history|career history|job experience|relevant experience)",
    "INTERNSHIP":     r"(internships?|intern experience|training experience|industrial training|vocational training|summer internship|winter internship|internship experience|industry experience|practical experience|practical training|apprenticeship|work placement|placement experience|industrial experience)",
    "PROJECTS":       r"(projects?|personal projects?|academic projects?|key projects?|major projects?|mini projects?|project work|project details|notable projects?|relevant projects?|college projects?)",
    "CERTIFICATIONS": r"(certifications?|licenses?|courses?|credentials?|certificate programs?|online courses?|professional certifications?|training certifications?|moocs?|udemy|coursera|nptel)",
    "ACHIEVEMENTS":   r"(achievements?|awards?|honors?|honours?|accomplishments?|hackathon|extra curricular|activities|positions? of responsibility|leadership|volunteering|volunteer)",
    "LANGUAGES":      r"(languages?|spoken languages?|language proficiency)",
}

def parse_resume(text: str) -> dict:
    lines = text.splitlines()
    result = {k: [] for k in HEADINGS}
    result["_name"] = ""
    result["_contact"] = {"Email": [], "Phone": [], "LinkedIn": [], "GitHub": []}

    result["_contact"]["Email"]    = list(set(re.findall(r"[\w.\-+]+@[\w.\-]+\.\w{2,}", text)))
    result["_contact"]["Phone"]    = list(set(re.findall(r"(?<!\d)(\+?[\d][\d\s\-().]{7,15}\d)(?!\d)", text)))[:2]
    result["_contact"]["LinkedIn"] = list(set(re.findall(r"linkedin\.com/in/[\w\-]+", text, re.I)))
    result["_contact"]["GitHub"]   = list(set(re.findall(r"github\.com/[\w\-]+", text, re.I)))

    for line in lines:
        l = line.strip()
        if l and not re.search(r"[@|/\\]|\d{5,}|http|linkedin|github", l, re.I) and 1 < len(l.split()) <= 6 and len(l) < 50:
            result["_name"] = l
            break

    current = None
    for line in lines:
        stripped = line.strip()
        if not stripped:
            if current:
                result[current].append("")
            continue
        matched = False
        clean_stripped = re.sub(r"[:\-\u2013]+$", "", stripped).strip()
        for section, pattern in HEADINGS.items():
            if (
                re.fullmatch(pattern, clean_stripped, re.IGNORECASE)
                or re.fullmatch(pattern, stripped, re.IGNORECASE)
                or (len(stripped) < 50 and re.match(r"^" + pattern + r"[\s:]*$", stripped, re.IGNORECASE))
                or (len(clean_stripped) < 50 and re.match(r"^" + pattern + r"[\s:]*$", clean_stripped, re.IGNORECASE))
            ):
                current = section
                matched = True
                break
        if not matched and current:
            result[current].append(stripped)

    raw_skill = " ".join(result.get("SKILLS", []))
    result["_skill_tags"] = [s.strip() for s in re.split(r"[,|•·/]", raw_skill) if 1 < len(s.strip()) < 40]

    return result


def section_card(title: str, content_html: str):
    st.markdown(f"""
    <div class="rm-card">
      <div class="rm-card-title">{title}</div>
      {content_html}
    </div>""", unsafe_allow_html=True)


# ── GitHub repo fetcher ────────────────────────────────────────────────────────
def fetch_github_projects(username: str) -> list:
    try:
        url = f"https://api.github.com/users/{username}/repos?per_page=100&sort=updated"
        resp = requests.get(url, timeout=8)
        if resp.status_code == 200:
            repos = resp.json()
            return [
                {
                    "name": r["name"],
                    "description": r.get("description") or "",
                    "language": r.get("language") or "",
                    "stars": r.get("stargazers_count", 0),
                    "url": r.get("html_url", ""),
                    "topics": r.get("topics", []),
                }
                for r in repos if not r.get("fork", False)
            ]
        else:
            return []
    except Exception:
        return []


def lines_to_entries(lines):
    entries, current_entry = [], []
    for l in lines:
        if l == "":
            if current_entry:
                entries.append(current_entry)
                current_entry = []
        else:
            current_entry.append(l)
    if current_entry:
        entries.append(current_entry)
    return entries


# ── Upload ─────────────────────────────────────────────────────────────────────
uploaded = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

if uploaded:
    with st.spinner("Reading PDF…"):
        raw_text = extract_text(uploaded)
    if not raw_text:
        st.error("No text found in this PDF. It may be a scanned image. Try a text-based PDF.")
        st.stop()

    with st.spinner("Parsing sections…"):
        data = parse_resume(raw_text)

    st.success(f"Here's what we found in **{uploaded.name}**")
    st.markdown("---")

    # ── NAME ──────────────────────────────────────────────────────────────────
    name = data["_name"]
    section_card("👤 Name",
        f'<p class="rm-name">{name or "Not detected"}</p>')

    # ── CONTACT ───────────────────────────────────────────────────────────────
    cp = data["_contact"]
    contact_chips = ""
    for label, vals in cp.items():
        for v in vals:
            contact_chips += f'<span class="rm-chip">📌 {label}: {v}</span>'
    if contact_chips:
        section_card("📬 Contact",
            f'<div class="rm-contact-row">{contact_chips}</div>')

    # ── SUMMARY ───────────────────────────────────────────────────────────────
    summary = [l for l in data.get("SUMMARY", []) if l]
    if summary:
        section_card("📝 Summary",
            f'<p class="rm-content">{chr(10).join(summary)}</p>')

    # ── Pre-calculate project counts BEFORE columns ───────────────────────────
    import difflib
    proj_raw_pre   = [l for l in data.get("PROJECTS", []) if l]
    gh_links_pre   = data["_contact"].get("GitHub", [])
    gh_repos_pre   = []
    gh_username_pre = None
    if gh_links_pre:
        match_pre = re.search(r"github\.com/([^/\s]+)", gh_links_pre[0], re.I)
        if match_pre:
            gh_username_pre = match_pre.group(1)
            gh_repos_pre = fetch_github_projects(gh_username_pre)

    def normalize_pre(s):
        return re.sub(r"[^a-z0-9]", "", s.lower())

    def extract_proj_names_pre(lines):
        names = []
        for line in lines:
            stripped = line.strip()
            if stripped.startswith(("-","•","*")): continue
            if len(stripped) < 5: continue
            if stripped[0].islower(): continue
            desc_patterns = [r"^(and |the |to |for |with |by |in |of )",r"^(trends|insights|decisions|patterns|records)",r"^\d+\."]
            if any(re.match(p, stripped, re.I) for p in desc_patterns): continue
            clean = re.sub(r"\s*[|–-]\s*(Tech Stack|Tech|Stack|View Project).*","",stripped,flags=re.I)
            clean = re.sub(r"\s*View Project.*","",clean,flags=re.I)
            clean = re.sub(r"\s*Analyzed\s+[\d,+]+.*","",clean,flags=re.I)
            clean = re.sub(r"\s*Created\s+.*","",clean,flags=re.I)
            clean = clean.strip(" –-|:")
            if len(clean) > 4: names.append(clean)
        return names

    resume_proj_names_pre = extract_proj_names_pre(proj_raw_pre)
    resume_proj_count_pre = len(resume_proj_names_pre)
    github_proj_count_pre = len(gh_repos_pre)
    gh_norm   = [normalize_pre(r["name"]) for r in gh_repos_pre]
    res_norm  = [normalize_pre(n) for n in resume_proj_names_pre]
    dups_pre  = sum(1 for rn in res_norm if difflib.get_close_matches(rn, gh_norm, n=1, cutoff=0.7))
    total_proj_count = resume_proj_count_pre + github_proj_count_pre - dups_pre

    col1, col2 = st.columns(2, gap="large")

    with col1:
        # SKILLS
        tags = data.get("_skill_tags", [])
        if tags:
            tags_html = "".join(f'<span class="rm-skill">{t}</span>' for t in tags)
            section_card("🛠️ Skills", tags_html)
        elif data.get("SKILLS"):
            section_card("🛠️ Skills",
                f'<p class="rm-content">{chr(10).join(data["SKILLS"])}</p>')

        # EDUCATION
        edu = [l for l in data.get("EDUCATION", []) if l]
        if edu:
            entries = lines_to_entries(edu)
            html = ""
            for e in entries:
                html += '<div class="rm-entry">'
                html += f'<div class="rm-entry-title">{e[0]}</div>'
                for sub in e[1:]:
                    html += f'<div class="rm-entry-body">{sub}</div>'
                html += "</div>"
            section_card("🎓 Education", html)

        # CERTIFICATIONS
        certs = [l for l in data.get("CERTIFICATIONS", []) if l]
        if certs:
            entries = lines_to_entries(certs)
            html = ""
            for e in entries:
                html += '<div class="rm-entry">'
                html += f'<div class="rm-entry-title">{e[0]}</div>'
                for sub in e[1:]:
                    html += f'<div class="rm-entry-body">{sub}</div>'
                html += "</div>"
            section_card("🏅 Certifications", html)

        # ACHIEVEMENTS
        ach = [l for l in data.get("ACHIEVEMENTS", []) if l]
        if ach:
            html = "".join(f'<div class="rm-entry-body" style="margin-bottom:0.3rem;">• {l}</div>' for l in ach)
            section_card("🏆 Achievements", html)

    with col2:
        # EXPERIENCE
        exp = [l for l in data.get("EXPERIENCE", []) if l]
        if exp:
            entries = lines_to_entries(exp)
            html = ""
            for e in entries:
                html += '<div class="rm-entry">'
                html += f'<div class="rm-entry-title">{e[0]}</div>'
                for sub in e[1:]:
                    html += f'<div class="rm-entry-body">{sub}</div>'
                html += "</div>"
            section_card("💼 Work Experience", html)

        # INTERNSHIP
        intern = [l for l in data.get("INTERNSHIP", []) if l]
        if intern:
            entries = []
            current_entry = []
            for line in intern:
                is_new_entry = (
                    line
                    and not line.startswith(("-", "•", "*", "-"))
                    and not re.match(r"^(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\d)", line, re.I)
                    and not re.match(r"^(remote|onsite|hybrid|present|expected)", line, re.I)
                    and len(line) > 10
                    and current_entry
                    and re.search(r"(intern|analyst|engineer|developer|scientist|manager|at |@)", line, re.I)
                )
                if is_new_entry:
                    if current_entry:
                        entries.append(current_entry)
                    current_entry = [line]
                elif line == "":
                    if current_entry:
                        entries.append(current_entry)
                    current_entry = []
                else:
                    current_entry.append(line)
            if current_entry:
                entries.append(current_entry)
            if len(entries) <= 1:
                entries = lines_to_entries(intern)

            html = ""
            for e in entries:
                if not e:
                    continue
                html += '<div class="rm-entry">'
                html += f'<div class="rm-entry-title">{e[0]}</div>'
                for sub in e[1:]:
                    html += f'<div class="rm-entry-body">{sub}</div>'
                html += "</div>"
            section_card(f"🏢 Internship ({len(entries)} found)", html)

        # ── PROJECTS (resume + GitHub) ─────────────────────────────────────
        proj_raw = [l for l in data.get("PROJECTS", []) if l]

        def extract_project_names(lines):
            names = []
            for line in lines:
                stripped = line.strip()
                if stripped.startswith("-") or stripped.startswith("•") or stripped.startswith("*"):
                    continue
                if len(stripped) < 5:
                    continue
                if stripped[0].islower():
                    continue
                desc_patterns = [
                    r"^(and |the |to |for |with |by |in |of )",
                    r"^(trends|insights|decisions|patterns|records)",
                    r"^\d+\.",
                ]
                if any(re.match(p, stripped, re.I) for p in desc_patterns):
                    continue
                clean = re.sub(r"\s*[|–-]\s*(Tech Stack|Tech|Stack|View Project).*", "", stripped, flags=re.I)
                clean = re.sub(r"\s*View Project.*", "", clean, flags=re.I)
                clean = re.sub(r"\s*Analyzed\s+[\d,+]+.*", "", clean, flags=re.I)
                clean = re.sub(r"\s*Created\s+.*", "", clean, flags=re.I)
                clean = clean.strip(" –-|:")
                if len(clean) > 4:
                    names.append(clean)
            return names

        resume_proj_names = extract_project_names(proj_raw)
        resume_proj_count = len(resume_proj_names)

        # Fetch GitHub repos
        gh_repos    = []
        gh_links    = data["_contact"].get("GitHub", [])
        gh_username = None
        if gh_links:
            match = re.search(r"github\.com/([^/\s]+)", gh_links[0], re.I)
            if match:
                gh_username = match.group(1)
                with st.spinner(f"🐙 Fetching GitHub repos for @{gh_username}…"):
                    gh_repos = fetch_github_projects(gh_username)

        github_proj_count = len(gh_repos)

        import difflib as _difflib
        def normalize(s):
            return re.sub(r"[^a-z0-9]", "", s.lower())

        gh_normalized = [normalize(r["name"]) for r in gh_repos]
        resume_normalized = [normalize(n) for n in resume_proj_names]
        duplicates = sum(
            1 for rn in resume_normalized
            if _difflib.get_close_matches(rn, gh_normalized, n=1, cutoff=0.7)
        )
        total_proj_count = resume_proj_count + github_proj_count - duplicates

        if proj_raw or gh_repos:
            # Open card + stat bar + divider (kept short and separate from the
            # per-item loop below — very long single HTML strings can get
            # rendered as raw text by Streamlit instead of parsed HTML)
            st.markdown(f"""
            <div class="rm-card">
              <div class="rm-card-title">🚀 Projects</div>
              <div class="rm-projbar">
                <div class="rm-projstat">
                  <div class="rm-projstat-num">📄 {resume_proj_count}</div>
                  <div class="rm-projstat-label">Resume Projects</div>
                </div>
                <div class="rm-projdiv"></div>
                <div class="rm-projstat">
                  <div class="rm-projstat-num">🐙 {github_proj_count}</div>
                  <div class="rm-projstat-label">GitHub Repos</div>
                </div>
                <div class="rm-projdiv"></div>
                <div class="rm-projstat">
                  <div class="rm-projstat-num">✨ {total_proj_count}</div>
                  <div class="rm-projstat-label">Total Unique Projects</div>
                </div>
              </div>
              <div class="rm-gh-divider">📋 All Project Names</div>
            </div>
            """, unsafe_allow_html=True)

            # Build all row HTML, then flush in small batches (4 rows per
            # st.markdown call). This avoids both failure modes seen before:
            # one huge call gets dumped as raw text by Streamlit, while one
            # call per row creates a visible white gap between every row.
            all_rows = []
            for i, name_r in enumerate(resume_proj_names, 1):
                all_rows.append(
                    f'<div class="rm-proj-item">'
                    f'<span class="rm-proj-num">#{i}</span>'
                    f'<span class="rm-proj-name">📄 {name_r}</span>'
                    f'<span class="rm-proj-badge">Resume</span>'
                    f'</div>'
                )

            for j, repo in enumerate(gh_repos, resume_proj_count + 1):
                repo_url  = repo["url"]
                repo_name = repo["name"]
                repo_lang = repo.get("language") or ""
                lang_badge = (
                    f'<span style="font-size:0.7rem;background:#D0F0E4;color:#1A6B47;'
                    f'border-radius:99px;padding:2px 8px;margin-right:4px;">{repo_lang}</span>'
                    if repo_lang.strip() else ""
                )
                all_rows.append(
                    f'<div class="rm-gh-item">'
                    f'<span class="rm-gh-num">#{j}</span>'
                    f'<a href="{repo_url}" target="_blank" '
                    f'style="font-size:0.87rem;color:#1A1A2E;font-weight:600;text-decoration:none;">'
                    f'🐙 {repo_name}</a>'
                    f'<span style="margin-left:auto;display:flex;align-items:center;gap:4px;">'
                    f'{lang_badge}<span class="rm-gh-badge">GitHub</span></span>'
                    f'</div>'
                )

            BATCH_SIZE = 4
            for k in range(0, len(all_rows), BATCH_SIZE):
                st.markdown("".join(all_rows[k:k + BATCH_SIZE]), unsafe_allow_html=True)

            if not gh_repos and gh_username:
                st.markdown('<p style="color:#ef4444;font-size:0.83rem;">⚠️ Could not fetch GitHub repos (private profile or API limit).</p>', unsafe_allow_html=True)

    # ── Raw text ──────────────────────────────────────────────────────────────
    with st.expander("📃 View Raw Extracted Text"):
        st.text(raw_text)

    # ── Debug: show detected sections ─────────────────────────────────────────
    with st.expander("🔍 Debug — What sections were detected from your resume?"):
        for sec in ["SUMMARY","SKILLS","EDUCATION","EXPERIENCE","INTERNSHIP","PROJECTS","CERTIFICATIONS","ACHIEVEMENTS","LANGUAGES"]:
            lines_found = [l for l in data.get(sec, []) if l]
            status = f"✅ {len(lines_found)} lines found" if lines_found else "❌ Not detected"
            st.markdown(f"**{sec}**: {status}")
            if lines_found:
                st.caption(" | ".join(lines_found[:3]) + ("..." if len(lines_found) > 3 else ""))

    # ── JSON export ───────────────────────────────────────────────────────────
    export = {
        "name": data["_name"],
        "contact": data["_contact"],
        "summary": summary,
        "skills": data.get("_skill_tags", []),
        "education": edu if 'edu' in dir() else [],
        "experience": exp if 'exp' in dir() else [],
        "internship": intern if 'intern' in dir() else [],
        "projects": proj_raw if 'proj_raw' in dir() else [],
        "github_repos": [r["name"] for r in gh_repos] if gh_repos else [],
        "project_counts": {
            "resume": resume_proj_count,
            "github": github_proj_count,
            "total": total_proj_count,
        },
        "certifications": certs if 'certs' in dir() else [],
        "achievements": ach if 'ach' in dir() else [],
    }
    st.download_button(
        "⬇️ Download Parsed Data as JSON",
        data=json.dumps(export, indent=2),
        file_name="parsed_resume.json",
        mime="application/json",
    )

    # Save parsed resume JSON for dataset building
    try:
        import time, os
        parsed_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "parsed_resumes")
        os.makedirs(parsed_dir, exist_ok=True)
        mentor_id = None
        gh = export.get('contact', {}).get('GitHub', [])
        emails = export.get('contact', {}).get('Email', [])
        if gh:
            mentor_id = gh[0].split('/')[-1]
        elif emails:
            mentor_id = emails[0].split('@')[0]
        else:
            mentor_id = export.get('name') or os.path.splitext(uploaded.name)[0]
        safe = re.sub(r"[^0-9a-zA-Z_-]", "_", str(mentor_id))[:50]
        fname = f"{safe}_{int(time.time())}.json"
        path = os.path.join(parsed_dir, fname)
        with open(path, 'w', encoding='utf-8') as fh:
            json.dump(export, fh, ensure_ascii=False, indent=2)
    except Exception:
        pass  # internal dataset logging only — safe to skip silently

    # ── MENTOR RATING — Button-triggered, 5-star display ──────────────────────
    st.markdown("---")
    st.markdown('<div class="rm-rate-btn-wrap">', unsafe_allow_html=True)

    if "show_rating" not in st.session_state:
        st.session_state["show_rating"] = False

    col_btn_l, col_btn_c, col_btn_r = st.columns([2, 1, 2])
    with col_btn_c:
        if st.button("See Profile Score"):
            st.session_state["show_rating"] = True

    st.markdown('</div>', unsafe_allow_html=True)

    if st.session_state["show_rating"]:
        skills_count_ml   = len(data.get("_skill_tags", []))
        projects_count_ml = total_proj_count
        exp_lines_ml      = [l for l in data.get("EXPERIENCE", []) if l]
        internship_lines  = [l for l in data.get("INTERNSHIP", []) if l]

        # ── Real duration parsing ───────────────────────────────────────
        # Reads actual date ranges like "June 2025 – July 2025" or
        # "Jan 2023 - Present" out of the EXPERIENCE/INTERNSHIP text and
        # sums real months, instead of guessing from line counts.
        import datetime

        MONTHS = {
            "jan": 1, "feb": 2, "mar": 3, "apr": 4, "may": 5, "jun": 6,
            "jul": 7, "aug": 8, "sep": 9, "oct": 10, "nov": 11, "dec": 12,
        }

        def parse_month_year(token: str):
            token = token.strip().lower()
            if token in ("present", "current", "now", "till date", "ongoing", "expected"):
                today = datetime.date.today()
                return today.year * 12 + today.month
            m = re.match(r"([a-z]{3,9})[a-z]*\.?\s+(\d{4})", token)
            if m:
                mon_str, year_str = m.group(1)[:3], m.group(2)
                if mon_str in MONTHS:
                    return int(year_str) * 12 + MONTHS[mon_str]
            m2 = re.match(r"(\d{4})$", token)
            if m2:
                return int(m2.group(1)) * 12 + 1
            return None

        def total_months_from_lines(lines):
            text = " ".join(lines)
            # Matches "Jan 2023 – Dec 2023", "June 2025 - July 2025",
            # "Jan 2023 - Present", "2022 - 2023", etc.
            # Anchored on actual month-name tokens (not a generic word) so
            # it can't swallow a preceding job title like "Senior Analyst
            # 2019" as if "Analyst" were part of the date — that bug caused
            # any resume with more than one date range, or a bare-year
            # range preceded by a title on the same line, to silently
            # return 0 months for that entry.
            MONTH_NAMES = r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            date_token = rf"{MONTH_NAMES}[a-z]*\.?\s+\d{{4}}|\d{{4}}"
            pattern = re.compile(
                rf"\b({date_token})\s*[-–—]+\s*"
                rf"({date_token}|present|current|now|till date|ongoing|expected)\b",
                re.IGNORECASE,
            )
            months = 0
            for start_raw, end_raw in pattern.findall(text):
                start = parse_month_year(start_raw)
                end = parse_month_year(end_raw)
                if start is not None and end is not None and end >= start:
                    months += (end - start) + 1  # inclusive of both months
            return months

        exp_months = total_months_from_lines(exp_lines_ml)
        intern_months = total_months_from_lines(internship_lines)
        total_months = exp_months + intern_months

        if total_months > 0:
            experience_years = round(total_months / 12, 3)
        elif exp_lines_ml:
            # Dates couldn't be parsed but there is experience text —
            # don't silently report 0; fall back to a conservative
            # estimate rather than guessing a full year.
            experience_years = 0.5
        elif internship_lines:
            experience_years = 0.25
        else:
            experience_years = 0

        feedback_score = 3.0  # neutral default — no real feedback collected yet

        # ── Mentor rating: documented weighted formula ──────────────────
        # mentor_rating = (experience_years * 2) + (skills_count * 1.5)
        #                + (projects_count * 1.2) + (feedback_score * 10)
        # capped at 100. This is the formula the project's own dataset
        # generator (Final Dataset.py) and design doc define, and unlike
        # the previously-used mentor_model.pkl (an XGBoost model trained
        # on only 40 synthetic rows of WHOLE-NUMBER experience_years from
        # 1–15, i.e. working professionals), it is linear and well-behaved
        # at ANY experience value — including fractional years from a
        # resume with only a few months of internship. The pickled model
        # had never seen values like 0.17 during training, so it would
        # silently clamp to its nearest learned region and effectively
        # ignore experience for students — that's why it kept returning
        # "Excellent Mentor" regardless of whether someone had 2 months
        # or 2 years of experience. This formula has no such blind spot.
        predicted_rating = (
            (experience_years * 2)
            + (skills_count_ml * 1.5)
            + (projects_count_ml * 1.2)
            + (feedback_score * 10)
        )
        predicted_rating = min(round(predicted_rating, 2), 100.0)
        predicted_rating = max(predicted_rating, 0.0)

        # Convert 0-100 → 0-10 rating (the number shown to the user)
        rating_out_of_10 = round((predicted_rating / 100.0) * 10.0, 1)

        # Stars are still shown out of 5 for the visual, derived from the
        # same 0-10 rating (rating_out_of_10 / 10 * 5 == rating_out_of_10 / 2)
        stars_float = rating_out_of_10 / 2.0
        full_stars  = int(stars_float)
        half_star   = 1 if (stars_float - full_stars) >= 0.4 else 0
        empty_stars = 5 - full_stars - half_star

        stars_display = "★" * full_stars + ("½" if half_star else "") + "☆" * empty_stars

        if predicted_rating >= 80:
            grade, grade_color = "Strong Profile", "#10b981"
        elif predicted_rating >= 60:
            grade, grade_color = "Solid Profile", "#6366f1"
        elif predicted_rating >= 40:
            grade, grade_color = "Growing Profile", "#f59e0b"
        else:
            grade, grade_color = "Early Stage", "#ef4444"

        if experience_years >= 1:
            exp_label = f"{experience_years:g} yrs"
        elif experience_years > 0:
            months_label = round(experience_years * 12)
            exp_label = f"{months_label} mo" if months_label != 1 else "1 mo"
        else:
            exp_label = "Fresher"

        st.markdown(f"""
        <div class="rm-rating-card">
          <div class="rm-rating-label">Profile Score</div>
          <div class="rm-stars" title="{rating_out_of_10:.1f} out of 10">{stars_display}</div>
          <div class="rm-rating-score">{rating_out_of_10:.1f} <span style="font-size:1.2rem;color:#9999B0;">/ 10</span></div>
          <div class="rm-rating-grade" style="color:{grade_color};">{grade}</div>
          <div class="rm-rating-pills">
            <span class="rm-rating-pill">⏱ {exp_label}</span>
            <span class="rm-rating-pill">🛠 {skills_count_ml} skills</span>
            <span class="rm-rating-pill">🚀 {projects_count_ml} projects</span>
          </div>
          <div class="rm-rating-meta">Based on your experience, skills and project count</div>
        </div>
        """, unsafe_allow_html=True)