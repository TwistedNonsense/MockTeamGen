import unittest

import os


def _has_display() -> bool:
    if os.name == "nt":
        return True
    return bool(os.environ.get("DISPLAY"))


class TestModuleImports(unittest.TestCase):
    def test_import_hash_password(self):
        import hash_password  # noqa: F401
        self.assertTrue(hasattr(hash_password, "HashPanel"))
        self.assertTrue(hasattr(hash_password, "HASHING_AVAILABLE"))
        self.assertIsInstance(hash_password.HASHING_AVAILABLE, bool)

    def test_import_generator(self):
        import generator  # noqa: F401
        self.assertTrue(hasattr(generator, "App"))

    @unittest.skipUnless(_has_display(), "No GUI display available for tkinter")
    def test_hash_panel_constructs(self):
        import tkinter as tk

        from hash_password import HashPanel

        root = tk.Tk()
        try:
            root.withdraw()
            panel = HashPanel(root)
            self.assertIsNotNone(panel)
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()
