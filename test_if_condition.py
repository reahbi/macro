#!/usr/bin/env python3
"""
Test script for if condition functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.core.macro_types import (
    IfConditionStep, MouseClickStep, KeyboardTypeStep, 
    WaitTimeStep, StepFactory
)
from src.automation.executor import StepExecutor
from src.config.settings import Settings
import logging

# Setup logging
logging.basicConfig(level=logging.DEBUG)

def test_if_condition():
    """Test if condition step creation and execution"""
    
    # Create settings
    settings = Settings()
    
    # Create executor
    executor = StepExecutor(settings)
    
    # Test 1: Variable comparison condition
    print("\n=== Test 1: Variable comparison ===")
    
    # Set test variables
    executor.set_variables({
        'name': '홍길동',
        'age': '25',
        'department': '의료정보팀'
    })
    
    # Create if condition step
    if_step = IfConditionStep()
    if_step.name = "나이 확인"
    if_step.condition_type = "variable_greater"
    if_step.condition_value = {
        'variable': 'age',
        'compare_value': '20'
    }
    
    # Add true branch steps
    true_step = KeyboardTypeStep()
    true_step.name = "성인 메시지"
    true_step.text = "{{name}}님은 성인입니다."
    if_step.true_steps.append(true_step)
    
    # Add false branch steps
    false_step = KeyboardTypeStep()
    false_step.name = "미성년 메시지"
    false_step.text = "{{name}}님은 미성년자입니다."
    if_step.false_steps.append(false_step)
    
    # Execute (dry run - just log)
    print(f"Condition: age ({executor.variables['age']}) > 20")
    result = executor._execute_if_condition(if_step)
    print(f"Result: {result}")
    
    # Test 2: Text contains condition
    print("\n=== Test 2: Text contains ===")
    
    if_step2 = IfConditionStep()
    if_step2.name = "부서 확인"
    if_step2.condition_type = "variable_contains"
    if_step2.condition_value = {
        'variable': 'department',
        'compare_value': '의료'
    }
    
    print(f"Condition: department ({executor.variables['department']}) contains '의료'")
    result2 = executor._execute_if_condition(if_step2)
    print(f"Result: {result2}")
    
    # Test 3: Variable with template substitution
    print("\n=== Test 3: Variable template ===")
    
    executor.set_variables({
        'threshold': '30',
        'current_value': '25'
    })
    
    if_step3 = IfConditionStep()
    if_step3.name = "임계값 비교"
    if_step3.condition_type = "variable_less"
    if_step3.condition_value = {
        'variable': 'current_value',
        'compare_value': '{{threshold}}'  # Using variable in comparison
    }
    
    print(f"Condition: current_value ({executor.variables['current_value']}) < threshold ({executor.variables['threshold']})")
    result3 = executor._execute_if_condition(if_step3)
    print(f"Result: {result3}")
    
    # Test 4: Serialization
    print("\n=== Test 4: Serialization ===")
    
    # Convert to dict
    step_dict = if_step.to_dict()
    print(f"Serialized step type: {step_dict['step_type']}")
    print(f"Condition type: {step_dict['condition_type']}")
    print(f"True steps count: {len(step_dict['true_steps'])}")
    print(f"False steps count: {len(step_dict['false_steps'])}")
    
    # Recreate from dict
    recreated_step = StepFactory.from_dict(step_dict)
    print(f"Recreated step name: {recreated_step.name}")
    print(f"Recreated condition type: {recreated_step.condition_type}")
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    test_if_condition()