import json
import subprocess

from pydriller import ModifiedFile


class TerraMetricsLoader:

    def __init__(self, mod: ModifiedFile):
        self.mod = mod
        self.tmp = "tmp"
        self.target = self.tmp + "/code_metrics.json"
        self.service_locator_jar_path = self.tmp + "/terrametrics_2.2.2.jar"
        self.tmp_blob_path_after_change = self.tmp + "/temporary_file_after_change.tf"
        self.tmp_blob_path_before_change = self.tmp + "/temporary_file_before_change.tf"

    def get_content_file(self, before):
        if before:
            return self.mod.source_code_before
        return self.mod.source_code

    def write_blob_to_file(self, file_path, blob):
        with open(file_path, "wb") as file:
            file.truncate(0)
            file.write(blob.encode('utf-8'))
        return file_path

    def save_blob_tmp(self, before):
        blob = self.get_content_file(before)
        if blob is not None:
            if before:
                return self.write_blob_to_file(self.tmp_blob_path_before_change, blob)
            else:
                return self.write_blob_to_file(self.tmp_blob_path_after_change, blob)
        return None

    def call_service_locator(self, before):
        try:
            # Prepare the command to measure the metrics
            tempPath = self.save_blob_tmp(before)

            # print(self.read_blob_from_file(tempPath))
            if tempPath is None:
                return None

            # prepare the command to be executed
            print("🔄 Preparing command...")
            command, args = self.prepareCommand(before)

            if not command or not args.get("target"):
                raise ValueError("❌ Invalid command or missing target argument")

            print(f"🚀 Executing command: {' '.join(command)}")

            # Run the command and capture output
            process = subprocess.run(command, capture_output=True, text=True)

            # Debug subprocess output
            if process.returncode != 0:
                print(f"❌ Error executing service locator: {process.stderr}")
                return None

            print("✅ Command executed successfully, retrieving results...")

            # Get the results as JSON
            results = self.getJsonObjects(args["target"])

            # if results:
            #     print("📌 Results Retrieved:")
            #     print(json.dumps(results, indent=4))  # Pretty-print JSON results
            # else:
            #     print("⚠️ No results found or JSON file is empty.")

            # Clean up temporary files
            # self.clean_file(self.tmp_blob_path_after_change)
            # self.clean_file(self.tmp_blob_path_before_change)
            # self.clean_file(self.target)

            return results
        except Exception as e:
            print(f"❌ Error in call_service_locator: {e}")
            return None

    def clean_file(self, file_path):
        # Open the file in write mode, which truncates its content
        with open(file_path, "wb") as file:
            file.truncate(0)

    def getJsonObjects(self, path: str):
        # Read and parse the JSON file
        with open(path, 'r') as file:
            try:
                self.positions = json.load(file)
                return self.positions
            except json.JSONDecodeError as e:
                print("Error decoding JSON:", e)
                return None

    def prepareCommand(self, before: bool):
        """
        Prepares the command to invoke the Java service with the necessary arguments.

        Args:
            before (bool): Flag indicating whether to analyze the content before the change.

        Returns:
            A tuple containing the command list to be executed and the arguments dictionary.
        """

        args = {"file": self.save_blob_tmp(before), "target": self.target}

        command = ['java', '-jar', self.service_locator_jar_path]

        for arg, value in args.items():
            command.append(f"--{arg}")
            command.append(value)

        # Get all the blocks with their positions
        command.append("-b")

        return command, args
