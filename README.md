# Markov Chain Text Generator

A lightweight, zero-dependency first-order Markov Chain sentence generator written in pure Python.

This project analyzes the word transition probabilities within any given source text (corpus) and generates novel, stylistically consistent sentences based on learned state transitions.

---

## Features

- **Zero Dependencies:** Pure Python with standard library only (`collections.defaultdict`, `itertools.pairwise`, `random`, `pathlib`, `sys`).
- **Probabilistic Word Sampling:** Retains duplicate transition candidates to ensure natural frequency-weighted selection without external math libraries.
- **Sentence-Aware Generation:**
  - Intelligently chooses capitalized starter words to begin sentences.
  - Automatically terminates when encountering terminal punctuation (`.`, `!`, `?`), reaching `max_words`, or hitting a dead end.
- **Robust CLI & Error Handling:** Gracefully handles non-existent files and insufficient corpus tokens with clear messages.
- **Comprehensive Unit Tests:** 100% standard library `unittest` suite covering transitions, edge cases, and CLI behavior.

---

## How It Works

A **1st-Order Markov Chain** models sequences where the probability of each word $W_n$ depends solely on the immediately preceding word $W_{n-1}$:

$$P(W_n \mid W_{n-1})$$

### 1. Building the Transition Graph
Given a corpus:
> *"The cat sat on the mat."*

The model tokenizes words and pairs adjacent tokens:
- `"The"` $\rightarrow$ `["cat"]`
- `"cat"` $\rightarrow$ `["sat"]`
- `"the"` $\rightarrow$ `["mat."]`

### 2. Sentence Synthesis
1. Pick a random word starting with an uppercase letter (`"In"`, `"The"`, `"Alice"`).
2. Sample the next token from the candidate list corresponding to the current state using `random.choice`.
3. Stop when terminal punctuation (`.`, `!`, `?`) is reached or the word limit is met.

---

## Getting Started

### Prerequisites

- Python 3.10 or higher.
- No external packages required (`pip install` not needed).

### Usage

1. **Default Run (uses `input.txt`):**
   ```bash
   python markov.py
   ```

2. **Custom Corpus:**
   Pass any text file path as an argument:
   ```bash
   python markov.py path/to/your_text.txt
   ```

---

## Sample Output

Using an excerpt from Ömer Seyfettin's classic story *Kaşağı* (`input.txt`) as the corpus:

```text
--- Generated Text (1st-Order Markov Chain) ---
[1] Annem geldikten sonra yalağın taşında ezdi dedim.
[2] Ertesi sene annem yazın gene ahırda hep yalnız tımarı beceremiyordum.
[3] Kasabaya at gönderildi, doktor geldi.
```

---

## Running Tests

Run the built-in unit test suite:

```bash
python -m unittest test_markov.py
```

Expected output:
```text
............
----------------------------------------------------------------------
Ran 12 tests in 0.050s

OK
```

---

## Project Structure

```text
├── markov.py          # Core logic (build_chain, generate_sentence, CLI)
├── test_markov.py     # Unit test suite
├── input.txt          # Sample corpus (Ömer Seyfettin - Kaşağı)
└── README.md          # Project documentation
```

---

## License

This project is open-source and available under the [MIT License](LICENSE).
