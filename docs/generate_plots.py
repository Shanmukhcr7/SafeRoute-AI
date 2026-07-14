import json
import matplotlib.pyplot as plt
import numpy as np

with open('models/evaluation/evaluation_report.json', 'r') as f:
    data = json.load(f)

# 1. Feature Importance Plot
feat_imp = data['feature_importance']
features = [x['feature'] for x in feat_imp]
importances = [x['importance'] for x in feat_imp]

plt.figure(figsize=(10, 6))
# Create bar plot manually
y_pos = np.arange(len(features))
plt.barh(y_pos, importances, align='center', color='teal')
plt.yticks(y_pos, features)
plt.gca().invert_yaxis()  # highest importance at the top
plt.title('Global Feature Importance (Permutation)')
plt.xlabel('Importance')
plt.tight_layout()
plt.savefig('docs/assets/feature_importance.png')
plt.close()

# 2. ROC Curve
roc = data['roc_fatal']
fpr = roc['fpr']
tpr = roc['tpr']
auc = roc['auc']

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'ROC curve (AUC = {auc:.3f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('Receiver Operating Characteristic (ROC) - Fatal vs Non-Fatal')
plt.legend(loc="lower right")
plt.tight_layout()
plt.savefig('docs/assets/roc_curve.png')
plt.close()

# 3. Confusion Matrix
cm = np.array(data['confusion_matrix'])
plt.figure(figsize=(6, 5))

# Plot matrix using matshow
cax = plt.matshow(cm, cmap='Blues')
plt.colorbar(cax)

for (i, j), z in np.ndenumerate(cm):
    plt.text(j, i, '{:d}'.format(z), ha='center', va='center')

plt.xticks([0, 1], ['Non-Severe', 'Severe'])
plt.yticks([0, 1], ['Non-Severe', 'Severe'])
plt.ylabel('Actual Label')
plt.xlabel('Predicted Label')
plt.title('Confusion Matrix', pad=20)
plt.tight_layout()
plt.savefig('docs/assets/confusion_matrix.png')
plt.close()

print("Plots successfully generated in docs/assets/")
