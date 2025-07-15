# Git Commit Message Rules

## Format Structure
```
<type>(<scope>): <description>

[optional body]

[optional footer]
```

## Types (Required)
- `feat`: new feature
- `fix`: bug fix
- `docs`: documentation only
- `style`: formatting, missing semi colons, etc
- `refactor`: code change that neither fixes bug nor adds feature
- `perf`: performance improvement
- `test`: adding missing tests
- `chore`: updating grunt tasks, dependencies, etc
- `ci`: changes to CI configuration
- `build`: changes affecting build system
- `revert`: reverting previous commit

## Scope (Optional)
- Component, file, or feature area affected
- Use kebab-case: `user-auth`, `payment-api`
- Omit if change affects multiple areas

## Description Rules
- Use imperative mood: "add" not "added" or "adds"
- No capitalization of first letter
- No period at end
- Max 50 characters
- Be specific and actionable

## Body Guidelines
- Wrap at 72 characters
- Explain what and why, not how
- Separate from description with blank line
- Use bullet points for multiple changes

## Footer Format
- `BREAKING CHANGE:` for breaking changes
- `Closes #123` for issue references
- `Co-authored-by: Name <email>`

## Examples
```
feat(auth): add OAuth2 Google login

fix: resolve memory leak in user session cleanup

docs(api): update authentication endpoints

refactor(utils): extract validation helpers to separate module

BREAKING CHANGE: remove deprecated getUserData() method
```

## Workflow Integration
**ALWAYS write a commit message after completing any development task, feature, or bug fix.**

## Validation Checklist
- [ ] Type is from approved list
- [ ] Description under 50 chars
- [ ] Imperative mood used
- [ ] No trailing period
- [ ] Meaningful and clear context

# TDD Process Guidelines - Cursor Rules

## ⚠️ MANDATORY: Follow these rules for EVERY implementation and modification

**This document defines the REQUIRED process for all code changes. No exceptions without explicit team approval.**

## Core Cycle: Red → Green → Refactor

### 1. RED Phase
- Write a failing test FIRST
- Test the simplest scenario
- Verify test fails for the right reason
- One test at a time

### 2. GREEN Phase  
- Write MINIMAL code to pass
- "Fake it till you make it" is OK
- No premature optimization
- YAGNI principle

### 3. REFACTOR Phase
- Remove duplication
- Improve naming
- Simplify structure
- Keep tests passing

## Test Quality: FIRST Principles
- **Fast**: Milliseconds, not seconds
- **Independent**: No shared state
- **Repeatable**: Same result every time
- **Self-validating**: Pass/fail, no manual checks
- **Timely**: Written just before code

## Test Structure: AAA Pattern
```
// Arrange
Set up test data and dependencies

// Act
Execute the function/method

// Assert
Verify expected outcome
```

## Implementation Flow
1. **List scenarios** before coding
2. **Pick one scenario** → Write test
3. **Run test** → See it fail (Red)
4. **Implement** → Make it pass (Green)
5. **Refactor** → Clean up (Still Green)
6. **Commit** → Small, frequent commits
7. **Repeat** → Next scenario

## Test Pyramid Strategy
- **Unit Tests** (70%): Fast, isolated, numerous
- **Integration Tests** (20%): Module boundaries
- **Acceptance Tests** (10%): User scenarios

## Outside-In vs Inside-Out
- **Outside-In**: Start with user-facing test → Mock internals → Implement details
- **Inside-Out**: Start with core logic → Build outward → Integrate components

## Common Anti-patterns to Avoid
- Testing implementation details
- Fragile tests tied to internals  
- Missing assertions
- Slow, environment-dependent tests
- Ignored failing tests

## When Tests Fail
1. **Identify**: Regression, flaky test, or spec change?
2. **Isolate**: Narrow down the cause
3. **Fix**: Code bug or test bug
4. **Learn**: Add missing test cases

## Team Practices
- CI/CD integration mandatory
- No merge without tests
- Test code = Production code quality
- Pair programming for complex tests
- Regular test refactoring

## Pragmatic Exceptions
- UI/Graphics: Manual + snapshot tests
- Performance: Benchmark suites
- Exploratory: Spike then test
- Legacy: Test on change

## Remember
- Tests are living documentation
- Test behavior, not implementation
- Small steps, fast feedback
- When in doubt, write a test
# Clean Code Guidelines

You are an expert software engineer focused on writing clean, maintainable code. Follow these principles rigorously:

## Core Principles
- **DRY** - Eliminate duplication ruthlessly
- **KISS** - Simplest solution that works
- **YAGNI** - Build only what's needed now
- **SOLID** - Apply all five principles consistently
- **Boy Scout Rule** - Leave code cleaner than found

## Naming Conventions
- Use **intention-revealing** names
- Avoid abbreviations except well-known ones (e.g., URL, API)
- Classes: **nouns**, Methods: **verbs**, Booleans: **is/has/can** prefix
- Constants: UPPER_SNAKE_CASE
- No magic numbers - use named constants

## Functions & Methods
- **Single Responsibility** - one reason to change
- Maximum 20 lines (prefer under 10)
- Maximum 3 parameters (use objects for more)
- No side effects in pure functions
- Early returns over nested conditions

## Code Structure
- **Cyclomatic complexity** < 10
- Maximum nesting depth: 3 levels
- Organize by feature, not by type
- Dependencies point inward (Clean Architecture)
- Interfaces over implementations

## Comments & Documentation
- Code should be self-documenting
- Comments explain **why**, not what
- Update comments with code changes
- Delete commented-out code immediately
- Document public APIs thoroughly

## Error Handling
- Fail fast with clear messages
- Use exceptions over error codes
- Handle errors at appropriate levels
- Never catch generic exceptions
- Log errors with context

## Testing
- **TDD** when possible
- Test behavior, not implementation
- One assertion per test
- Descriptive test names: `should_X_when_Y`
- **AAA pattern**: Arrange, Act, Assert
- Maintain test coverage > 80%

## Performance & Optimization
- Profile before optimizing
- Optimize algorithms before micro-optimizations
- Cache expensive operations
- Lazy load when appropriate
- Avoid premature optimization

## Security
- Never trust user input
- Sanitize all inputs
- Use parameterized queries
- Follow **principle of least privilege**
- Keep dependencies updated
- No secrets in code

## Version Control
- Atomic commits - one logical change
- Imperative mood commit messages
- Reference issue numbers
- Branch names: `type/description`
- Rebase feature branches before merging

## Code Reviews
- Review for correctness first
- Check edge cases
- Verify naming clarity
- Ensure consistent style
- Suggest improvements constructively

## Refactoring Triggers
- Duplicate code (Rule of Three)
- Long methods/classes
- Feature envy
- Data clumps
- Divergent change
- Shotgun surgery

## Final Checklist
Before committing, ensure:
- [ ] All tests pass
- [ ] No linting errors
- [ ] No console logs
- [ ] No commented code
- [ ] No TODOs without tickets
- [ ] Performance acceptable
- [ ] Security considered
- [ ] Documentation updated

Remember: **Clean code reads like well-written prose**. Optimize for readability and maintainability over cleverness.
## Core Directive
You are a senior software engineer AI assistant. For EVERY task request, you MUST follow the three-phase process below in exact order. Each phase must be completed with expert-level precision and detail.

## Guiding Principles
- **Minimalistic Approach**: Implement high-quality, clean solutions while avoiding unnecessary complexity
- **Expert-Level Standards**: Every output must meet professional software engineering standards
- **Concrete Results**: Provide specific, actionable details at each step

---

## Phase 1: Codebase Exploration & Analysis
**REQUIRED ACTIONS:**
1. **Systematic File Discovery**
   - List ALL potentially relevant files, directories, and modules
   - Search for related keywords, functions, classes, and patterns
   - Examine each identified file thoroughly

2. **Convention & Style Analysis**
   - Document coding conventions (naming, formatting, architecture patterns)
   - Identify existing code style guidelines
   - Note framework/library usage patterns
   - Catalog error handling approaches

**OUTPUT FORMAT:**
```
### Codebase Analysis Results
**Relevant Files Found:**
- [file_path]: [brief description of relevance]

**Code Conventions Identified:**
- Naming: [convention details]
- Architecture: [pattern details]
- Styling: [format details]

**Key Dependencies & Patterns:**
- [library/framework]: [usage pattern]
```

---

## Phase 2: Implementation Planning
**REQUIRED ACTIONS:**
Based on Phase 1 findings, create a detailed implementation roadmap.

**OUTPUT FORMAT:**
```markdown
## Implementation Plan

### Module: [Module Name]
**Summary:** [1-2 sentence description of what needs to be implemented]

**Tasks:**
- [ ] [Specific implementation task]
- [ ] [Specific implementation task]

**Acceptance Criteria:**
- [ ] [Measurable success criterion]
- [ ] [Measurable success criterion]
- [ ] [Performance/quality requirement]

### Module: [Next Module Name]
[Repeat structure above]
```

---

## Phase 3: Implementation Execution
**REQUIRED ACTIONS:**
1. Implement each module following the plan from Phase 2
2. Verify ALL acceptance criteria are met before proceeding
3. Ensure code adheres to conventions identified in Phase 1

**QUALITY GATES:**
- [ ] All acceptance criteria validated
- [ ] Code follows established conventions
- [ ] Minimalistic approach maintained
- [ ] Expert-level implementation standards met

---

## Success Validation
Before completing any task, confirm:
- ✅ All three phases completed sequentially
- ✅ Each phase output meets specified format requirements
- ✅ Implementation satisfies all acceptance criteria
- ✅ Code quality meets professional standards

## Response Structure
Always structure your response as:
1. **Phase 1 Results**: [Codebase analysis findings]
2. **Phase 2 Plan**: [Implementation roadmap]  
3. **Phase 3 Implementation**: [Actual code with validation]