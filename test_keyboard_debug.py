"""
Debug script to test keyboard type step variable handling
"""

import sys
sys.path.insert(0, 'src')

from core.macro_types import KeyboardTypeStep, Macro, StepFactory
import json

# Create a keyboard type step
step = KeyboardTypeStep()
step.name = "Test Keyboard Step"
step.text = "Hello ${name}, your order ${order_id} is ready!"
step.use_variables = True
step.interval = 0.1

print("Step created:")
print(f"  Name: {step.name}")
print(f"  Text: {step.text}")
print(f"  Use variables: {step.use_variables}")
print(f"  Interval: {step.interval}")

# Convert to dict
step_dict = step.to_dict()
print("\nStep as dict:")
print(json.dumps(step_dict, indent=2))

# Create from dict
restored_step = KeyboardTypeStep.from_dict(step_dict)
print("\nRestored step:")
print(f"  Name: {restored_step.name}")
print(f"  Text: {restored_step.text}")
print(f"  Use variables: {restored_step.use_variables}")
print(f"  Interval: {restored_step.interval}")

# Test in a macro
macro = Macro(name="Test Macro")
macro.add_step(step)

# Convert macro to dict
macro_dict = macro.to_dict()
print("\nMacro as dict:")
print(json.dumps(macro_dict, indent=2))

# Save to file
with open("test_macro.json", "w", encoding='utf-8') as f:
    json.dump(macro_dict, f, indent=2, ensure_ascii=False)

# Load from file
with open("test_macro.json", "r", encoding='utf-8') as f:
    loaded_macro_dict = json.load(f)

# Create macro from loaded dict
loaded_macro = Macro.from_dict(loaded_macro_dict)
loaded_step = loaded_macro.steps[0]

print("\nLoaded step from file:")
print(f"  Name: {loaded_step.name}")
print(f"  Text: {loaded_step.text}")
print(f"  Use variables: {loaded_step.use_variables}")
print(f"  Interval: {loaded_step.interval}")

# Test variable substitution
from automation.executor import StepExecutor

executor = StepExecutor()
executor.set_variables({
    'name': 'Claude',
    'order_id': '12345'
})

# Test substitution
substituted_text = executor._substitute_variables(step.text)
print(f"\nOriginal text: {step.text}")
print(f"Substituted text: {substituted_text}")