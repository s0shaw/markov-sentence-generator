import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from markov import build_chain, generate_sentence, load_corpus, main


class TestMarkovChain(unittest.TestCase):
    def test_build_chain_transitions(self):
        text = "the cat sat on the mat"
        chain = build_chain(text)
        self.assertEqual(chain["the"], ["cat", "mat"])
        self.assertEqual(chain["cat"], ["sat"])
        self.assertEqual(chain["sat"], ["on"])
        self.assertEqual(chain["on"], ["the"])
        self.assertNotIn("mat", chain)

    def test_build_chain_insufficient_tokens(self):
        self.assertEqual(build_chain(""), {})
        self.assertEqual(build_chain("hello"), {})

    def test_generate_sentence_basic(self):
        text = "The dog barked. The dog ran."
        chain = build_chain(text)
        sentence = generate_sentence(chain, max_words=10)
        self.assertTrue(sentence.startswith("The"))
        self.assertTrue(len(sentence.split()) <= 10)

    def test_generate_sentence_empty_or_zero_length(self):
        text = "The dog barked."
        chain = build_chain(text)
        self.assertEqual(generate_sentence({}, max_words=10), "")
        self.assertEqual(generate_sentence(chain, max_words=0), "")
        self.assertEqual(generate_sentence(chain, max_words=-5), "")

    def test_starter_word_avoids_terminal_punctuation(self):
        # "No." has uppercase starter and exists in chain ("No." -> "The"),
        # but should not be picked because "Start" is available without terminal punctuation.
        text = "Start walking now. No. The end."
        chain = build_chain(text)
        for _ in range(20):
            sentence = generate_sentence(chain, max_words=10)
            self.assertFalse(sentence.startswith("No."))

    def test_generate_sentence_terminal_punctuation_with_quotes(self):
        text = 'Alice shouted "Run!" and they vanished.'
        chain = build_chain(text)
        # When "Run!"" is hit, sentence should stop immediately
        # Alice -> shouted -> "Run!"
        sentence = generate_sentence(chain, max_words=10)
        if '"Run!"' in sentence:
            words = sentence.split()
            self.assertEqual(words[-1], '"Run!"')

    def test_load_corpus_missing_file(self):
        with self.assertRaises(FileNotFoundError):
            load_corpus("non_existent_file_xyz.txt")

    def test_load_corpus_success(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            sample_file = Path(tmp_dir) / "sample.txt"
            sample_content = "Sample content for markov test."
            sample_file.write_text(sample_content, encoding="utf-8")
            loaded = load_corpus(str(sample_file))
            self.assertEqual(loaded, sample_content)

    def test_main_missing_file(self):
        with patch("sys.argv", ["markov.py", "non_existent_file_xyz.txt"]):
            with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
                with self.assertRaises(SystemExit) as cm:
                    main()
                self.assertEqual(cm.exception.code, 1)
                self.assertIn("Error: File not found", mock_stderr.getvalue())

    def test_main_unicode_decode_error(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            sample_file = Path(tmp_dir) / "invalid_encoding.txt"
            # Write invalid UTF-8 bytes
            sample_file.write_bytes(b"\xff\xfe\x00\x00invalid")
            with patch("sys.argv", ["markov.py", str(sample_file)]):
                with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
                    with self.assertRaises(SystemExit) as cm:
                        main()
                    self.assertEqual(cm.exception.code, 1)
                    self.assertIn("Error:", mock_stderr.getvalue())

    def test_main_insufficient_corpus(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            sample_file = Path(tmp_dir) / "short.txt"
            sample_file.write_text("OneWord", encoding="utf-8")
            with patch("sys.argv", ["markov.py", str(sample_file)]):
                with patch("sys.stderr", new_callable=io.StringIO) as mock_stderr:
                    with self.assertRaises(SystemExit) as cm:
                        main()
                    self.assertEqual(cm.exception.code, 1)
                    self.assertIn("minimum 2 words needed", mock_stderr.getvalue())

    def test_main_success(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            sample_file = Path(tmp_dir) / "corpus.txt"
            sample_file.write_text("The quick brown fox jumps over the lazy dog.", encoding="utf-8")
            with patch("sys.argv", ["markov.py", str(sample_file)]):
                with patch("sys.stdout", new_callable=io.StringIO) as mock_stdout:
                    main()
                    output = mock_stdout.getvalue()
                    self.assertIn("--- Generated Text (1st-Order Markov Chain) ---", output)
                    self.assertIn("[1]", output)
                    self.assertIn("[2]", output)
                    self.assertIn("[3]", output)


if __name__ == "__main__":
    unittest.main()
