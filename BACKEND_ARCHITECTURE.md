# ResuMentor — Backend & Scoring Logic

This document explains what happens between "user uploads a PDF" and "user
sees a score" — the actual logic, not the UI.

---

## 1. Pipeline overview

```
 PDF upload
     │
     ▼
 [1] Text extraction        extract_text()      — pdfplumber, page by page
     │
     ▼
 [2] Section parsing        parse_resume()       — regex-based header detection
     │                                              (SUMMARY, SKILLS, EXPERIENCE,
     │                                               PROJECTS, EDUCATION, etc.)
     ▼
 [3] Feature extraction     — skills_count      (from detected skill tags)
     │                       — projects_count   (resume projects + GitHub repos,
     │                                            de-duplicated against each other)
     │                       — experience_years (real date-range parsing, e.g.
     │                                            "Jan 2023 – Present")
     ▼
 [4] Scoring formula        — weighted sum → 0–100 → stars/grade
     │
     ▼
 Displayed result
```

---

## 2. Stage-by-stage

### [1] Text extraction — `extract_text()`
Uses `pdfplumber` to pull raw text out of every page of the uploaded PDF.
If the PDF is a scanned image with no embedded text layer, this returns
empty and the app stops with an error — there is no OCR step.

### [2] Section parsing — `parse_resume()`
Splits the raw text into sections (Summary, Skills, Experience, Internship,
Projects, Education, Certifications, Achievements) by pattern-matching
common section headers. It also pulls out:
- **Name** — first non-empty, name-shaped line near the top
- **Contact info** — email/phone/LinkedIn/GitHub via regex
- **Skill tags** (`_skill_tags`) — individual skills split out of the
  Skills section (comma/pipe/bullet separated)

This is regex/heuristic-based, not ML — it will misfire on resumes with
unusual formatting (no clear section headers, skills embedded in prose,
non-English section titles, etc.).

### [3] Feature extraction
Three numbers feed the scoring formula:

| Feature | How it's derived |
|---|---|
| `skills_count` | Length of the skill tag list from step 2 |
| `projects_count` | Project entries detected in the resume's Projects section, **plus** repos pulled from the person's GitHub profile (if a GitHub link was found in contact info) — with a similarity check (`difflib`) to avoid double-counting a project that appears in both the resume and GitHub |
| `experience_years` | Actual date ranges (e.g. `Jan 2023 – Present`, `June 2025 - July 2025`) are regex-matched out of the Experience and Internship sections and summed in months, then converted to years. If no parseable date range exists but experience text is present, it falls back to a conservative estimate (0.5y for work experience, 0.25y for internship-only) rather than guessing a full year |

### [4] Scoring formula — the "model"
**Important: this is not a trained ML model.** It's a transparent, hand-set
weighted formula:

```
rating = (experience_years × 2)
       + (skills_count     × 1.5)
       + (projects_count   × 1.2)
       + (feedback_score   × 10)

rating = min(rating, 100)        # capped at 100
```

- `feedback_score` is currently **hardcoded to 3.0 (neutral)** for every
  resume — there's no real feedback data being collected yet, so this term
  always contributes a flat 30 points to everyone's score.
- The 0–100 result is converted to a 0–5 star display: `stars = rating / 20`
- Grade bands: **80+** → Strong Profile · **60–79** → Solid Profile ·
  **40–59** → Growing Profile · **below 40** → Early Stage

These weights (2 / 1.5 / 1.2 / 10) are **not learned from data** — they're
the same fixed weights defined in `Final Dataset.py`, carried into the live
app as-is.

---

## 3. About the XGBoost model in this repo (`Model.py`, `mentor_model.pkl`)

The repo also contains a proper trained ML pipeline:
- `Final Dataset.py` / `build_dataset.py` generate a synthetic training set
  (`final_dataset.csv`) using the same formula above, plus synthetic
  feedback text run through a keyword-based sentiment mapper (`Sentiment.py`)
- `Model.py` trains an `XGBoostRegressor` on that synthetic data and saves
  it as `mentor_model.pkl`

**This model is not used by the live app.** It was tried and dropped: it
was trained only on whole-number `experience_years` from 1–15 (i.e.
working professionals), so it had never seen fractional values like 0.17
years. Fed a student resume with a couple months of internship, it would
silently clamp to its nearest learned region and return a high score
regardless of actual experience — it effectively ignored experience for
anyone without a full year of it. The straightforward formula above has no
such blind spot, which is why `app.py` uses it directly instead of loading
the `.pkl` file.

If you want to explain this to your head as one line: **the "model" powering
the live score is a documented weighted formula, not the pickled XGBoost
model** — the ML pipeline exists in the repo but was superseded.

---

## 4. Known limitations worth flagging

- **Weights are heuristic, not fitted.** Nobody has validated that
  `experience×2 + skills×1.5 + projects×1.2` actually correlates with
  "good hire" or "good mentor" outcomes — they were picked, not learned.
- **`feedback_score` is always neutral (3.0).** Until there's a real
  feedback loop, ~30% of every score is a constant, which quietly
  compresses the effective spread between weak and strong resumes.
- **Section-header parsing is brittle.** Resumes with creative formatting,
  no clear headers, or a non-standard layout can under-detect skills/
  projects/experience, which directly lowers the score for reasons
  unrelated to resume quality.
- **Project de-duplication is approximate.** The GitHub/resume project
  matching uses fuzzy string similarity (`difflib`, cutoff 0.7) — it can
  both over-merge (different projects with similar names) and under-merge
  (same project named differently in each place).

---

## 5. Testing at scale

See `batch_test_resumes.py` — point it at a folder of resume PDFs and it
scores all of them in one run using the exact same functions as the live
app, and writes a CSV report. Useful for exactly this kind of "run it
against a bunch of real resumes and sanity-check the ratings" exercise.
