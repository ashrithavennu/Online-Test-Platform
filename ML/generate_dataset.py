"""
EduAssess — Dataset Generator
Generates a realistic student exam performance dataset.
Run this once to create dataset.csv
"""

import pandas as pd
import numpy as np

np.random.seed(42)
n = 300  # 300 student exam records

# ── Generate features ─────────────────────────
scores       = np.random.normal(65, 18, n).clip(10, 100).round(1)
time_taken   = np.random.normal(35, 8, n).clip(10, 45).round(0).astype(int)
num_attempts = np.random.randint(1, 6, n)
past_score   = (scores + np.random.normal(0, 10, n)).clip(10, 100).round(1)

# ── Label based on rules (mirrors Decision Tree logic) ──
def label(score, time, attempts, past):
    if score >= 75:
        return 'Good Performer'
    elif score >= 50:
        return 'Average Performer'
    else:
        return 'Needs Improvement'

labels = [label(scores[i], time_taken[i], num_attempts[i], past_score[i])
          for i in range(n)]

df = pd.DataFrame({
    'score':        scores,
    'time_taken':   time_taken,
    'num_attempts': num_attempts,
    'past_score':   past_score,
    'performance':  labels
})

df.to_csv('dataset.csv', index=False)
print(f"Dataset created: {len(df)} records")
print(df['performance'].value_counts())
print(df.head())
