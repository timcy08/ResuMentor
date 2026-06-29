import pandas as pd
import numpy as np
import pickle
from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import mean_absolute_error, r2_score
from xgboost import XGBRegressor
import warnings
warnings.filterwarnings("ignore")


# Load data
df = pd.read_csv("final_dataset.csv")
print("Dataset shape:", df.shape)

# Features and target
features = ["experience_years", "skills_count", "projects_count", "feedback_score"]
X = df[features]
y = df["mentor_rating"]

# Train/test split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.15, random_state=42)

# Pipeline: scaler + xgb
pipe = Pipeline([
    ("scaler", StandardScaler()),
    ("xgb", XGBRegressor(objective='reg:squarederror', random_state=42))
])

param_dist = {
    'xgb__n_estimators': [50, 100, 200],
    'xgb__learning_rate': [0.01, 0.05, 0.1],
    'xgb__max_depth': [3, 4, 6],
    'xgb__subsample': [0.6, 0.8, 1.0],
    'xgb__colsample_bytree': [0.6, 0.8, 1.0]
}

rs = RandomizedSearchCV(pipe, param_distributions=param_dist, n_iter=10, cv=3, scoring='r2', random_state=42, n_jobs=-1)
print("Starting randomized search for hyperparameters...")
rs.fit(X_train, y_train)

print("Best params:", rs.best_params_)

# Evaluate
best = rs.best_estimator_
preds = best.predict(X_test)
mae = mean_absolute_error(y_test, preds)
r2 = r2_score(y_test, preds)

print(f"Test MAE: {mae:.3f}")
print(f"Test R2 : {r2:.3f}")

# Save pipeline
with open("mentor_model.pkl", "wb") as f:
    pickle.dump(best, f)

print("Saved pipeline to mentor_model.pkl")