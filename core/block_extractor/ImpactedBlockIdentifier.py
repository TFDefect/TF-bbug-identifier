from pydriller import ModificationType

from core.block_extractor.TerraMetricsLoader import TerraMetricsLoader
from core.change.Additions import Additions
from core.change.Deletions import Deletions


class ImpactedBlockIdentifier:

    def __init__(self, mod):
        self.mod = mod

        self.blockLocatorInstance = TerraMetricsLoader(self.mod)

        # status, data after the block changed
        after = self.blockLocatorInstance.call_service_locator(before=False)

        if after is not None:

            self.blocks_after_change = after["data"]
            self.status_after_change = after["status"]
            self.head_after_change = after["head"]
            self.num_lines_of_code_file_after_change = self.head_after_change["num_lines_of_code"]
            self.num_blocks_file_after_change = self.head_after_change["num_blocks"]

        else:
            self.blocks_after_change = []
            self.status_after_change = 404
            self.head_after_change = 0
            self.num_lines_of_code_file_after_change = 0
            self.num_blocks_file_after_change = 0


        # status, data before the block changed
        before = self.blockLocatorInstance.call_service_locator(before=True)

        if before is not None:
            self.blocks_before_change = before["data"]
            # print("before change :", self.blocks_before_change)

            self.status_before_change = before["status"]
            self.head_before_change = before["head"]
            self.num_lines_of_code_file_before_change = self.head_before_change["num_lines_of_code"]
            self.num_blocks_file_before_change = self.head_before_change["num_blocks"]

        else:
            self.blocks_before_change = []
            if self.mod.change_type == ModificationType.ADD:
                self.status_before_change = 200
            else:
                self.status_before_change = 404
            self.num_lines_of_code_file_before_change = 0
            self.num_blocks_file_before_change = 0

        # Get added and removed lines_change
        self.additions = Additions(self.mod)
        self.added_lines = self.additions.get_added_lines_in_a_file()
        self.added_lines_content = self.additions.get_added_lines_content_in_a_file()
        self.deletions = Deletions(self.mod)
        self.removed_lines = self.deletions.get_deleted_lines_in_a_file()

    def is_dict_in_list(self, target_dict, list_of_dicts):
        for d in list_of_dicts:
            if d["block_identifiers"] == target_dict["block_identifiers"]:
                return True
        return False

    def get_block(self, block, list_of_dicts):
        minDistance = float('inf')
        closestBlock = None

        for d in list_of_dicts:
            if block["block_identifiers"] == d["block_identifiers"]:
                distance = abs(block["start_block"] - d["start_block"])
                if distance <= minDistance:
                    minDistance = distance
                    closestBlock = d
        return closestBlock

    def is_block_exist(self, block, list_of_dicts):
        closestBlock = self.get_block(block, list_of_dicts)
        if closestBlock is not None:
            return True
        return False

    from typing import List, Dict

    def identify_impacted_blocks_in_a_file(self) -> List[Dict]:
        """
        Identifies impacted blocks in a file based on added and removed lines.

        Returns:
            List[Dict]: A list of impacted blocks, each represented as:
                {
                    "type": str,  # Type of change ("new", "fully_removed", "modified")
                    "block": dict  # The impacted block's data
                }
        """
        impacted_blocks = []

        # 1. Identify added blocks (new blocks that didn't exist before)
        for obj in self.blocks_after_change:
            if not self.is_block_exist(obj, self.blocks_before_change):
                impacted_blocks.append({"type": "new", "block": obj})

        # 2. Identify fully removed blocks
        for obj in self.blocks_before_change:
            if not self.is_block_exist(obj, self.blocks_after_change):
                impacted_blocks.append({"type": "fully_removed", "block": obj})

        # 3. Identify partially modified blocks
        for obj in self.blocks_after_change:
            for line in self.added_lines:
                if obj["start_block"] <= line <= obj["end_block"]:
                    if not self.is_dict_in_list(obj, impacted_blocks):
                        impacted_blocks.append({"type": "modified", "block": obj})

        # 4. Identify removed attributes within a block
        for ancientBlock in self.blocks_before_change:
            cpt = 0  # Counter for removed lines
            for line in self.removed_lines:
                if ancientBlock["start_block"] <= line <= ancientBlock["end_block"]:
                    cpt += 1

            # If all attributes were removed, classify as fully removed
            if cpt >= ancientBlock["numAttrs"]:
                impacted_blocks.append({"type": "fully_removed", "block": ancientBlock})
            elif ancientBlock["numAttrs"] > cpt >= 1:
                # If some attributes were removed but the block still exists, it's modified
                target_block = self.get_block(ancientBlock, self.blocks_after_change)
                if target_block is not None:
                    impacted_blocks.append({"type": "modified", "block": target_block})

        return impacted_blocks
