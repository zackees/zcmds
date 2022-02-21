import os
import unittest


class MainTester(unittest.TestCase):

    def test_imports(self) -> None:
        from static_ffmpeg.run import check_system
        check_system()


if __name__ == "__main__":
    unittest.main()
