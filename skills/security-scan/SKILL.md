---
name: security-scan
description: Scans code for security vulnerabilities before they reach production. Use this skill whenever the user asks to check for security issues, vulnerabilities, or security problems in their code — including phrases like "scan for vulnerabilities", "security review", "check for bugs", "is this code safe", "before I push this", "pentest my code", "security audit", "look for XSS/SQLi/injection", or any time the user is about to deploy or open a PR. Also trigger proactively when the user is writing authentication, database queries, file handling, API routes, or anything that touches user input.
argument-hint: [path or file to scan]
---

# Security Scan

Scan JavaScript/TypeScript and Python codebases for security vulnerabilities before they reach production. Combines automated tooling with targeted code review covering the OWASP Top 10 and language-specific attack patterns.

## Workflow

### Step 0: Detect project context

Before scanning, figure out what you're working with:

```bash
# Detect project type
ls package.json pyproject.toml requirements.txt setup.py 2>/dev/null

# Understand scope — what path are we scanning?
# If the user gave a path via $ARGUMENTS, use that. Otherwise scan the current directory.
```

If `$ARGUMENTS` is provided, treat it as the root path to scan. Otherwise use the current working directory.

### Step 1: Run automated tools (where available)

Auto-detect what's installed and run everything you can — don't ask first, just run and report what you used.

**JavaScript / TypeScript — dependency vulnerabilities:**
```bash
# Always available if package.json exists
npm audit --json 2>/dev/null
```

**Semgrep — static analysis for both JS/TS and Python (if installed):**
```bash
which semgrep && semgrep --config=p/security-audit --json 2>/dev/null
```

**Bandit — Python static analysis (if installed):**
```bash
which bandit && bandit -r . -f json 2>/dev/null
```

When a tool isn't installed, note it in the report under "Tools not available" and explain what it would have caught. Don't block — move on to the next step.

### Step 2: Claude-native code review

Automated tools catch known patterns but miss logic flaws and subtle misconfigurations. After running the tools, do your own targeted review of the most sensitive areas.

**Where to look first:**
- Authentication and session management (login, logout, token issuance, password reset)
- Database queries (anywhere user input flows into a query)
- File operations (uploads, downloads, path construction)
- API route handlers (especially ones that skip auth middleware)
- Configuration files (secrets, credentials, environment variables)
- Input parsing (JSON, XML, multipart forms)

**Grep for high-signal patterns:**

For JavaScript/TypeScript:
```bash
# Injection risks
grep -rn "innerHTML\|dangerouslySetInnerHTML\|eval(\|new Function(" --include="*.js" --include="*.ts" --include="*.jsx" --include="*.tsx" .

# Command injection
grep -rn "exec(\|execSync(\|spawn(" --include="*.js" --include="*.ts" .

# Hardcoded secrets
grep -rn "password\s*=\s*['\"][^'\"]\|api_key\s*=\s*['\"][^'\"]\|secret\s*=\s*['\"][^'\"]" --include="*.js" --include="*.ts" -i .

# SQL via string concatenation
grep -rn "query\s*=.*+\|execute(.*+\|db\.query.*\$" --include="*.js" --include="*.ts" .
```

For Python:
```bash
# Injection risks
grep -rn "os\.system\|subprocess.*shell=True\|eval(\|exec(" --include="*.py" .

# SQL injection
grep -rn "cursor\.execute.*%" --include="*.py" .

# Insecure deserialization
grep -rn "pickle\.loads\|yaml\.load(" --include="*.py" .

# Weak crypto / random
grep -rn "import random\|md5(\|sha1(" --include="*.py" .
```

Read the files around each hit — the one-line match rarely tells the whole story. Focus your reading time on files where user-controlled data enters the system.

### Step 3: Write the vulnerability report

After gathering all findings, produce a prioritized report. **Always produce the full report even if no vulnerabilities are found** — "no issues found" is a valid and useful result.

Use this structure:

---

## Security Scan Report

**Scanned:** `[path]`
**Languages detected:** [JS/TS | Python | Mixed]
**Tools run:** [npm audit | semgrep | bandit | none]
**Tools not available:** [list with install command]

---

### Summary

| Severity | Count |
|----------|-------|
| Critical | N |
| High     | N |
| Medium   | N |
| Low      | N |
| Info     | N |

[One sentence overall assessment — e.g. "Two high-severity injection risks need immediate attention before deploying."]

---

### Findings

For each finding, use this format:

**[SEVERITY] [Finding title]**
`file/path.ts:42`

[What the vulnerability is and why it's dangerous — explain it plainly, not just the CVE name.]

```
[Relevant code snippet showing the issue]
```

**Fix:** [Concrete remediation — show the corrected code where possible, not just "sanitize input".]

---

### Tools not available

[For each tool not installed, explain what it would have checked and how to install it.]

```bash
# Install semgrep for static analysis (JS, TS, Python + more)
pip3 install semgrep

# Install bandit for Python security linting
pip3 install bandit
```

---

## Severity guidelines

Use these when deciding severity — the risk to production is what matters, not just theoretical exploitability:

| Severity | Meaning |
|----------|---------|
| **Critical** | Remotely exploitable with no auth, or direct path to data exfiltration / RCE |
| **High** | Exploitable by authenticated users, or enables privilege escalation |
| **Medium** | Requires specific conditions but real-world exploitable |
| **Low** | Defense-in-depth issue; unlikely to be exploited alone |
| **Info** | Best practice deviation, no direct exploit path |

## What to look for (cheat sheet)

### JavaScript / TypeScript

| Pattern | Risk | Look for |
|---------|------|----------|
| `innerHTML = userInput` | XSS | DOM manipulation with unsanitized data |
| `eval()`, `new Function()` | Code injection | Dynamic code execution |
| String-concatenated SQL | SQL injection | `"SELECT * WHERE id = " + req.params.id` |
| `child_process.exec()` with user input | Command injection | Shell commands built from request data |
| JWT `alg: none` or weak secret | Auth bypass | JWT verification code |
| Missing `httpOnly` / `secure` on cookies | Session hijack | Cookie configuration |
| `path.join()` with user input unchecked | Path traversal | File serving routes |
| Hardcoded secrets in source | Credential leak | `apiKey = "sk-..."` |
| `res.redirect(req.query.url)` | Open redirect | Redirect handlers |
| Missing rate limiting on auth routes | Brute force | Login / password reset endpoints |

### Python

| Pattern | Risk | Look for |
|---------|------|----------|
| `cursor.execute("... %s" % user_input)` | SQL injection | Old-style string formatting in queries |
| `os.system(user_input)` | Command injection | Shell calls with user data |
| `subprocess.run(..., shell=True)` | Command injection | When combined with user input |
| `pickle.loads(user_data)` | RCE via deserialization | Any pickle from external sources |
| `yaml.load()` without `Loader=yaml.SafeLoader` | Code execution | YAML parsing |
| `eval(user_input)` | Code execution | Dynamic evaluation |
| `import random` for tokens / passwords | Weak randomness | Should use `secrets` module |
| `hashlib.md5(password)` | Weak hashing | Password storage |
| Hardcoded credentials | Credential leak | `PASSWORD = "hunter2"` |
| `open(user_path)` without validation | Path traversal | File read/write routes |

## Notes on scope

- If the user asks to scan a specific file or directory, focus there — don't scan the entire repo.
- If the repo is large (>500 files), prioritize the grep patterns and read the riskiest files rather than trying to read everything.
- Dependency vulnerabilities from `npm audit` are always worth reporting, even for medium/low severity — the fix is usually just `npm audit fix`.
- Don't report linting issues, code style, or performance problems — those aren't security vulnerabilities.
