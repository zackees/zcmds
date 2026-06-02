import unittest


class ImgAiTester(unittest.TestCase):
    def test_imgai_imports(self) -> None:
        from zcmds.cmds.common import imgai

        self.assertTrue(callable(imgai.main))
        self.assertTrue(callable(imgai.read_console))


if __name__ == "__main__":
    unittest.main()
