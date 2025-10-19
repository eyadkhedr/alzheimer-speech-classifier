"""
Language-Independent Alzheimer’s Speech Classifier
--------------------------------------------------
This script trains a Random Forest model on combined acoustic and linguistic features
for multilingual Alzheimer’s detection. It outputs:
- A trained model saved to backend/models/dementia_model.pkl
- A list of selected features used during inference
- Evaluation metrics and visualizations (ROC, confusion matrices)
"""

# ==============================
# 1. Imports
# ==============================
import os
import pandas as pd
import numpy as np
from scipy.stats import ttest_ind
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (accuracy_score, precision_score, recall_score,
                             f1_score, confusion_matrix, classification_report,
                             roc_curve, auc)
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import matplotlib.pyplot as plt
import seaborn as sns
import joblib
import warnings
warnings.filterwarnings('ignore')

# ==============================
# 2. Helper Functions
# ==============================
def plot_confusion_matrix(y_true, y_pred, title, output_dir, cmap='Blues'):
    """Save confusion matrix plot"""
    cm = confusion_matrix(y_true, y_pred)
    plt.figure(figsize=(6, 4))
    sns.heatmap(cm, annot=True, fmt='d', cmap=cmap, xticklabels=['HC', 'AD'], yticklabels=['HC', 'AD'])
    plt.xlabel('Predicted Label')
    plt.ylabel('True Label')
    plt.title(title)
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{title.replace(' ', '_')}.png"))
    plt.close()

def plot_roc_curve(y_true, y_scores, title, output_dir):
    """Save ROC curve plot"""
    fpr, tpr, _ = roc_curve(y_true, y_scores)
    roc_auc = auc(fpr, tpr)
    plt.figure(figsize=(6, 4))
    plt.plot(fpr, tpr, color='darkorange', lw=2, label='AUC = {:.2f}'.format(roc_auc))
    plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
    plt.xlabel('False Positive Rate')
    plt.ylabel('True Positive Rate')
    plt.title(title)
    plt.legend(loc='lower right')
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, f"{title.replace(' ', '_')}.png"))
    plt.close()

# ==============================
# 3. Paths
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "../sample_data")
OUTPUT_DIR = os.path.join(BASE_DIR, "../backend/outputs")
MODEL_DIR = os.path.join(BASE_DIR, "../backend/models")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

acoustic_csv_files = [
    os.path.join(DATA_DIR, "Englsih_Acoustic_Features.csv"),
    os.path.join(DATA_DIR, "German_Acoustic_Features.csv"),
    os.path.join(DATA_DIR, "Mandarin_Acoustic_Features.csv"),
]

linguistic_csv_files = [
    os.path.join(DATA_DIR, "English_Linguistic_Features.csv"),
    os.path.join(DATA_DIR, "German_Linguistic_Features.csv"),
    os.path.join(DATA_DIR, "Mandarin_Linguistic_Features.csv"),
]

# ==============================
# 4. Load, Align, and Combine Datasets
# ==============================
datasets = []

for acoustic_file, ling_file in zip(acoustic_csv_files, linguistic_csv_files):
    if not (os.path.exists(acoustic_file) and os.path.exists(ling_file)):
        print(f"Missing files for pair: {acoustic_file} | {ling_file}")
        continue

    acoustic_df = pd.read_csv(acoustic_file).dropna().reset_index(drop=True)
    ling_df = pd.read_csv(ling_file).dropna().reset_index(drop=True)

    common_labels = set(acoustic_df['label'].unique()).intersection(set(ling_df['label'].unique()))
    if not common_labels:
        print(f"No common labels between {acoustic_file} and {ling_file}. Skipping.")
        continue

    combined_df = pd.DataFrame()
    for label in common_labels:
        num_a = acoustic_df[acoustic_df['label'] == label].shape[0]
        num_l = ling_df[ling_df['label'] == label].shape[0]
        min_samples = min(num_a, num_l)
        if min_samples == 0:
            continue

        a_sampled = acoustic_df[acoustic_df['label'] == label].sample(n=min_samples, random_state=42)
        l_sampled = ling_df[ling_df['label'] == label].sample(n=min_samples, random_state=42)

        a_sampled.reset_index(drop=True, inplace=True)
        l_sampled.reset_index(drop=True, inplace=True)

        a_features = a_sampled.drop(columns=['label', 'file_name'], errors='ignore')
        l_features = l_sampled.drop(columns=['label'], errors='ignore')

        a_features.fillna(a_features.median(), inplace=True)
        l_features.fillna(l_features.median(), inplace=True)

        combined_label_df = pd.concat([a_features, l_features], axis=1)
        combined_label_df['label'] = label
        combined_df = pd.concat([combined_df, combined_label_df], ignore_index=True)

    if not combined_df.empty:
        combined_df = combined_df.sample(frac=1, random_state=42).reset_index(drop=True)
        datasets.append(combined_df)

if not datasets:
    raise ValueError("No valid datasets loaded. Check file paths in sample_data/.")

# ==============================
# 5. Feature Preparation
# ==============================
combined_data = pd.concat(datasets, ignore_index=True)
features = combined_data.drop(columns=['label'], errors='ignore')
labels = combined_data['label'].map({'AD': 1, 'HC': 0})

features.fillna(features.median(), inplace=True)
scaler = StandardScaler()
features_scaled = scaler.fit_transform(features)
features_scaled_df = pd.DataFrame(features_scaled, columns=features.columns)

# Feature selection by Random Forest importance
rf_selector = RandomForestClassifier(random_state=42)
rf_selector.fit(features_scaled_df, labels)
importances = rf_selector.feature_importances_
feature_importance_df = pd.DataFrame({
    'feature': features.columns,
    'importance': importances
}).sort_values(by='importance', ascending=False)

TOP_N = 397
significant_features = feature_importance_df['feature'].iloc[:TOP_N].tolist()
print(f"Selected Top {TOP_N} Features")

# Save feature list
features_path = os.path.join(MODEL_DIR, "selected_features.txt")
with open(features_path, "w") as f:
    for feat in significant_features:
        f.write(f"{feat}\n")
print(f"Saved selected feature list to: {features_path}")

# ==============================
# 6. Train Model
# ==============================
train_df = datasets[0]
X_train = train_df.drop(columns=['label'], errors='ignore')
y_train = train_df['label'].map({'AD': 1, 'HC': 0})
X_train.fillna(X_train.median(), inplace=True)
X_train_scaled = scaler.transform(X_train)
X_train_selected = pd.DataFrame(X_train_scaled, columns=X_train.columns)[significant_features]

X_train_split, X_val_split, y_train_split, y_val_split = train_test_split(
    X_train_selected, y_train, test_size=0.2, stratify=y_train, random_state=42
)

model = RandomForestClassifier(random_state=42)
model.fit(X_train_split, y_train_split)
y_val_pred = model.predict(X_val_split)
y_val_proba = model.predict_proba(X_val_split)[:, 1]

val_accuracy = accuracy_score(y_val_split, y_val_pred)
val_f1 = f1_score(y_val_split, y_val_pred)
print(f"\nValidation Accuracy: {val_accuracy * 100:.2f}% | F1: {val_f1 * 100:.2f}%")

plot_confusion_matrix(y_val_split, y_val_pred, "Confusion Matrix - Validation", OUTPUT_DIR)
plot_roc_curve(y_val_split, y_val_proba, "ROC Curve - Validation", OUTPUT_DIR)

# ==============================
# 7. Test Across Other Languages
# ==============================
overall_y_true, overall_y_pred, overall_y_prob = [], [], []

for i, test_df in enumerate(datasets[1:], start=2):
    X_test = test_df.drop(columns=['label'], errors='ignore')
    y_test = test_df['label'].map({'AD': 1, 'HC': 0})
    X_test.fillna(X_test.median(), inplace=True)
    X_test_scaled = scaler.transform(X_test)
    X_test_selected = pd.DataFrame(X_test_scaled, columns=X_test.columns)[significant_features]

    y_pred = model.predict(X_test_selected)
    y_proba = model.predict_proba(X_test_selected)[:, 1]

    acc = accuracy_score(y_test, y_pred)
    f1 = f1_score(y_test, y_pred)
    print(f"\nDataset {i} → Accuracy: {acc*100:.2f}% | F1: {f1*100:.2f}%")

    plot_confusion_matrix(y_test, y_pred, f"Confusion Matrix - Dataset_{i}", OUTPUT_DIR)
    plot_roc_curve(y_test, y_proba, f"ROC Curve - Dataset_{i}", OUTPUT_DIR)

    overall_y_true.extend(y_test)
    overall_y_pred.extend(y_pred)
    overall_y_prob.extend(y_proba)

# ==============================
# 8. Final Model Save
# ==============================
model_path = os.path.join(MODEL_DIR, "dementia_model.pkl")
joblib.dump(model, model_path)
print(f"\nModel saved successfully at: {model_path}")
