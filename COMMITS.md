## Format
Follow Conventional Commits:

```
<type>: <short description>

<optional body: what changed and why, list subtasks if milestone commit>
```

# Types
- `feat:` new feature
- `fix:` bug fix
- `refactor:` restructuring without behavior change
- `docs:` documentation only
- `chore:` tooling, deps, config
- `test:` tests
- `style:` formatting only


## Examples

Good:
```
feat: placeholder substitution

- Added sensitive field list to persona.ts
- Replaced phone, address, email with placeholders before prompt construction
- Injected real values into LaTeX output post-generation
```
