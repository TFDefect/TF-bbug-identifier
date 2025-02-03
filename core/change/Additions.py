from pydriller import ModifiedFile
from utility.TerraformSpecialCases import UtilityChange
from utility.filter_values import filter_values_between_start_end


class Additions:
    """
    Represents additions in a modified file within a repository, providing detailed information
    about the added lines, including their content and location within the file.

    Attributes:
        mod (ModifiedFile): An instance of ModifiedFile from PyDriller representing the modified file.
        start (int): The starting line number of a block of interest within the file. Defaults to 0.
        end (int): The ending line number of a block of interest within the file. Defaults to 0.
        utility (UtilityChange): An instance of UtilityChange for utility operations on changes.
        added_lines_content (List[str]): Content of the lines that have been added, with special lines excluded.
        added_lines (List[int]): Line numbers of the lines that have been added.
    """

    def __init__(self, mod: ModifiedFile, start=0, end=0):
        """
        Initializes the Additions object with a ModifiedFile instance and optionally a specific block within the file.

        Args:
            mod (ModifiedFile): The modified file instance from PyDriller.
            start (int, optional): The start line number of the block. Defaults to 0.
            end (int, optional): The end line number of the block. Defaults to 0.
        """
        self.mod = mod
        self.start = start
        self.end = end
        self.utility = UtilityChange()
        # Extract and store the content of added lines, excluding special lines like comments or whitespace.
        self.added_lines_content = self.utility.exclude_special_lines(self.mod.diff_parsed['added'])
        # Extract just the line numbers of the added lines.
        self.added_lines = [added[0] for added in self.added_lines_content]

    def get_added_lines_in_a_file(self):
        """
        Retrieves the line numbers of all added lines in the modified file.

        Returns:
            List[int]: A list of integers representing the line numbers of added lines.
        """
        return self.added_lines

    def get_added_lines_content_in_a_file(self):
        """
        Retrieves the content of all added lines in the modified file, excluding special lines.

        Returns:
            List[str]: A list of strings representing the content of added lines.
        """
        return self.added_lines_content

    def get_added_lines_in_a_block(self):
        """
        Retrieves the line numbers of added lines within a specified block of the file.

        Returns:
            List[int]: A list of integers representing the line numbers of added lines within the specified block.
        """
        return filter_values_between_start_end(self.added_lines, self.start, self.end)

    def count_added_lines_in_a_block(self):
        """
        Counts the number of added lines within a specified block of the file.

        Returns:
            int: The number of added lines within the specified block.
        """
        return len(self.get_added_lines_in_a_block())
