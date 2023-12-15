import unittest

from zcmds.util.sound import beep
from zcmds.util.streaming_console import (
    StreamingConsoleMarkdown,
    _get_clear_line_sequence,
)


class TestStreamingConsoleMarkdown(unittest.TestCase):

    @unittest.skip("skip")
    def test(self) -> None:
        data = "To write a binary search algorithm in Python, you don't need any additional third-party libraries. Here's an example implementation:\n\n"
        scm = StreamingConsoleMarkdown()
        md = scm.update(data)
        self.assertEqual(1, scm.last_written_lines)
        #scm.last_written_lines = 1
        scm.update(data)
        self.assertEqual(1, scm.last_written_lines)
        print()


    def test2(self) -> None:
        data = "To write a binary search algorithm in Python, you don't need any additional third-party libraries. Here's an example implementation:\n\n```python\ndef binary_search(arr, target):\n    low = 0\n    high = len(arr) - 1\n\n    while low <= high:\n        mid = (low + high) // 2\n        if arr[mid] == target:\n            return mid\n        elif arr[mid] < target:\n            low = mid + 1\n        else:\n            high = mid - 1\n\n    return -1\n\n# Example usage"
        scm = StreamingConsoleMarkdown()
        md = scm.update(data)
        scm.pop_last()
        print()

    @unittest.skip("skip")
    def test3(self) -> None:
        import sys
        md = b"To write a binary search algorithm in Python, you don't need any additional third-party libraries. Here's an example implementation:\n\n\x1b[48;2;32;32;32m\x1b[38;2;110;191;38;01mdef\x1b[39;00m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;113;173;255mbinary_search\x1b[39m\x1b[38;2;208;208;208m(\x1b[39m\x1b[38;2;208;208;208marr\x1b[39m\x1b[38;2;208;208;208m,\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208mtarget\x1b[39m\x1b[38;2;208;208;208m)\x1b[39m\x1b[38;2;208;208;208m:\x1b[39m\n\x1b[38;2;208;208;208m    \x1b[39m\x1b[38;2;208;208;208mlow\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208m=\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;81;178;253m0\x1b[39m\n\x1b[38;2;208;208;208m    \x1b[39m\x1b[38;2;208;208;208mhigh\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208m=\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;47;188;205mlen\x1b[39m\x1b[38;2;208;208;208m(\x1b[39m\x1b[38;2;208;208;208marr\x1b[39m\x1b[38;2;208;208;208m)\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208m-\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;81;178;253m1\x1b[39m\n\n\x1b[38;2;208;208;208m    \x1b[39m\x1b[38;2;110;191;38;01mwhile\x1b[39;00m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208mlow\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208m<\x1b[39m\x1b[38;2;208;208;208m=\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208mhigh\x1b[39m\x1b[38;2;208;208;208m:\x1b[39m\n\x1b[38;2;208;208;208m        \x1b[39m\x1b[38;2;208;208;208mmid\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208m=\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208m(\x1b[39m\x1b[38;2;208;208;208mlow\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208m+\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208mhigh\x1b[39m\x1b[38;2;208;208;208m)\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208m/\x1b[39m\x1b[38;2;208;208;208m/\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;81;178;253m2\x1b[39m\n\x1b[38;2;208;208;208m        \x1b[39m\x1b[38;2;110;191;38;01mif\x1b[39;00m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208marr\x1b[39m\x1b[38;2;208;208;208m[\x1b[39m\x1b[38;2;208;208;208mmid\x1b[39m\x1b[38;2;208;208;208m]\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208m==\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208mtarget\x1b[39m\x1b[38;2;208;208;208m:\x1b[39m\n\x1b[38;2;208;208;208m            \x1b[39m\x1b[38;2;110;191;38;01mreturn\x1b[39;00m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208mmid\x1b[39m\n\x1b[38;2;208;208;208m        \x1b[39m\x1b[38;2;110;191;38;01melif\x1b[39;00m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208marr\x1b[39m\x1b[38;2;208;208;208m[\x1b[39m\x1b[38;2;208;208;208mmid\x1b[39m\x1b[38;2;208;208;208m]\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208m<\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208mtarget\x1b[39m\x1b[38;2;208;208;208m:\x1b[39m\n\x1b[38;2;208;208;208m            \x1b[39m\x1b[38;2;208;208;208mlow\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208m=\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208mmid\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208m+\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;81;178;253m1\x1b[39m\n\x1b[38;2;208;208;208m        \x1b[39m\x1b[38;2;110;191;38;01melse\x1b[39;00m\x1b[38;2;208;208;208m:\x1b[39m\n\x1b[38;2;208;208;208m            \x1b[39m\x1b[38;2;208;208;208mhigh\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208m=\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208mmid\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208m-\x1b[39m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;81;178;253m1\x1b[39m\n\n\x1b[38;2;208;208;208m    \x1b[39m\x1b[38;2;110;191;38;01mreturn\x1b[39;00m\x1b[38;2;208;208;208m \x1b[39m\x1b[38;2;208;208;208m-\x1b[39m\x1b[38;2;81;178;253m1\x1b[39m\n\n\x1b[38;2;171;171;171;03m# Example usage\x1b[39;00m\x1b[39;49;00m\n\x1b[49m"
        sys.stdout.write(md.decode("utf-8"))
        for i in range(18):
            scm = StreamingConsoleMarkdown()
            scm._clear_last_line()
            i = i
            import time
            time.sleep(.4)
        print()

if __name__ == "__main__":
    unittest.main()
