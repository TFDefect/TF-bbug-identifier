import os
import random
import numpy as np
from sklearn.dummy import DummyClassifier

from core.ProjectAnalyzer import ProjectAnalyzer

if __name__ == '__main__':
    """
    This script initializes a ProjectAnalyzer instance, analyzes a specific commit, 
    identifies changed Terraform blocks while ignoring fully removed blocks, and predicts defects.
    """

    # Define repository details
    project = "TFDefect/trivial-tf-changes"  # Example repository for testing
    local_path = "clones"  # Directory where the repository is stored/cloned
    repo_url = f"https://github.com/{project}.git"  # Construct GitHub repository URL
    test_special_commit = None  # Placeholder for testing specific commits (if needed)

    # Initialize the ProjectAnalyzer without cloning (assumes the repo already exists locally)
    projectAnalyzer = ProjectAnalyzer(
        project, repo_url, local_path, test_special_commit=test_special_commit, clone_repo=False
    )

    # Define the commit hash to analyze
    commit_hash = "be6a5b2da67c9c208ed03301942a8db00af03104"

    # Identify changed blocks in the given commit
    changed_blocks = projectAnalyzer.identify_changed_block_from_specific_commits(commit_hash=commit_hash)

    # Define icons for each block type
    ICONS = {
        "new": "🆕",  # New block
        "modified": "✏️",  # Modified block
        "removed": "❌",  # Fully removed block
        "fully_removed": "🚫"  # Block exists but all attributes removed
    }

    # Extract features (for simplicity, we use the block length as a numeric feature)
    X = []
    y = []  # Dummy labels (randomly assigned for testing)

    for changed_file in changed_blocks:
        modified_file_path = changed_file["modifiedFilePath"]
        impacted_blocks = changed_file["itsChangedBlocks"]

        # Filter out fully removed blocks
        filtered_blocks = [block for block in impacted_blocks if block["type"] != "fully_removed"]

        # Process each block
        for block in filtered_blocks:
            block_type = block["type"]
            block_data = block["block"]

            # Convert block attributes to a numerical feature (length of the block)
            block_size = block_data["loc"]

            X.append([block_size])  # Use block size as a simple feature
            y.append(random.choice([0, 1]))  # Dummy labels (0: non-defect, 1: defect)

    # Convert lists to NumPy arrays for sklearn compatibility
    X = np.array(X)
    y = np.array(y)

    # Train a DummyClassifier
    dummy_clf = DummyClassifier(strategy="stratified", random_state=42)
    # train the module
    dummy_clf.fit(X, y)

    # Predict defectiveness for changed blocks
    predictions = dummy_clf.predict(X)

    # Output the identified changed blocks with defect predictions
    print(f"\n📌 Impacted Terraform Blocks in Commit: {commit_hash}")

    index = 0
    for changed_file in changed_blocks:
        modified_file_path = changed_file["modifiedFilePath"]
        impacted_blocks = changed_file["itsChangedBlocks"]

        # Filter out fully removed blocks
        filtered_blocks = [block for block in impacted_blocks if block["type"] != "fully_removed"]

        # If there are any remaining blocks after filtering, print them
        if filtered_blocks:

            print(f"\n📂 Changed TF File: {modified_file_path}")

            for block in filtered_blocks:
                block_type = block["type"]
                block_data = block["block"]
                icon = ICONS.get(block_type, "🔹")  # Default icon if type is unknown
                defect_label = "🐞 Defective" if predictions[index] == 1 else "✅ Clean"

                print(f"  {icon} {block_type.capitalize()} Block → {block_data['block'] + ' ' + block_data['block_name'] } | {defect_label}")
                index += 1
