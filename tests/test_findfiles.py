import unittest
import os
import subprocess
from datetime import datetime, timedelta
from zcmds.cmds.common.findfiles import main

HERE = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(HERE, "findfilestmp")
os.makedirs(TMP_DIR, exist_ok=True)


class FindFiles(unittest.TestCase):
    def tearDown(self) -> None:
        # Remove all files in the TMP_DIR
        for filename in os.listdir(TMP_DIR):
            os.remove(os.path.join(TMP_DIR, filename))

    def test_findfiles_size(self) -> None:
        # Create a temporary file with size 4k
        tmpfilename = os.path.join(TMP_DIR, "tempfile.mp4")
        with open(tmpfilename, "wb") as tmpfile:
            tmpfile.write(os.urandom(4 * 1024))  # 4k

        try:
            # Confirm that it is found with the size filter
            output = []
            sys_args = ["--larger-than", "3k", "--smaller-than", "5k", "--cwd", TMP_DIR, "*.mp4"]
            result = main(sys_args, _print=output.append)
            self.assertEqual(0, result)
            self.assertIn(tmpfilename, "\n".join(output))

            # Now do the search but use a size filter that is outside the bounds of the file and confirm
            # it can't be found.
            output = []
            sys_args = ["--larger-than", "5k", "--smaller-than", "3k", "--cwd", TMP_DIR, "*.mp4"]
            result = main(sys_args, _print=output.append)
            self.assertEqual(1, result)
            self.assertNotIn(tmpfilename, "\n".join(output))
        except Exception as e:
            print(f"An error occurred while executing the command: {e}")
            self.fail("Command execution failed")
        finally:
            os.remove(tmpfilename)

    def test_findfiles_size_using_cmd(self) -> None:
        # Chat GPT Implement this using subprocess.check_output
        tmpfilename = os.path.join(TMP_DIR, "tempfile.mp4")
        with open(tmpfilename, "wb") as tmpfile:
            tmpfile.write(os.urandom(4 * 1024))  # 4k
        try:
            command = f'python -m zcmds.cmds.common.findfiles --larger-than 3k --smaller-than 5k --cwd {TMP_DIR} "*.mp4"'
            result = subprocess.check_output(command, shell=True, cwd=TMP_DIR).decode("utf-8")
            self.assertIn(tmpfilename, result)
        except subprocess.CalledProcessError as e:
            print(f"An error occurred while executing the command: {e}")
            self.fail("Command execution failed")
        finally:
            os.remove(tmpfilename)

    def test_findfiles_sanity(self) -> None:
        # Create a temporary file with size 4k
        tmpfilename = os.path.join(TMP_DIR, "tempfile.mp4")
        with open(tmpfilename, "wb") as tmpfile:
            tmpfile.write(os.urandom(4 * 1024))  # 4k

        try:
            # Confirm that it is found
            output = []
            sys_args = ["*.mp4"]
            result = main(sys_args, _print=output.append)
            self.assertEqual(0, result)
            self.assertIn(tmpfilename, "\n".join(output))
        except Exception as e:
            print(f"An error occurred while executing the command: {e}")
            self.fail("Command execution failed")
        finally:
            os.remove(tmpfilename)

    def test_findfiles_start_end(self) -> None:
        # Create a temporary file
        tmpfilename = os.path.join(TMP_DIR, "tempfile.mp4")
        with open(tmpfilename, "wb") as tmpfile:
            tmpfile.write(os.urandom(4 * 1024))  # 4k

        try:
            # Get today's date in the format YYYY-MM-DD
            today = datetime.now().strftime("%Y-%m-%d")
            # Get yesterday's date in the format YYYY-MM-DD
            yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

            # Confirm that it is found with the start time filter
            output = []
            sys_args = ["--start", yesterday, "--end", today, "--cwd", TMP_DIR, "*.mp4"]
            result = main(sys_args, _print=output.append)
            self.assertEqual(0, result)
            self.assertIn(tmpfilename, "\n".join(output))

            # Now do the search but use a start time that is after the file's creation time
            # and confirm it can't be found.
            output = []
            # Set start date as tomorrow
            tomorrow = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")
            sys_args = ["--start", tomorrow, "--cwd", TMP_DIR, "*.mp4"]
            result = main(sys_args, _print=output.append)
            self.assertEqual(1, result)
            self.assertNotIn(tmpfilename, "\n".join(output))
        except Exception as e:
            print(f"An error occurred while executing the command: {e}")
            self.fail("Command execution failed")


if __name__ == "__main__":
    unittest.main()
