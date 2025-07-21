@echo off
echo ===============================================
echo    Macro Notification System Test Suite
echo ===============================================
echo.

echo [1/3] Running basic component tests...
echo ---------------------------------------
python test_simple_check.py
echo.
pause

echo [2/3] Running feature-specific tests...
echo ---------------------------------------
python test_features_check.py
echo.
pause

echo [3/3] Running floating widget demo...
echo ---------------------------------------
python test_floating_widget.py
echo.
echo Note: Close the floating widget demo window to continue.
pause

echo ===============================================
echo    All tests completed!
echo    Check NOTIFICATION_SYSTEM_FINAL_TEST_REPORT.md
echo    for detailed results.
echo ===============================================
pause