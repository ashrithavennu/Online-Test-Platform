"""
EduAssess — ML Module
Task: Student Performance Prediction
Algorithm: Decision Tree Classifier
"""

# ══════════════════════════════════════════════
# STEP 1 — IMPORTS
# ══════════════════════════════════════════════
import pandas as pd
import numpy as np
import pickle
import os
from sklearn.tree import DecisionTreeClassifier, export_text, plot_tree
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import (accuracy_score, classification_report,
                             confusion_matrix, ConfusionMatrixDisplay)
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

print("=" * 55)
print("   EduAssess — Student Performance Prediction ML")
print("   Algorithm: Decision Tree Classifier")
print("=" * 55)

# ══════════════════════════════════════════════
# STEP 2 — LOAD DATASET
# ══════════════════════════════════════════════
print("\n📂 STEP 1: Loading Dataset...")

script_dir = os.path.dirname(os.path.abspath(__file__))
df = pd.read_csv(os.path.join(script_dir, 'dataset.csv'))

print(f"   Total records : {len(df)}")
print(f"   Columns       : {list(df.columns)}")
print(f"\n   Class distribution:")
print(df['performance'].value_counts().to_string())

# ══════════════════════════════════════════════
# STEP 3 — PREPROCESSING & ENCODING
# ══════════════════════════════════════════════
print("\n⚙️  STEP 2: Preprocessing & Encoding...")

# Feature columns
FEATURES = ['score', 'time_taken', 'num_attempts', 'past_score']
TARGET   = 'performance'

X = df[FEATURES]
y = df[TARGET]

# Encode labels → numbers
le = LabelEncoder()
y_encoded = le.fit_transform(y)

print(f"   Label mapping:")
for cls, idx in zip(le.classes_, le.transform(le.classes_)):
    print(f"     {idx} → {cls}")

# Check for missing values
print(f"   Missing values: {X.isnull().sum().sum()}")
print(f"   Feature stats:")
print(X.describe().round(2).to_string())

# ══════════════════════════════════════════════
# STEP 4 — TRAIN / TEST SPLIT
# ══════════════════════════════════════════════
print("\n✂️  STEP 3: Train/Test Split (80/20)...")

X_train, X_test, y_train, y_test = train_test_split(
    X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
)

print(f"   Training samples : {len(X_train)}")
print(f"   Testing  samples : {len(X_test)}")

# ══════════════════════════════════════════════
# STEP 5 — TRAIN DECISION TREE
# ══════════════════════════════════════════════
print("\n🌳 STEP 4: Training Decision Tree Classifier...")

model = DecisionTreeClassifier(
    max_depth        = 5,
    min_samples_split= 10,
    min_samples_leaf = 5,
    random_state     = 42,
    criterion        = 'gini'
)
model.fit(X_train, y_train)

print("   Model trained successfully!")
print(f"   Tree depth    : {model.get_depth()}")
print(f"   Tree leaves   : {model.get_n_leaves()}")
print(f"   Features used : {FEATURES}")

# Feature importance
print("\n   Feature Importances:")
for feat, imp in sorted(zip(FEATURES, model.feature_importances_),
                         key=lambda x: -x[1]):
    bar = '█' * int(imp * 40)
    print(f"     {feat:<15} {imp:.4f}  {bar}")

# ══════════════════════════════════════════════
# STEP 6 — EVALUATION
# ══════════════════════════════════════════════
print("\n📊 STEP 5: Model Evaluation...")

y_pred = model.predict(X_test)
acc    = accuracy_score(y_test, y_pred)

print(f"\n   ✅ Test Accuracy : {acc * 100:.2f}%")

# Cross-validation
cv_scores = cross_val_score(model, X, y_encoded, cv=5, scoring='accuracy')
print(f"   ✅ CV Accuracy   : {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")

print("\n   Classification Report:")
print(classification_report(y_test, y_pred,
      target_names=le.classes_, digits=4))

# Confusion Matrix
print("   Confusion Matrix:")
cm = confusion_matrix(y_test, y_pred)
print(cm)

# ══════════════════════════════════════════════
# STEP 7 — SAVE VISUALISATIONS
# ══════════════════════════════════════════════
print("\n🎨 STEP 6: Saving Visualisations...")

fig, axes = plt.subplots(1, 3, figsize=(20, 6))
fig.suptitle('EduAssess — Decision Tree Model Analysis', fontsize=14, fontweight='bold')

# (a) Confusion Matrix
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=le.classes_)
disp.plot(ax=axes[0], colorbar=False, cmap='Blues')
axes[0].set_title('Confusion Matrix')
axes[0].tick_params(axis='x', rotation=15)

# (b) Feature Importance
feat_imp = pd.Series(model.feature_importances_, index=FEATURES).sort_values()
axes[1].barh(feat_imp.index, feat_imp.values,
             color=['#4f8ef7','#7c3aed','#06b6d4','#10b981'])
axes[1].set_title('Feature Importances')
axes[1].set_xlabel('Importance Score')

# (c) CV Scores
axes[2].bar(range(1, 6), cv_scores * 100, color='#4f8ef7', alpha=0.8)
axes[2].axhline(cv_scores.mean() * 100, color='red', linestyle='--',
                label=f'Mean: {cv_scores.mean()*100:.1f}%')
axes[2].set_title('Cross-Validation Accuracy')
axes[2].set_xlabel('Fold')
axes[2].set_ylabel('Accuracy (%)')
axes[2].legend()
axes[2].set_ylim(0, 110)

plt.tight_layout()
plot_path = os.path.join(script_dir, 'model_analysis.png')
plt.savefig(plot_path, dpi=150, bbox_inches='tight')
plt.close()
print(f"   Saved: model_analysis.png")

# Decision Tree visualisation
fig2, ax2 = plt.subplots(figsize=(20, 10))
plot_tree(model, feature_names=FEATURES,
          class_names=le.classes_,
          filled=True, rounded=True, ax=ax2,
          fontsize=9)
ax2.set_title('Decision Tree Structure', fontsize=14, fontweight='bold')
plt.tight_layout()
tree_path = os.path.join(script_dir, 'decision_tree.png')
plt.savefig(tree_path, dpi=120, bbox_inches='tight')
plt.close()
print(f"   Saved: decision_tree.png")

# ══════════════════════════════════════════════
# STEP 8 — SAVE MODEL (pickle)
# ══════════════════════════════════════════════
print("\n💾 STEP 7: Saving Model...")

model_data = {
    'model':          model,
    'label_encoder':  le,
    'features':       FEATURES,
    'accuracy':       acc,
    'cv_mean':        cv_scores.mean(),
    'classes':        list(le.classes_)
}

# Save in ML/ folder
ml_model_path = os.path.join(script_dir, 'model.pkl')
with open(ml_model_path, 'wb') as f:
    pickle.dump(model_data, f)
print(f"   Saved: ML/model.pkl")

# Also save in Backend/ml_model/ so Flask can load it
backend_model_dir = os.path.join(script_dir, '..', 'Backend', 'ml_model')
os.makedirs(backend_model_dir, exist_ok=True)
backend_model_path = os.path.join(backend_model_dir, 'model.pkl')
with open(backend_model_path, 'wb') as f:
    pickle.dump(model_data, f)
print(f"   Saved: Backend/ml_model/model.pkl")

# ══════════════════════════════════════════════
# STEP 9 — TEST PREDICTION
# ══════════════════════════════════════════════
print("\n🧪 STEP 8: Testing Predictions on Sample Data...")

test_cases = [
    {'score': 88, 'time_taken': 30, 'num_attempts': 2, 'past_score': 85, 'expected': 'Good Performer'},
    {'score': 62, 'time_taken': 38, 'num_attempts': 3, 'past_score': 60, 'expected': 'Average Performer'},
    {'score': 35, 'time_taken': 42, 'num_attempts': 5, 'past_score': 40, 'expected': 'Needs Improvement'},
    {'score': 91, 'time_taken': 25, 'num_attempts': 1, 'past_score': 88, 'expected': 'Good Performer'},
    {'score': 55, 'time_taken': 40, 'num_attempts': 4, 'past_score': 50, 'expected': 'Average Performer'},
]

print(f"\n   {'Score':>6} {'Time':>5} {'Att':>4} {'Past':>6}  {'Predicted':<22} {'Expected':<22} {'Match'}")
print("   " + "-" * 80)
all_correct = 0
for tc in test_cases:
    features = [[tc['score'], tc['time_taken'], tc['num_attempts'], tc['past_score']]]
    pred_idx  = model.predict(features)[0]
    pred      = le.inverse_transform([pred_idx])[0]
    proba     = model.predict_proba(features)[0]
    conf      = round(max(proba) * 100, 1)
    match     = '✅' if pred == tc['expected'] else '❌'
    if pred == tc['expected']:
        all_correct += 1
    print(f"   {tc['score']:>6} {tc['time_taken']:>5} {tc['num_attempts']:>4} {tc['past_score']:>6}  "
          f"{pred:<22} {tc['expected']:<22} {match} ({conf}%)")

print(f"\n   Sample Accuracy: {all_correct}/{len(test_cases)} correct")

# Print tree rules
print("\n🌳 Decision Tree Rules (text):")
tree_rules = export_text(model, feature_names=FEATURES)
# Show first 30 lines only
lines = tree_rules.split('\n')[:30]
print('\n'.join('   ' + l for l in lines))
print("   ...")

print("\n" + "=" * 55)
print("   ✅ ML Module Complete!")
print(f"   Model Accuracy  : {acc*100:.2f}%")
print(f"   CV Accuracy     : {cv_scores.mean()*100:.2f}%")
print(f"   Model saved to  : ML/model.pkl")
print(f"                   : Backend/ml_model/model.pkl")
print("=" * 55)
