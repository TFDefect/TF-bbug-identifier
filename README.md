# TerraMetrics-In-Action Documentation 📖

## Overview 🚀
This documentation provides a step-by-step guide on how to use the `core.ProjectAnalyzer` class for analyzing Terraform changes in a Git repository. The script processes changed blocks, applies a simple defect prediction model, and presents the results.

## Prerequisites ⚙️
Before running the script, ensure you have the required dependencies installed.

### Install Dependencies 📦
Run the following command to install all necessary Python packages:
```bash
pip install -r requirements.txt
```

### Dependencies in `requirements.txt` 📜
- GitPython
- PyDriller
- Scikit-learn
- NumPy

## Steps to Run the Analysis 🔍

### 1️⃣ Initialize the Repository
The script initializes the `ProjectAnalyzer` instance, which allows analyzing Terraform (`.tf`) files in a given repository.

```python
project = "TFDefect/trivial-tf-changes"  # Example repository for testing
local_path = "clones"  # Directory where the repository is stored/cloned
repo_url = f"https://github.com/{project}.git"  # Construct GitHub repository URL

projectAnalyzer = ProjectAnalyzer(
    project, repo_url, local_path, test_special_commit=None, clone_repo=False
)
```
📌 **Note:** Set `clone_repo=True` if you need to clone the repository before analysis.

### 2️⃣ Select a Commit to Analyze 🏷️
The script requires a commit hash to analyze Terraform changes:

```python
commit_hash = "be6a5b2da67c9c208ed03301942a8db00af03104"
changed_blocks = projectAnalyzer.identify_changed_block_from_specific_commits(commit_hash=commit_hash)
```

### 3️⃣ Extract Features for Defect Prediction 🤖
The script extracts changed blocks within a TF file, then it identifies for each one the block size (i.e., as feature, metric) and assigns a random defect labels to simulate:

```python
X = []  # Feature matrix
y = []  # Labels

for changed_file in changed_blocks:
    impacted_blocks = changed_file["itsChangedBlocks"]
    filtered_blocks = [block for block in impacted_blocks if block["type"] != "fully_removed"]
    
    for block in filtered_blocks:
        block_size = block["block"]["loc"]  # Extract length of the block
        X.append([block_size])
        y.append(random.choice([0, 1]))  # Random defect label
```

 🛠️ Feature extraction is crucial for training any machine learning model. In this script:

**Block Size (loc)**: The length of the modified block is used as the primary feature.

**Filtering Fully Removed Blocks**: Blocks that are completely removed are ignored.

**Random Labels**: Since this is a dummy model, labels are randomly assigned as either 0 (non-defect) or 1 (defect).

**NumPy Conversion**: The extracted features are converted into NumPy arrays for compatibility with machine learning models.

### 4️⃣ Train a Dummy Model 🎯
The script trains a `DummyClassifier` (a basic/trivial machine learning model used as preliminary prototype) to simulate defect prediction:

```python
from sklearn.dummy import DummyClassifier
import numpy as np

X = np.array(X)
y = np.array(y)

dummy_clf = DummyClassifier(strategy="stratified", random_state=42)
dummy_clf.fit(X, y)
```

### 5️⃣ Predict Defectiveness of Changed Blocks 🐞
The script predicts whether each changed block is defective or clean:

```python
predictions = dummy_clf.predict(X)
```

### 6️⃣ Display Results 📊
The script outputs Terraform files and their modified blocks along with defect predictions:

```python
ICONS = {
    "new": "🆕",  # New block
    "modified": "✏️",  # Modified block
    "removed": "❌",  # Fully removed block
    "fully_removed": "🚫"  # Block exists but all attributes removed
}

for changed_file in changed_blocks:
    modified_file_path = changed_file["modifiedFilePath"]
    impacted_blocks = changed_file["itsChangedBlocks"]
    filtered_blocks = [block for block in impacted_blocks if block["type"] != "fully_removed"]
    
    if filtered_blocks:
        print(f"\n📂 Changed TF File: {modified_file_path}")
        for index, block in enumerate(filtered_blocks):
            block_type = block["type"]
            block_data = block["block"]
            icon = ICONS.get(block_type, "🔹")
            defect_label = "🐞 Defective" if predictions[index] == 1 else "✅ Clean"
            print(f"  {icon} {block_type.capitalize()} Block → {block_data['block']} {block_data['block_name']} | {defect_label}")
```

## Example Output 📝
```
📌 Impacted Terraform Blocks in Commit: be6a5b2da67c9c208ed03301942a8db00af03104

📂 Changed TF File: modules/network/main.tf
  ✏️ Modified Block → resource azurerm_virtual_network my_vnet | 🐞 Defective
  🆕 New Block → module subnet my_subnet | ✅ Clean
```

## Summary 📢
- The script analyzes Terraform (`.tf`) files in a Git repository.
- Extracts changed blocks while ignoring fully removed ones.
- Uses a simple machine learning model to predict defects.
- Outputs results with intuitive icons.

---
✅ **You're now ready to analyze Terraform changes in a repository!** 🚀

