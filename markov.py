from collections import defaultdict
from itertools import pairwise
from pathlib import Path
import random
import sys

TERMINAL_PUNCTUATION = (".", "!", "?")
CLOSING_PUNCTUATION = "\"'”’)}]"


def build_chain(text: str) -> dict[str, list[str]]:
    """Build a first-order Markov Chain transition dictionary from input text.

    Args:
        text: Raw source text (corpus).

    Returns:
        Dictionary mapping each token to a list of subsequent candidate tokens.
    """
    words = text.split()
    if len(words) < 2:
        return {}

    chain = defaultdict(list)
    for current_word, next_word in pairwise(words):
        chain[current_word].append(next_word)
    return dict(chain)


def generate_sentence(chain: dict[str, list[str]], max_words: int = 30) -> str:
    """Generate a sentence using the Markov Chain transitions.

    Args:
        chain: Markov transition dictionary.
        max_words: Maximum number of tokens in the generated sentence.

    Returns:
        Generated sentence string.
    """
    if not chain or max_words <= 0:
        return ""

    # Prefer capitalized words that do not immediately end the sentence
    candidate_starters = [
        w for w in chain
        if w and w[0].isupper() and not w.rstrip(CLOSING_PUNCTUATION).endswith(TERMINAL_PUNCTUATION)
    ]
    if not candidate_starters:
        candidate_starters = [w for w in chain if w and w[0].isupper()]
    if not candidate_starters:
        candidate_starters = list(chain.keys())

    current_word = random.choice(candidate_starters)
    output = [current_word]

    for _ in range(max_words - 1):
        if current_word.rstrip(CLOSING_PUNCTUATION).endswith(TERMINAL_PUNCTUATION) or current_word not in chain:
            break
        next_word = random.choice(chain[current_word])
        output.append(next_word)
        current_word = next_word

    return " ".join(output)


def load_corpus(file_path: str) -> str:
    """Read and return utf-8 encoded corpus text from the specified file.

    Args:
        file_path: Path to the corpus file.

    Returns:
        Full content of the corpus file.

    Raises:
        FileNotFoundError: If the file does not exist or is a directory.
    """
    path = Path(file_path)
    if not path.is_file():
        raise FileNotFoundError(f"File not found: {file_path}")
    return path.read_text(encoding="utf-8")


def main():
    """CLI entry point for generating sentences from a text corpus."""
    target_path = sys.argv[1] if len(sys.argv) > 1 else "input.txt"

    try:
        raw_text = load_corpus(target_path)
    except (FileNotFoundError, UnicodeDecodeError, PermissionError) as err:
        print(f"Error: {err}", file=sys.stderr)
        print("Usage: python markov.py [corpus_file.txt] (or create 'input.txt')", file=sys.stderr)
        sys.exit(1)

    chain = build_chain(raw_text)
    if not chain:
        print("Error: Input text is too short to generate transitions (minimum 2 words needed).", file=sys.stderr)
        sys.exit(1)

    print("--- Generated Text (1st-Order Markov Chain) ---")
    for i in range(3):
        print(f"[{i + 1}] {generate_sentence(chain)}")


if __name__ == "__main__":
    main()
