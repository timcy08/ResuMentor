# ResuMentor 🎯

AI-powered Resume Parser & Mentor Evaluator — analyzes resumes and gives mentor-style feedback to help improve them.

## Features
- Parses resume content
- Evaluates resume quality using a trained ML model
- Gives feedback/suggestions to improve the resume

## Tech Stack
- Python
- Streamlit
- Scikit-learn (model: `mentor_model.pkl`)

## How to Run

```bash
git clone https://github.com/timcy08/ResuMentor.git
cd ResuMentor
pip install -r requirements.txt
streamlit run app.py
```

App opens at `http://localhost:8501`

## Files
- `app.py` — main Streamlit app
- `build_dataset.py`, `random_data.py` — dataset creation scripts
- `final_dataset.csv`, `synthetic_feedback.csv` — data used
- `mentor_model.pkl` — trained model

## Author
Navya Sharma ([@timcy08](https://github.com/timcy08))
