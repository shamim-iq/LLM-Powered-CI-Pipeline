import os
import re
from openai import OpenAI

# Initialize client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

INPUT_FILE = "app/calculator.py"
OUTPUT_FILE = "tests/test_calculator.py"

# Fallback tests (ensures pipeline never breaks)
FALLBACK_TESTS = """
import pytest
from app.calculator import add, subtract, multiply, divide

def test_add():
    assert add(2, 3) == 5

def test_subtract():
    assert subtract(5, 3) == 2

def test_multiply():
    assert multiply(2, 3) == 6

def test_divide():
    assert divide(10, 2) == 5

def test_divide_by_zero():
    with pytest.raises(ValueError):
        divide(10, 0)
"""

def read_code():
    with open(INPUT_FILE, "r") as f:
        return f.read()


def generate_tests(code: str) -> str:
    """
    Calls LLM to generate pytest test cases
    """
    prompt = f"""
You are a Python testing expert.

Generate pytest test cases for the following code.

STRICT REQUIREMENTS:
- Use correct import: from app.calculator import add, subtract, multiply, divide
- Do NOT use placeholders like 'your_module'
- Include edge cases and exception handling
- Output ONLY valid Python code (no explanations)

Code:
{code}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[{"role": "user", "content": prompt}],
        )

        return response.choices[0].message.content

    except Exception as e:
        print(f"[WARNING] LLM generation failed: {e}")
        print("[INFO] Falling back to static test cases.")
        return FALLBACK_TESTS


def sanitize_tests(test_code: str) -> str:
    """
    Cleans and fixes common LLM issues
    """

    # Fix incorrect imports
    test_code = re.sub(
        r"from\s+your_module\s+import",
        "from app.calculator import",
        test_code,
    )

    test_code = re.sub(
        r"from\s+calculator\s+import",
        "from app.calculator import",
        test_code,
    )

    # Remove markdown code fences if present
    test_code = test_code.replace("```python", "").replace("```", "")

    # Ensure file ends with newline
    if not test_code.endswith("\n"):
        test_code += "\n"

    return test_code


def write_tests(test_code: str):
    """
    Writes test cases to file
    """
    os.makedirs("tests", exist_ok=True)

    with open(OUTPUT_FILE, "w") as f:
        f.write(test_code)

    print(f"[INFO] Tests written to {OUTPUT_FILE}")


def main():
    print("[INFO] Reading source code...")
    code = read_code()

    print("[INFO] Generating tests using LLM...")
    tests = generate_tests(code)

    print("[INFO] Sanitizing generated tests...")
    tests = sanitize_tests(tests)

    print("[INFO] Writing tests to file...")
    write_tests(tests)

    print("[SUCCESS] Test generation complete.")


if __name__ == "__main__":
    main()