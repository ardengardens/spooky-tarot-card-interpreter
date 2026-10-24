"""
Three-card Tarot Reader for Python 3.10+
Supports OpenAI, Anthropic Claude, and Google Gemini.

Install packages inside your project's activated virtual environment:
    python -m pip install openai anthropic google-genai

Choose provider:
    export TAROT_PROVIDER=claude      # macOS/Linux
    export TAROT_PROVIDER=openai
    export TAROT_PROVIDER=gemini

API keys:
    export ANTHROPIC_API_KEY="your_claude_key"
    export OPENAI_API_KEY="your_openai_key"
    export GEMINI_API_KEY="your_gemini_key"

Optional model overrides:
    export CLAUDE_MODEL="claude-opus-5-5"
    export OPENAI_MODEL="gpt-6"  # Use a model enabled for your API account.
    export GEMINI_MODEL="gemini-flash-latest"

Run:
    python tarot.py


"""

import os
import random
import sys
import time
import textwrap
import time

CARDS = [
    ("The Fool", "beginnings, openness, spontaneity"),
    ("The Magician", "initiative, resourcefulness, focused action"),
    ("The High Priestess", "intuition, mystery, inner knowing"),
    ("The Empress", "nurturing, creativity, abundance"),
    ("The Emperor", "structure, leadership, boundaries"),
    ("The Hierophant", "tradition, learning, shared values"),
    ("The Lovers", "alignment, relationships, meaningful choices"),
    ("The Chariot", "determination, direction, self-discipline"),
    ("Strength", "courage, patience, gentle confidence"),
    ("The Hermit", "reflection, solitude, inner guidance"),
    ("Wheel of Fortune", "cycles, change, turning points"),
    ("Justice", "accountability, fairness, clear choices"),
    ("The Hanged Man", "pause, surrender, a new perspective"),
    ("Death", "transition, endings, transformation"),
    ("Temperance", "balance, integration, moderation"),
    ("The Devil", "attachment, temptation, limiting patterns"),
    ("The Tower", "disruption, revelation, unstable foundations"),
    ("The Star", "hope, renewal, inspiration"),
    ("The Moon", "uncertainty, dreams, unclear information"),
    ("The Sun", "joy, vitality, clarity"),
    ("Judgement", "reckoning, awakening, answering a call"),
    ("The World", "completion, integration, accomplishment"),
]

SUITS = {
    "Wands": "energy, ambition, creativity, action",
    "Cups": "emotions, connection, relationships, imagination",
    "Swords": "thoughts, communication, decisions, conflict",
    "Pentacles": "work, resources, routines, material life",
}

RANKS = [
    ("Ace", "a seed, opening, or fresh opportunity"),
    ("Two", "a choice, partnership, or balancing act"),
    ("Three", "growth, collaboration, or early progress"),
    ("Four", "stability, structure, or a pause"),
    ("Five", "friction, challenge, or disruption"),
    ("Six", "support, transition, or regained harmony"),
    ("Seven", "assessment, strategy, or perseverance"),
    ("Eight", "movement, practice, or focused effort"),
    ("Nine", "maturity, resilience, or nearing a threshold"),
    ("Ten", "culmination, responsibility, or a cycle's peak"),
    ("Page", "curiosity, a message, or a learner's outlook"),
    ("Knight", "pursuit, momentum, or an approach in motion"),
    ("Queen", "embodied understanding, care, or inner mastery"),
    ("King", "stewardship, leadership, or mature command"),
]

SPREAD = [
    ("Past / Context", "What background or earlier influence matters?"),
    ("Present / Focus", "What dynamic deserves attention now?"),
    ("Possible Direction", "What possibility may emerge if things continue?"),
]

READING_INSTRUCTIONS = """

Be concise, but do not omit important interpretive details
just to meet a word count. Do not cut off the response mid-sentence.
For medical, legal, financial, or safety-critical questions, encourage
evidence-based decisions and qualified professional support.
"""


def create_deck():
    """Build the 78-card deck."""
    deck = [
        {"name": name, "keywords": keywords, "suit": "Major Arcana"}
        for name, keywords in CARDS
    ]

    for suit, suit_keywords in SUITS.items():
        for rank, rank_keywords in RANKS:
            deck.append({
                "name": f"{rank} of {suit}",
                "keywords": f"{rank_keywords}; {suit_keywords}",
                "suit": suit,
            })

    return deck


def draw_three(deck):
    """Draw three distinct cards using the system random generator."""
    return random.SystemRandom().sample(deck, 3)


def make_user_prompt(question, cards):
    lines = []
    for index, card in enumerate(cards):
        position = SPREAD[index][0]
        lines.append(
            f"{index + 1}. {position}: {card['name']} — {card['keywords']}"
        )

    return (
        f"User's question:\n{question}\n\n"
        f"Cards drawn:\n" + "\n".join(lines)
    )


def interpret_with_claude(question, cards):
    """Generate the reading with the Anthropic Claude API."""
    try:
        from anthropic import Anthropic
    except ImportError:
        raise RuntimeError(
            "Claude SDK missing. Install it with: python -m pip install anthropic"
        )

    if not os.getenv("ANTHROPIC_API_KEY"):
        raise RuntimeError(
            "ANTHROPIC_API_KEY is not set. Configure your Claude API key first."
        )

    client = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    model = os.getenv("CLAUDE_MODEL", "claude-opus-5-5")

    message = client.messages.create(
        model=model,
        max_tokens=2400,
        system=READING_INSTRUCTIONS,
        messages=[
            {"role": "user", "content": make_user_prompt(question, cards)}
        ],
    )

    return "\n".join(
        block.text for block in message.content if block.type == "text"
    )


def interpret_with_openai(question, cards):
    """Generate the reading with the OpenAI API."""
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError(
            "OpenAI SDK missing. Install it with: python -m pip install openai"
        )

    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Configure your OpenAI API key first."
        )

    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    model = os.getenv("OPENAI_MODEL", "gpt-6")

    response = client.responses.create(
        model=model,
        instructions=READING_INSTRUCTIONS,
        input=make_user_prompt(question, cards),
        max_output_tokens=2400,
    )
    return response.output_text


def interpret_with_gemini(question, cards):
    """Generate the reading with the Google Gemini API."""
    try:
        from google import genai
    except ImportError:
        raise RuntimeError(
            "Gemini SDK missing. Install it with: "
            "python -m pip install google-genai"
        )

    api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. Configure your Gemini API key first."
        )

    client = genai.Client(api_key=api_key)
    model = os.getenv("GEMINI_MODEL", "gemini-flash-latest")
    response = client.models.generate_content(
        model=model,
        contents=make_user_prompt(question, cards),
        config={
            "system_instruction": READING_INSTRUCTIONS,
            "max_output_tokens": 2400,
        },
    )

    if not response.text:
        raise RuntimeError("Gemini returned an empty response.")
    return response.text


def choose_provider():
    """Let the user choose a provider or use TAROT_PROVIDER."""
    configured = os.getenv("TAROT_PROVIDER", "").strip().lower()
    if configured in ("claude", "openai", "gemini"):
        print(f"Using provider: {configured}")
        return configured

    while True:
        print("\\nChoose your interpretation model:")
        print("  1. Claude")
        print("  2. OpenAI")
        print("  3. Google Gemini")
        choice = input("Enter 1, 2, or 3: ").strip()
        if choice == "1":
            return "claude"
        if choice == "2":
            return "openai"
        if choice == "3":
            return "gemini"
        print("Please enter 1, 2, or 3.")



def type_out(text, delay=None):
    """Print the interpretation character by character, wrapping to terminal width."""
    if delay is None:
        # Set TAROT_TYPE_DELAY=0.01 for a gentle typewriter effect.
        try:
            delay = float(os.getenv("TAROT_TYPE_DELAY", "0.008"))
        except ValueError:
            delay = 0.008
    delay = max(0.0, min(delay, 0.2))

    # Wrap paragraphs to the current terminal width without splitting words.
    try:
        width = max(40, min(120, os.get_terminal_size().columns))
    except OSError:
        width = 80

    paragraphs = [p.strip() for p in text.strip().splitlines() if p.strip()]
    wrapped = "\\n\\n".join(
        textwrap.fill(p, width=width, break_long_words=False, break_on_hyphens=False)
        for p in paragraphs
    )

    for character in wrapped:
        print(character, end="", flush=True)
        if delay:
            time.sleep(delay)
    print("\\n")




def type_out(text, delay=0.15):
    """Print the finished interpretation one character at a time."""
    for character in text:
        print(character, end="", flush=True)
        if delay > 0:
            time.sleep(delay)
    print()  # End the interpretation with a newline.


def main():
    print("\n=== Three-Card Tarot Reflection ===")
    print("Symbolic reflection and entertainment, not certain prediction.")

    try:
        provider = choose_provider()
    except (EOFError, KeyboardInterrupt):
        print("\nGoodbye.")
        return

    deck = create_deck()
    interpreter = {
        "claude": interpret_with_claude,
        "openai": interpret_with_openai,
        "gemini": interpret_with_gemini,
    }[provider]

    print("\nAsk a question, or type 'quit' to exit.\n")

    while True:
        try:
            question = input("Your question: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            break

        if question.lower() in ("quit", "exit", "q"):
            print("Goodbye.")
            break

        if not question:
            print("Please enter a question.\n")
            continue

        if len(question) > 2000:
            print("Please keep your question under 2,000 characters.\n")
            continue

        cards = draw_three(deck)

        print("\nYour cards:")
        for index, card in enumerate(cards):
            print(f"  {SPREAD[index][0]}: {card['name']}")

        print(f"\nAsking {provider.title()} to interpret your spread...\n")
        try:
            reading = interpreter(question, cards)
            type_out(reading)
        except Exception as error:
            print(f"Could not generate the interpretation: {error}")
            print(
                "Check the provider's API key, model ID, account access, "
                "connection, and usage limits."
            )

        print("\n" + "-" * 58 + "\n")


if __name__ == "__main__":
    main()
