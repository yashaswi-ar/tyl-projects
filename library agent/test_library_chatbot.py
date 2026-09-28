import builtins
import contextlib
import importlib.util
import io
import pathlib
import unittest

MODULE_PATH = pathlib.Path(__file__).resolve().parent / 'student_library_chatbot.py'


def load_module():
    spec = importlib.util.spec_from_file_location('student_library_chatbot', MODULE_PATH)
    module = importlib.util.module_from_spec(spec)
    original_input = builtins.input
    builtins.input = lambda *args, **kwargs: (_ for _ in ()).throw(EOFError)
    try:
        spec.loader.exec_module(module)
    except SystemExit:
        pass
    finally:
        builtins.input = original_input
    return module


class LibraryChatbotTests(unittest.TestCase):
    def test_specific_book_reports_total_and_available_copies(self):
        module = load_module()
        stream = io.StringIO()
        with contextlib.redirect_stdout(stream):
            module.answer('How many copies of The Jungle Book are available?')
        output = stream.getvalue().lower()
        self.assertIn('total copies', output)
        self.assertIn('available copies', output)
        self.assertIn('3', output)


if __name__ == '__main__':
    unittest.main()
