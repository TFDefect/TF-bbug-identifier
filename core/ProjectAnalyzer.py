import os
import shutil
import stat
from typing import Optional, List

from git import Repo, GitCommandError
from pydriller import Repository
from pydriller.domain.commit import Commit

from core.block_extractor.ImpactedBlockIdentifier import ImpactedBlockIdentifier


class ProjectAnalyzer:
    """
    A class to analyze a given Git repository, specifically focusing on Terraform (.tf) file modifications.
    This class supports cloning a repository, retrieving commit modifications, identifying changed blocks,
    and cleaning up cloned repositories.

    Attributes:
        projectName (str): The name of the project being analyzed.
        modelName (str): A sanitized version of the project name used for local storage.
        repo_url (str): The remote URL of the Git repository.
        local_repo_path (str): The local path where the repository is stored.
        clone_repo (bool): Indicates whether the repository should be cloned.
        file_ext_to_parse (List[str]): The list of file extensions to analyze (default: ["tf"]).
        test_special_commit (Optional[str]): An optional commit hash for testing.
    """

    def __init__(
            self,
            projectName: str,
            repo_url: str,
            local_repo_path: str,
            test_special_commit: Optional[str] = None,
            clone_repo: bool = False,
            file_ext_to_parse: List[str] = ["tf"]
    ):
        """
        Initializes the ProjectAnalyzer class with repository details and configurations.

        Args:
            projectName (str): The name of the project.
            repo_url (str): The URL of the remote repository.
            local_repo_path (str): The local directory path to store the repository.
            test_special_commit (Optional[str]): A commit hash for testing (default: None).
            clone_repo (bool): Whether to clone the repository (default: False).
            file_ext_to_parse (List[str]): List of file extensions to parse (default: ["tf"]).

        Raises:
            Exception: If `clone_repo` is False and the local repository does not exist.
        """
        self.projectName = projectName
        self.modelName = projectName.replace("/", "__")
        self.repo_url = repo_url
        self.local_repo_path = os.path.join(local_repo_path, self.modelName)
        self.clone_repo = clone_repo
        self.file_ext_to_parse = file_ext_to_parse
        self.test_special_commit = test_special_commit

        # Clone repository if required, otherwise verify the local path exists
        if self.clone_repo:
            self.clone_repository()
        elif not os.path.exists(self.local_repo_path):
            raise Exception(f"Local repository path {self.local_repo_path} does not exist.")

    def clone_repository(self) -> bool:
        """
        Clones the repository from the given remote URL if it does not already exist locally.

        Returns:
            bool: True if cloning is successful or if the repository already exists, False otherwise.
        """
        if not os.path.exists(self.local_repo_path):
            try:
                print(f"Cloning repository {self.repo_url} into {self.local_repo_path}...")
                Repo.clone_from(self.repo_url, self.local_repo_path, multi_options=["--no-checkout"])

                # Configure repo settings for compatibility with certain filesystems
                repo = Repo(self.local_repo_path)
                repo.git.config("core.protectNTFS", "false")

                return True
            except GitCommandError as e:
                print(f"GitCommandError cloning repository {self.local_repo_path}: {e}")
                return False
            except Exception as e:
                print(f"Error cloning repository {self.local_repo_path}: {e}")
                return False
        else:
            print(f"Repository {self.local_repo_path} already exists.")
            return True

    def remove_readonly(self, func, path: str, exc_info):
        """
        Removes the read-only attribute from a file and retries deletion.

        Args:
            func: The function to attempt deletion.
            path (str): The file path.
            exc_info: Exception information (ignored).
        """
        os.chmod(path, stat.S_IWRITE)
        func(path)

    def cleanup_repository(self):
        """
        Deletes the cloned repository from the local filesystem.
        """
        if os.path.exists(self.local_repo_path):
            print(f"Removing cloned repository at {self.local_repo_path}...")
            try:
                shutil.rmtree(self.local_repo_path, onerror=self.remove_readonly)
                print("Repository successfully removed.")
            except Exception as e:
                print(f"Failed to remove repository: {e}")

    def helper_function_get_specific_modification(self, commit_hash: str) -> Optional[Commit]:
        """
        Retrieves a specific commit from the repository based on its hash.

        Args:
            commit_hash (str): The hash of the commit to find.

        Returns:
            Optional[Commit]: The Commit object if found, otherwise None.
        """
        repo = Repository(path_to_repo=self.local_repo_path)

        for commit in repo.traverse_commits():
            if commit.hash == commit_hash:
                return commit  # Return the commit object if found

        return None  # Return None if commit is not found

    def identify_changed_blocks_from_a_tf_file(self, mod) -> List[dict]:
        """
        Identifies impacted code blocks in a modified Terraform file.

        Args:
            mod: A modified file object containing changes.

        Returns:
            List[dict]: A list of impacted code blocks in the file.
        """
        impactedBlockIdentifier = ImpactedBlockIdentifier(mod)
        return impactedBlockIdentifier.identify_impacted_blocks_in_a_file()

    def identify_changed_block_from_specific_commits(self, commit_hash: str) -> List[dict]:
        """
        Identifies changed blocks from a specific commit in the repository.

        Args:
            commit_hash (str): The hash of the commit to analyze.

        Returns:
            List[dict]: A list of dictionaries containing modified file paths and their changed blocks.
        """
        specificCommit = self.helper_function_get_specific_modification(commit_hash)
        if not specificCommit:
            print(f"Commit {commit_hash} not found.")
            return []

        all_changed_blocks_in_a_commit = []

        for modifiedFile in specificCommit.modified_files:
            impactedBlockPositions = self.identify_changed_blocks_from_a_tf_file(modifiedFile)
            currentObj = {
                "modifiedFilePath": modifiedFile.new_path,
                "itsChangedBlocks": impactedBlockPositions
            }
            all_changed_blocks_in_a_commit.append(currentObj)

        return all_changed_blocks_in_a_commit
