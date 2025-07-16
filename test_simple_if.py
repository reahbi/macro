#!/usr/bin/env python3
"""
Simple test for if condition logic
"""

# Test variable comparison logic
def test_variable_comparison():
    """Test variable comparison operations"""
    
    # Test data
    variables = {
        'name': '홍길동',
        'age': '25',
        'score': '85.5',
        'department': '의료정보팀'
    }
    
    print("=== Variable Comparison Tests ===")
    
    # Test equals
    print(f"\nTest: age == '25' -> {variables['age'] == '25'}")
    print(f"Test: age == '30' -> {variables['age'] == '30'}")
    
    # Test contains
    print(f"\nTest: '의료' in department -> {'의료' in variables['department']}")
    print(f"Test: '영업' in department -> {'영업' in variables['department']}")
    
    # Test numeric comparison
    age_val = float(variables['age'])
    print(f"\nTest: age > 20 -> {age_val > 20}")
    print(f"Test: age < 30 -> {age_val < 30}")
    
    # Test variable substitution pattern
    import re
    
    def substitute_variables(text, vars):
        pattern = r'\{\{(\w+)\}\}'
        def replacer(match):
            var_name = match.group(1)
            return str(vars.get(var_name, match.group(0)))
        return re.sub(pattern, replacer, text)
    
    # Test substitution
    text = "{{name}}님의 나이는 {{age}}세입니다."
    result = substitute_variables(text, variables)
    print(f"\nTemplate: {text}")
    print(f"Result: {result}")
    
    # Test nested substitution
    variables['threshold'] = '80'
    compare_text = "{{threshold}}"
    compare_value = substitute_variables(compare_text, variables)
    score_val = float(variables['score'])
    threshold_val = float(compare_value)
    
    print(f"\nTest: score ({score_val}) > threshold ({threshold_val}) -> {score_val > threshold_val}")

if __name__ == "__main__":
    test_variable_comparison()