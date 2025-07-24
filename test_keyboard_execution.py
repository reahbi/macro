"""
Test keyboard type step execution with variables
"""

import sys
sys.path.insert(0, 'src')

from core.macro_types import KeyboardTypeStep, Macro
from automation.executor import StepExecutor
from config.settings import Settings
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)

# Create settings
settings = Settings()

# Create a keyboard type step
step = KeyboardTypeStep()
step.name = "Test Keyboard Step"
step.text = "Hello ${name}, your order ${order_id} is ready!"
step.use_variables = True
step.interval = 0.0  # No delay for testing

print("Step details:")
print(f"  Text: {step.text}")
print(f"  Use variables: {step.use_variables}")

# Create executor with settings
executor = StepExecutor(settings)

# Set variables (simulating Excel data)
variables = {
    'name': 'Claude',
    'order_id': '12345'
}
executor.set_variables(variables)

print(f"\nVariables set: {variables}")

# Test variable substitution directly
substituted = executor._substitute_variables(step.text)
print(f"\nDirect substitution result: {substituted}")

# Inspect the actual handler
print(f"\nHandler for KEYBOARD_TYPE: {executor._handlers.get(step.step_type)}")

# Mock the pyautogui.typewrite to see what would be typed
import pyautogui
original_typewrite = pyautogui.typewrite
typed_text = []

def mock_typewrite(text, interval=0.0):
    typed_text.append(text)
    print(f"Mock typewrite called with: '{text}', interval={interval}")

pyautogui.typewrite = mock_typewrite

try:
    # Execute the step
    print("\nExecuting step...")
    executor.execute_step(step)
    print(f"Text that would be typed: {typed_text}")
finally:
    # Restore original
    pyautogui.typewrite = original_typewrite