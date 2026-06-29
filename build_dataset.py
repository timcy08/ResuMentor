import os
import json
import glob
import time
import requests
import pandas as pd
from tqdm import tqdm

# Configuration
WORKDIR = os.path.dirname(os.path.abspath(__file__))
PARSED_DIR = os.path.join(WORKDIR, "parsed_resumes")  # optional folder where parsed resume JSONs are stored
FEEDBACK_CSV = os.path.join(WORKDIR, "synthetic_feedback.csv")
OUTPUT_CSV = os.path.join(WORKDIR, "final_dataset.csv")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")  # optional for higher rate limits

# Helpers

def load_feedback():
    if not os.path.exists(FEEDBACK_CSV):
        print("Feedback CSV not found:", FEEDBACK_CSV)
        return pd.DataFrame(columns=["mentor_id", "feedback_score"])
    df = pd.read_csv(FEEDBACK_CSV)
    if "score" not in df.columns:
        # map sentiments to scores
        score_map = {"Positive": 5, "Neutral": 3, "Negative": 1}
        df['score'] = df['sentiment'].map(score_map)
    # average per mentor
    out = df.groupby('mentor_id')['score'].mean().reset_index()
    out.columns = ["mentor_id", "feedback_score"]
    return out


def load_parsed_resumes():
    # parsed JSONs should contain: mentor_id (optional), skills (list), projects (list), experience (years or text)
    if not os.path.exists(PARSED_DIR):
        print("Parsed resumes directory not found:", PARSED_DIR)
        return pd.DataFrame(columns=["mentor_id", "skills_count", "projects_count", "experience_years"])

    rows = []
    for f in glob.glob(os.path.join(PARSED_DIR, "*.json")):
        try:
            with open(f, 'r', encoding='utf-8') as fh:
                d = json.load(fh)
            mentor_id = d.get('mentor_id') or os.path.splitext(os.path.basename(f))[0]
            skills = d.get('skills', []) or []
            projects = d.get('projects', []) or []
            exp = d.get('experience_years') or d.get('experience') or None
            # try to normalize experience
            if isinstance(exp, str):
                # crude attempt to extract year numbers
                import re
                yrs = re.findall(r"(\d+(?:\.\d+)?)\s*(?:yrs|years|year)", exp, re.I)
                if yrs:
                    exp_val = float(yrs[0])
                else:
                    exp_val = None
            else:
                exp_val = float(exp) if exp is not None else None

            rows.append({
                "mentor_id": mentor_id,
                "skills_count": len(skills),
                "projects_count": len(projects),
                "experience_years": exp_val
            })
        except Exception as e:
            print("Error reading parsed resume", f, e)
    return pd.DataFrame(rows)


def fetch_github_metrics(username):
    # returns dict with repo_count and stars_total
    headers = {"Accept": "application/vnd.github+json"}
    if GITHUB_TOKEN:
        headers['Authorization'] = f"token {GITHUB_TOKEN}"
    try:
        url = f"https://api.github.com/users/{username}/repos?per_page=100"
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code != 200:
            return {"github_repos": 0, "github_stars": 0}
        repos = r.json()
        repo_count = len([rr for rr in repos if not rr.get('fork')])
        stars = sum(rr.get('stargazers_count', 0) for rr in repos)
        return {"github_repos": repo_count, "github_stars": stars}
    except Exception:
        return {"github_repos": 0, "github_stars": 0}


# Build

def build(final_output=OUTPUT_CSV):
    print("Loading feedback...")
    df_fb = load_feedback()

    print("Loading parsed resumes (if any)...")
    df_parsed = load_parsed_resumes()

    # Start with parsed data
    if df_parsed.empty:
        print("No parsed resumes found; creating dataset from feedback + synthetic/random features as fallback.")
        # fallback: use existing synthetic pipeline (like original Final Dataset.py)
        df = pd.read_csv(FEEDBACK_CSV)
        # compute avg per mentor
        score_map = {"Positive": 5, "Neutral": 3, "Negative": 1}
        df['score'] = df['sentiment'].map(score_map)
        mentor_scores = df.groupby('mentor_id')['score'].mean().reset_index()
        mentor_scores.columns = ["mentor_id", "feedback_score"]

        import random
        random.seed(42)
        rows = []
        for _, r in mentor_scores.iterrows():
            mentor_id = r['mentor_id']
            experience_years = random.randint(1, 15)
            skills_count = random.randint(3, 20)
            projects_count = random.randint(1, 25)
            feedback_score = r['feedback_score']
            mentor_rating = round((experience_years * 2) + (skills_count * 1.5) + (projects_count * 1.2) + (feedback_score * 10), 2)
            mentor_rating = min(mentor_rating, 100)
            rows.append([mentor_id, experience_years, skills_count, projects_count, feedback_score, mentor_rating])
        df_final = pd.DataFrame(rows, columns=["mentor_id","experience_years","skills_count","projects_count","feedback_score","mentor_rating"])
        df_final.to_csv(final_output, index=False)
        print("Wrote fallback dataset to", final_output)
        return df_final

    # Merge parsed with feedback
    df = df_parsed.merge(df_fb, how='left', on='mentor_id')

    # Fill missing experience with median
    if 'experience_years' in df.columns:
        med = df['experience_years'].median()
        df['experience_years'] = df['experience_years'].fillna(med if not pd.isna(med) else 1)
    else:
        df['experience_years'] = 1

    # Fill missing feedback_score with neutral 3
    df['feedback_score'] = df['feedback_score'].fillna(3.0)

    # Add GitHub metrics (try to extract username from parsed file name or mentor_id)
    df['github_repos'] = 0
    df['github_stars'] = 0

    for idx, row in tqdm(df.iterrows(), total=len(df), desc="Fetching GitHub metrics", disable=True):
        mentor_id = row['mentor_id']
        # guess username = mentor_id lowercased without MT prefix
        guess = str(mentor_id).lower().replace('mt','')
        metrics = fetch_github_metrics(guess)
        df.at[idx, 'github_repos'] = metrics['github_repos']
        df.at[idx, 'github_stars'] = metrics['github_stars']
        time.sleep(0.1)

    # Compute mentor_rating using formula from doc (Experience 40%, Skills 30%, Projects 20%, Feedback 10%)
    # Normalize features first to a 0-100 scale using simple mins and maxs
    def scale_series(s, new_min=0, new_max=100):
        if s.max() == s.min():
            return pd.Series([50]*len(s), index=s.index)
        return ((s - s.min()) / (s.max() - s.min())) * (new_max - new_min) + new_min

    s_exp = scale_series(df['experience_years'])
    s_sk  = scale_series(df['skills_count'])
    s_proj= scale_series(df['projects_count'])
    s_feed= scale_series(df['feedback_score'])

    df['mentor_rating'] = (s_exp * 0.4) + (s_sk * 0.3) + (s_proj * 0.2) + (s_feed * 0.1)
    df['mentor_rating'] = df['mentor_rating'].round(2)

    # Save final
    output_cols = ['mentor_id','experience_years','skills_count','projects_count','github_repos','github_stars','feedback_score','mentor_rating']
    df_out = df[output_cols]
    df_out.to_csv(final_output, index=False)
    print("Wrote merged dataset to", final_output)
    return df_out


if __name__ == '__main__':
    df_res = build()
    print(df_res.head())
