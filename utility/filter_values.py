import os
from collections import defaultdict
from typing import List
from pathlib import Path
import pandas as pd


def filter_values_between_start_end(values: List[int], start: int, end: int):
    return [value for value in values if start < value < end]


def append_results_to_csv(results, filename):
    df = pd.DataFrame([results])
    df.to_csv(filename, mode='a', header=not os.path.exists(filename), index=False)


def get_working_directory(filePath):
    # Split the filePath by '/' to separate directories and filename
    parts = filePath.split('/')

    # If the filePath contains more than one part, there are directories in the path
    if len(parts) > 1:
        # Return the directory path without the filename
        return "/".join(parts[:-1])
    else:
        # If there's only one part, the file is in the top directory, return the top directory
        # Assuming Unix-like file system, top directory is '/'
        # For Windows or other systems, you might need to adjust this
        return "/"


def filter_rows(rows, attrs):
    all_occurrences = {}
    duplicated_objects = []
    non_duplicated_objects = []

    for item in rows:
        # exclude the items having ""alias"" != "_"
        if ("alias" in item) and (item["alias"] == "_"):
            # print(item)
            unique_key_parts = [item[attr] for attr in attrs if attr in item]
            unique_key = tuple(unique_key_parts)

            if unique_key in all_occurrences:
                all_occurrences[unique_key].append(item)
            else:
                all_occurrences[unique_key] = [item]

    for unique_key, items in all_occurrences.items():
        if len(items) > 1:
            # print("unique_key ::", unique_key)
            duplicated_objects.extend(items)
        else:
            non_duplicated_objects.extend(items)

    # Group duplicated objects by name
    grouped_objects = group_by_name(duplicated_objects, "workingDirectory")

    filtered = []

    for name, objs in grouped_objects.items():
        selected_obj = select_from_group(objs)
        filtered.append(selected_obj)

    filtered.extend(non_duplicated_objects)
    return filtered


def select_from_group(objs):
    """
    Prioritizes objects based on defined conditions:
    - Prefers objects coming from Terraform blocks with operators.
    - Next, prefers any objects with operators.
    - Then, prioritize objects with specific sourceName and operator conditions.
    Returns the first object if no specific conditions are met.
    """
    # Check for preferred conditions
    for obj in objs:
        # Check if object comes from Terraform block and has an operator
        # if obj.get("isComingFromTerraformBlock") and obj.get("operator") != "_":
        # Check if object comes from Terraform block
        if obj.get("isComingFromTerraformBlock"):
            return obj

        # Check for objects with an operator
        elif obj.get("operator") != "_":
            # if obj.get("sourceName") == "_":
            return obj  # Prioritize objects with specific sourceName and operator

    # Fallback to the first object if none of the preferred conditions are met
    return objs[0] if objs else None


# Function to group objects by name
def group_by_name(objects, attr):
    grouped = defaultdict(list)
    for obj in objects:
        grouped[obj[attr]].append(obj)
    return grouped


def transform_path(input_path, commit_hash=None):
    # Convert the input path to a Path object for platform-independent manipulation
    path_obj = Path(input_path)

    # Convert the Path object to a list of parts
    parts = path_obj.parts

    # Check if the commit hash is in the path
    if commit_hash in parts:
        # Find the index of the commit hash
        commit_index = parts.index(commit_hash)

        # Keep the parts of the path after the commit hash
        desired_parts = parts[commit_index + 1:]

        # Create a new Path object from the desired parts and convert it to a string
        transformed_path = Path(*desired_parts).as_posix()  # as_posix() ensures forward slashes
        return transformed_path
    else:
        return path_obj.as_posix()


