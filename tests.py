import pytest
import subprocess
from pathlib import Path

TEST_CASES = {
    "alice.txt": [
        "Employee: Welcome to our coffee shop. What can I get you?",
        "Guest: I'd like a latte",
        "Employee: Would you like to add a cookie for $0.50?",
        "Guest: No, thank you",
        "Employee: Would you like anything else?",
        "Guest: I'd like a macchiato",
        "Employee: Would you like anything else?",
        "Guest: I don't want a macchiato",
        "Employee: Would you like anything else?",
        "Guest: That's all",
        "Employee: Your total is $2.13. Thank you and have a nice day!"
    ],
    "bob.txt": [
        "Employee: Welcome to our coffee shop. What can I get you?",
        "Guest: I'd like an americano",
        "Employee: Would you like to add a cookie for $0.50?",
        "Guest: Yes, please",
        "Employee: Would you like anything else?",
        "Guest: That's all",
        "Employee: Your total is $2.01. Thank you and have a nice day!"
    ],
    "fred.txt": [
        "Employee: Welcome to our coffee shop. What can I get you?",
        "Guest: I'd like an americano",
        "Employee: Would you like to add a cookie for $0.50?",
        "Guest: Yes, please",
        "Employee: Would you like anything else?",
        "Guest: I'd like a latte",
        "Employee: Would you like anything else?",
        "Guest: That's all",
        "Employee: Your total is $4.14. Thank you and have a nice day!"
    ],
    "jack.txt": [
        "Employee: Welcome to our coffee shop. What can I get you?",
        "Guest: I'd like an americano",
        "Employee: Would you like to add a cookie for $0.50?",
        "Guest: No, thank you",
        "Employee: Would you like anything else?",
        "Guest: I'd like an americano",
        "Employee: Would you like anything else?",
        "Guest: I'd like an americano",
        "Employee: Would you like anything else?",
        "Guest: I don't want an americano",
        "Employee: Would you like anything else?",
        "Guest: I don't want an americano",
        "Employee: Would you like anything else?",
        "Guest: That's all",
        "Employee: Your total is $1.51. Thank you and have a nice day!"
    ]
}

@pytest.mark.parametrize("input_file,expected_output", TEST_CASES.items())
def test_conversation(input_file, expected_output, tmp_path):
    input_path = tmp_path / input_file
    input_path.write_text("\n".join([line.split("Guest: ")[1] for line in expected_output if line.startswith("Guest:")]))
    
    result = subprocess.check_output(
        ["./coffeeshop.py", str(input_path)],
        stderr=subprocess.STDOUT,
        universal_newlines=True
    )
    
    assert "\n".join(expected_output) in result
