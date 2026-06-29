import streamlit as st
import pdfplumber
import re
import json
import requests
import pandas as pd
import pickle

st.set_page_config(page_title="Resume Parser", page_icon="📄", layout="wide")

st.markdown("""
<style>
body { font-family: 'Segoe UI', sans-serif; }
.main-title {
    font-size: 2.2rem; font-weight: 800; color: #1e293b;
    text-align: center; margin-bottom: 0.2rem;
}
.subtitle {
    text-align: center; color: #64748b; margin-bottom: 1.5rem; font-size: 1rem;
}
.pipeline {
    display: flex; justify-content: center; align-items: center;
    gap: 0.4rem; flex-wrap: wrap;
    background: linear-gradient(90deg,#6366f1,#8b5cf6);
    border-radius: 10px; padding: 0.8rem 1rem;
    color: white; font-size: 0.9rem; margin-bottom: 2rem;
    font-weight: 500;
}
.section-wrap {
    background: #ffffff;
    border: 1.5px solid #e2e8f0;
    border-radius: 14px;
    padding: 1.2rem 1.5rem;
    margin-bottom: 1.2rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}
.sec-title {
    font-size: 0.72rem;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.1em;
    color: #6366f1;
    margin-bottom: 0.6rem;
    border-bottom: 2px solid #e0e7ff;
    padding-bottom: 0.4rem;
}
.name-text {
    font-size: 1.7rem;
    font-weight: 800;
    color: #1e293b;
    margin: 0;
}
.contact-row {
    display: flex; flex-wrap: wrap; gap: 0.6rem; margin-top: 0.4rem;
}
.contact-chip {
    background: #f1f5f9; border: 1px solid #cbd5e1;
    border-radius: 20px; padding: 3px 12px;
    font-size: 0.82rem; color: #334155;
}
.skill-tag {
    display: inline-block;
    background: #ede9fe; color: #4c1d95;
    border-radius: 20px; padding: 3px 13px;
    font-size: 0.82rem; margin: 3px 3px;
    font-weight: 500;
}
.content-text {
    font-size: 0.88rem; color: #374151;
    white-space: pre-wrap; line-height: 1.7;
}
.entry-block {
    border-left: 3px solid #c7d2fe;
    padding-left: 0.8rem;
    margin-bottom: 0.9rem;
}
.entry-title { font-weight: 700; color: #1e293b; font-size: 0.92rem; }
.entry-sub   { color: #6b7280; font-size: 0.82rem; margin-bottom: 0.2rem; }
.entry-body  { font-size: 0.85rem; color: #374151; line-height: 1.6; }
.github-card {
    border: 1.5px solid #d1d5db;
    border-radius: 10px;
    padding: 0.75rem 1rem;
    margin-bottom: 0.75rem;
    background: #f8fafc;
    transition: box-shadow 0.2s;
}
.github-card:hover { box-shadow: 0 4px 12px rgba(99,102,241,0.15); border-color: #a5b4fc; }
.github-card-title { font-weight: 700; color: #4f46e5; font-size: 0.92rem; text-decoration: none; }
.github-card-title:hover { text-decoration: underline; }
.github-card-desc { color: #6b7280; font-size: 0.82rem; margin: 0.2rem 0 0.4rem; }
.github-card-meta { display: flex; gap: 0.8rem; flex-wrap: wrap; font-size: 0.78rem; color: #9ca3af; }
.lang-dot { display:inline-block; width:10px; height:10px; border-radius:50%; background:#6366f1; margin-right:3px; }
.gh-divider { font-size:0.72rem; font-weight:700; text-transform:uppercase; letter-spacing:0.1em; color:#10b981; margin: 0.8rem 0 0.5rem; border-bottom: 2px solid #d1fae5; padding-bottom:0.3rem; }
.proj-stats-bar {
    display: flex; gap: 0; flex-wrap: wrap;
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    border-radius: 10px; padding: 0.75rem 1.2rem;
    margin-bottom: 1rem; align-items: center;
}
.proj-stat-box {
    text-align: center; flex: 1; min-width: 70px;
}
.proj-stat-num {
    font-size: 1.6rem; font-weight: 900; color: #ffffff; line-height: 1;
}
.proj-stat-label {
    font-size: 0.68rem; font-weight: 600; color: #c7d2fe;
    text-transform: uppercase; letter-spacing: 0.08em; margin-top: 2px;
}
.proj-stat-divider {
    width: 1px; background: rgba(255,255,255,0.35);
    align-self: stretch; min-height: 40px; margin: 0 0.5rem;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">📄 Resume Parser</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload your resume PDF — we\'ll extract and display every section clearly</div>', unsafe_allow_html=True)
st.markdown("""
<div class="pipeline">
  📤 Upload &nbsp;→&nbsp; 🔍 Extract Text &nbsp;→&nbsp;
  🗂️ Identify Sections &nbsp;→&nbsp; ✅ Display Results
</div>
""", unsafe_allow_html=True)


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
    "SUMMARY":        r"(professional summary|summary|objective|about me|profile|career objective)",
    "SKILLS":         r"(technical skills?|skills?|core competencies|technologies|tools)",
    "EDUCATION":      r"(education|academic|qualifications)",
    "EXPERIENCE":     r"(work experience|professional experience|employment history|experience)",
    "INTERNSHIP":     r"(internship|intern experience|training experience)",
    "PROJECTS":       r"(projects?|personal projects?|academic projects?|key projects?)",
    "CERTIFICATIONS": r"(certifications?|licenses?|courses?|credentials?)",
    "ACHIEVEMENTS":   r"(achievements?|awards?|honors?|accomplishments?|hackathon)",
    "LANGUAGES":      r"(languages?)",
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
        for section, pattern in HEADINGS.items():
            if re.fullmatch(pattern, stripped, re.IGNORECASE) or \
               (len(stripped) < 40 and re.match(r"^" + pattern + r"[:\s]*$", stripped, re.IGNORECASE)):
                current = section
                matched = True
                break
        if not matched and current:
            result[current].append(stripped)

    raw_skill = " ".join(result.get("SKILLS", []))
    result["_skill_tags"] = [s.strip() for s in re.split(r"[,|•·/]", raw_skill) if 1 < len(s.strip()) < 40]

    return result


def section_box(title: str, content_html: str):
    st.markdown(f"""
    <div class="section-wrap">
      <div class="sec-title">{title}</div>
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
uploaded = st.file_uploader("Upload Resume (PDF)", type=["pdf"])

if uploaded:
    with st.spinner("Reading PDF…"):
        raw_text = extract_text(uploaded)
    if not raw_text:
        st.error("No text found. The PDF may be image/scanned. Try a text-based PDF.")
        st.stop()

    with st.spinner("Parsing sections…"):
        data = parse_resume(raw_text)

    st.success(f"✅ Parsed **{uploaded.name}** successfully!")
    st.markdown("---")

    # ── NAME ──────────────────────────────────────────────────────────────────
    name = data["_name"]
    section_box("👤 Name", f'<p class="name-text">{name or "Not detected"}</p>')

    # ── CONTACT ───────────────────────────────────────────────────────────────
    cp = data["_contact"]
    contact_chips = ""
    for label, vals in cp.items():
        for v in vals:
            contact_chips += f'<span class="contact-chip">📌 {label}: {v}</span>'
    if contact_chips:
        section_box("📬 Contact", f'<div class="contact-row">{contact_chips}</div>')

    # ── SUMMARY ───────────────────────────────────────────────────────────────
    summary = [l for l in data.get("SUMMARY", []) if l]
    if summary:
        section_box("📝 Professional Summary", f'<p class="content-text">{chr(10).join(summary)}</p>')

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
            tags_html = "".join(f'<span class="skill-tag">{t}</span>' for t in tags)
            section_box("🛠️ Skills", tags_html)
        elif data.get("SKILLS"):
            section_box("🛠️ Skills", f'<p class="content-text">{chr(10).join(data["SKILLS"])}</p>')

        # EDUCATION
        edu = [l for l in data.get("EDUCATION", []) if l]
        if edu:
            entries = lines_to_entries(edu)
            html = ""
            for e in entries:
                html += '<div class="entry-block">'
                html += f'<div class="entry-title">{e[0]}</div>'
                for sub in e[1:]:
                    html += f'<div class="entry-body">{sub}</div>'
                html += "</div>"
            section_box("🎓 Education", html)

        # CERTIFICATIONS
        certs = [l for l in data.get("CERTIFICATIONS", []) if l]
        if certs:
            entries = lines_to_entries(certs)
            html = ""
            for e in entries:
                html += '<div class="entry-block">'
                html += f'<div class="entry-title">{e[0]}</div>'
                for sub in e[1:]:
                    html += f'<div class="entry-body">{sub}</div>'
                html += "</div>"
            section_box("🏅 Certifications", html)

        # ACHIEVEMENTS
        ach = [l for l in data.get("ACHIEVEMENTS", []) if l]
        if ach:
            html = "".join(f'<div class="entry-body">• {l}</div>' for l in ach)
            section_box("🏆 Achievements", html)

    with col2:
        # EXPERIENCE
        exp = [l for l in data.get("EXPERIENCE", []) if l]
        if exp:
            entries = lines_to_entries(exp)
            html = ""
            for e in entries:
                html += '<div class="entry-block">'
                html += f'<div class="entry-title">{e[0]}</div>'
                for sub in e[1:]:
                    html += f'<div class="entry-body">{sub}</div>'
                html += "</div>"
            section_box("💼 Work Experience", html)

        # INTERNSHIP
        intern = [l for l in data.get("INTERNSHIP", []) if l]
        if intern:
            entries = lines_to_entries(intern)
            html = ""
            for e in entries:
                html += '<div class="entry-block">'
                html += f'<div class="entry-title">{e[0]}</div>'
                for sub in e[1:]:
                    html += f'<div class="entry-body">{sub}</div>'
                html += "</div>"
            section_box("🏢 Internship", html)

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

        # ── Deduplicate: if resume project matches a GitHub repo, count as 1
        import difflib
        def normalize(s):
            return re.sub(r"[^a-z0-9]", "", s.lower())

        gh_normalized = [normalize(r["name"]) for r in gh_repos]
        resume_normalized = [normalize(n) for n in resume_proj_names]

        duplicates = 0
        for rn in resume_normalized:
            matches = difflib.get_close_matches(rn, gh_normalized, n=1, cutoff=0.7)
            if matches:
                duplicates += 1

        total_proj_count = resume_proj_count + github_proj_count - duplicates

        if proj_raw or gh_repos:
            # ── Stats bar ──────────────────────────────────────────────────
            st.markdown(f"""
            <div class="section-wrap">
            <div class="sec-title">🚀 Projects</div>
            <div class="proj-stats-bar">
                <div class="proj-stat-box">
                    <div class="proj-stat-num">📄 {resume_proj_count}</div>
                    <div class="proj-stat-label">Resume Projects</div>
                </div>
                <div class="proj-stat-divider"></div>
                <div class="proj-stat-box">
                    <div class="proj-stat-num">🐙 {github_proj_count}</div>
                    <div class="proj-stat-label">GitHub Repos</div>
                </div>
                <div class="proj-stat-divider"></div>
                <div class="proj-stat-box">
                    <div class="proj-stat-num">✨ {total_proj_count}</div>
                    <div class="proj-stat-label">Total Unique Projects</div>
                </div>
            </div>
            <div class="gh-divider">📋 All Project Names</div>
            </div>
            """, unsafe_allow_html=True)

            # ── Resume projects ─────────────────────────────────────────────
            for i, name_r in enumerate(resume_proj_names, 1):
                st.markdown(f"""
                <div style="display:flex;align-items:center;gap:0.6rem;
                            padding:0.55rem 0.8rem;margin-bottom:0.45rem;
                            background:#f1f5f9;border-radius:8px;
                            border-left:4px solid #6366f1;">
                    <span style="font-size:0.78rem;font-weight:700;color:#6366f1;min-width:24px;">#{i}</span>
                    <span style="font-size:0.88rem;color:#1e293b;font-weight:600;">📄 {name_r}</span>
                    <span style="margin-left:auto;font-size:0.72rem;background:#e0e7ff;
                                 color:#4338ca;border-radius:20px;padding:2px 10px;">Resume</span>
                </div>""", unsafe_allow_html=True)

            # ── GitHub repos ────────────────────────────────────────────────
            for j, repo in enumerate(gh_repos, resume_proj_count + 1):
                repo_url  = repo["url"]
                repo_name = repo["name"]
                repo_lang = repo.get("language") or ""
                # Build badges as a plain string — no nested HTML, no f-string conflicts
                badges = ""
                if repo_lang.strip():
                    badges += (
                        '<span style="font-size:0.72rem;background:#d1fae5;color:#065f46;'
                        f'border-radius:20px;padding:2px 8px;margin-right:4px;">{repo_lang}</span>'
                    )
                badges += (
                    '<span style="font-size:0.72rem;background:#d1fae5;color:#065f46;'
                    'border-radius:20px;padding:2px 10px;">GitHub</span>'
                )
                st.markdown(
                    '<div style="display:flex;align-items:center;gap:0.6rem;'
                    'padding:0.55rem 0.8rem;margin-bottom:0.45rem;'
                    'background:#f8fafc;border-radius:8px;border-left:4px solid #10b981;">'
                    f'<span style="font-size:0.78rem;font-weight:700;color:#10b981;min-width:24px;">#{j}</span>'
                    f'<a href="{repo_url}" target="_blank" '
                    'style="font-size:0.88rem;color:#1e293b;font-weight:600;text-decoration:none;">'
                    f'🐙 {repo_name}</a>'
                    f'<span style="margin-left:auto;display:flex;gap:0.3rem;align-items:center;">{badges}</span>'
                    '</div>',
                    unsafe_allow_html=True
                )

            if not gh_repos and gh_username:
                st.markdown('<p style="color:#ef4444;font-size:0.85rem;">⚠️ Could not fetch GitHub repos (private profile or API limit).</p>', unsafe_allow_html=True)

    # ── Raw text ──────────────────────────────────────────────────────────────
    with st.expander("📃 View Raw Extracted Text"):
        st.text(raw_text)

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
        # try to pick a stable id: GitHub username if present, else email, else name
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
        st.info(f"Saved parsed resume to {fname}")
    except Exception as e:
        st.warning(f"Could not save parsed resume: {e}")

    # ── MENTOR RATING PREDICTION ───────────────────────────────────────────
    st.markdown("---")
    st.markdown("## Mentor Rating Prediction")

    import os
    model_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mentor_model.pkl")
    try:
        with open(model_path, "rb") as f:
            ml_model = pickle.load(f)

        skills_count_ml   = len(data.get("_skill_tags", []))
        projects_count_ml = total_proj_count
        exp_lines_ml      = [l for l in data.get("EXPERIENCE", []) if l]
        experience_years  = max(1, len(exp_lines_ml) // 3)
        feedback_score    = 3.0  # default neutral for new mentor

        input_data = pd.DataFrame([{
            "experience_years": experience_years,
            "skills_count"    : skills_count_ml,
            "projects_count"  : projects_count_ml,
            "feedback_score"  : feedback_score
        }])

        predicted_rating = ml_model.predict(input_data)[0]
        predicted_rating = min(float(predicted_rating), 100.0)

        if predicted_rating >= 80:
            grade, color = "Excellent", "#10b981"
        elif predicted_rating >= 60:
            grade, color = "Good", "#6366f1"
        elif predicted_rating >= 40:
            grade, color = "Average", "#f59e0b"
        else:
            grade, color = "Poor", "#ef4444"

        st.markdown(f"""
        <div style="background:{color};border-radius:14px;padding:2rem;
                    text-align:center;margin-top:1rem;">
            <div style="font-size:3rem;font-weight:900;color:white;">{predicted_rating:.1f} / 100</div>
            <div style="font-size:1.4rem;color:white;font-weight:600;margin-top:0.5rem;">{grade} Mentor</div>
            <div style="font-size:0.85rem;color:rgba(255,255,255,0.8);margin-top:0.8rem;">
                Experience: {experience_years} yrs &nbsp;|&nbsp;
                Skills: {skills_count_ml} &nbsp;|&nbsp;
                Projects: {projects_count_ml}
            </div>
            <div style="font-size:0.75rem;color:rgba(255,255,255,0.6);margin-top:0.4rem;">
                Based on resume data only (no student feedback yet)
            </div>
        </div>
        """, unsafe_allow_html=True)

    except FileNotFoundError:
        st.error(f"mentor_model.pkl not found at: {model_path}")