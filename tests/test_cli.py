import unittest

from cs_deep_reader.cli import build_parser


class CliParserTests(unittest.TestCase):
    def test_import_command_parses_pdf_and_metadata(self) -> None:
        args = build_parser().parse_args(["import-book", "book.pdf", "--title", "Algorithms"])
        self.assertEqual("import-book", args.command)
        self.assertEqual("Algorithms", args.title)

    def test_mastery_command_requires_score(self) -> None:
        with self.assertRaises(SystemExit):
            build_parser().parse_args(["record-mastery", "--book", "algorithms", "--concept", "heap"])


if __name__ == "__main__":
    unittest.main()
