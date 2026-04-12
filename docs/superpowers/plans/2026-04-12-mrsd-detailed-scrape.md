# Mrsd Detailed Scrape Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add an `mrsd` detailed scrape variant with its own branch-specific keywords and Telegram destination, while keeping the scheduler on `main` through a dedicated GitHub Actions workflow.

**Architecture:** The implementation is split across two git contexts. `main` owns the new scheduled workflow file that checks out the `detailed-scrape-mrsd` branch, and the `detailed-scrape-mrsd` branch owns the branch-specific scraper values in `detailed_scrape_multi.py` and `detailed_scrape.py`. This keeps GitHub schedule compatibility while isolating the `mrsd` runtime behavior.

**Tech Stack:** Git, GitHub Actions, Python, existing scraper scripts

---

### Task 1: Create isolated worktree and branch

**Files:**
- Modify: `.gitignore`
- Create: `.worktrees/detailed-scrape-mrsd/`

- [ ] **Step 1: Verify `.worktrees/` is ignored**

```bash
git check-ignore -q .worktrees
echo $?
```

Expected: `0`

- [ ] **Step 2: Create the worktree and branch**

```bash
git worktree add .worktrees/detailed-scrape-mrsd -b detailed-scrape-mrsd
```

Expected: git reports a new worktree on branch `detailed-scrape-mrsd`

- [ ] **Step 3: Verify branch state inside the worktree**

```bash
git -C .worktrees/detailed-scrape-mrsd status --short --branch
```

Expected: `## detailed-scrape-mrsd`

- [ ] **Step 4: Run a baseline project check**

```bash
pytest
```

Expected: either a passing baseline or a clearly reported pre-existing failure before feature work continues

- [ ] **Step 5: Commit**

```bash
git add .gitignore
git commit -m "Ignore local worktrees directory"
```

Expected: already satisfied before this plan execution starts

### Task 2: Update scraper values on the `detailed-scrape-mrsd` branch

**Files:**
- Modify: `detailed_scrape_multi.py`
- Modify: `detailed_scrape.py`

- [ ] **Step 1: Write a failing regression check for the current branch-specific values**

```bash
python - <<'PY'
from pathlib import Path

content = Path("detailed_scrape_multi.py").read_text()
assert "-1003854188399" in content, "mrsd TARGET_CHAT_ID missing"
assert "'AMMN'" in content, "mrsd keyword list missing"
PY
```

Expected: FAIL before the `mrsd` branch values are added

- [ ] **Step 2: Update `detailed_scrape_multi.py` with the `mrsd` values**

```python
TARGET_CHAT_ID = "-1003854188399"

keywords = ['AMMN', 'ANTM', 'INCO', 'NCKL',
            'BRMS', 'BUMI', 'DEWA', 'ENRG',
            'BRPT', 'TPIA', 'BREN', 'ELSA',
            'ADRO', 'PTBA', 'AADI', 'MDKA',
            'MBMA', 'EMAS', 'INKP', 'BULL']
```

- [ ] **Step 3: Update `detailed_scrape.py` with the same `mrsd` values**

```python
TARGET_CHAT_ID = "-1003854188399"

keywords = ['AMMN', 'ANTM', 'INCO', 'NCKL',
            'BRMS', 'BUMI', 'DEWA', 'ENRG',
            'BRPT', 'TPIA', 'BREN', 'ELSA',
            'ADRO', 'PTBA', 'AADI', 'MDKA',
            'MBMA', 'EMAS', 'INKP', 'BULL']
```

- [ ] **Step 4: Re-run the regression check and verify it passes**

```bash
python - <<'PY'
from pathlib import Path

for path in ["detailed_scrape_multi.py", "detailed_scrape.py"]:
    content = Path(path).read_text()
    assert 'TARGET_CHAT_ID = "-1003854188399"' in content, f"{path} TARGET_CHAT_ID not updated"
    for keyword in ["AMMN", "ANTM", "INCO", "NCKL", "BRMS", "BUMI", "DEWA",
                    "ENRG", "BRPT", "TPIA", "BREN", "ELSA", "ADRO", "PTBA",
                    "AADI", "MDKA", "MBMA", "EMAS", "INKP", "BULL"]:
        assert f"'{keyword}'" in content, f"{path} missing keyword {keyword}"
PY
```

Expected: no output and exit code `0`

- [ ] **Step 5: Commit**

```bash
git -C .worktrees/detailed-scrape-mrsd add detailed_scrape_multi.py detailed_scrape.py
git -C .worktrees/detailed-scrape-mrsd commit -m "Configure mrsd detailed scrape targets"
```

### Task 3: Add the `mrsd` scheduler workflow on `main`

**Files:**
- Create: `.github/workflows/detailed_scrape_multiprocess_mrsd.yml`

- [ ] **Step 1: Write a failing file existence check**

```bash
test -f .github/workflows/detailed_scrape_multiprocess_mrsd.yml
```

Expected: exit code `1`

- [ ] **Step 2: Add the workflow file**

```yaml
name: Detailed Scrape Multiprocess Mrsd
on:
  schedule:
    # 22:45 WIB (Asia/Jakarta)
    - cron: '45 15 * * *'
    # 07:55 WIB (Asia/Jakarta)
    - cron: '55 0 * * *'
    # 12:30 WIB (Asia/Jakarta)
    - cron: '30 5 * * *'
    # 15:00 WIB (Asia/Jakarta)
    - cron: '0 8 * * *'
  workflow_dispatch:

jobs:
  build:
    env:
      PY_COLORS: "1"
    strategy:
      fail-fast: false
      max-parallel: 1
      matrix:
        os: [ubuntu-22.04]
        python-version: ["3.13"]

    runs-on: ${{ matrix.os }}
    steps:
    - uses: actions/checkout@v4
      with:
        ref: detailed-scrape-mrsd
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v5
      with:
        python-version: ${{ matrix.python-version }}
    - name: Set Locale
      if: runner.os == 'Linux'
      run: |
        sudo apt-get install tzdata locales -y && sudo locale-gen en_US.UTF-8
        sudo localectl set-locale LANG="en_US.UTF-8"
        export LANG="en_US.UTF-8"
        sudo update-locale
        locale -a
        locale
        locale -c -k LC_NUMERIC
        localectl status
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install --upgrade pip
        pip install --upgrade wheel
        pip install -r requirements.txt
        pip install --upgrade pyautogui
    - name: Install extra dependencies
      if: runner.os == 'Linux'
      run: |
        pip install --upgrade python-xlib
    - name: Install Chrome
      if: matrix.os == 'ubuntu-22.04'
      run: |
        sudo apt install google-chrome-stable
    - name: Check the console scripts interface
      run: |
        seleniumbase
        sbase
    - name: Install chromedriver
      run: |
        seleniumbase install chromedriver
    - name: Make sure pytest is working
      run: |
        echo "def test_1(): pass" > nothing.py
        pytest nothing.py --uc
    - name: Check which Chrome binaries exist
      run: |
        python -c "import os; print(os.path.exists('/usr/bin/google-chrome'))"
        python -c "import os; print(os.path.exists('/bin/google-chrome-stable'))"
        python -c "import os; print(os.path.exists('/bin/chromium-browser'))"
        python -c "import os; print(os.path.exists('/bin/chromium'))"
    - name: Display Chrome binary that's used
      run: |
        python -c "from seleniumbase.core import detect_b_ver; print(detect_b_ver.get_binary_location('google-chrome'))"
        python -c "from seleniumbase import undetected; print(undetected.find_chrome_executable())"
    - name: Make sure pytest with sb is working
      run: |
        echo "def test_0(sb): pass" > verify_sb.py
        pytest verify_sb.py
    - name: Run python detailed_scrape_multi.py --debug
      env:
        PROXY_USER: ${{ secrets.PROXY_USER }}
        PROXY_PASSWORD: ${{ secrets.PROXY_PASSWORD }}
        PROXY_HOST: ${{ secrets.PROXY_HOST }}
        PROXY_PORT: ${{ secrets.PROXY_PORT }}
        BOT_TOKEN: ${{ secrets.BOT_TOKEN }}
        SA_PRIVKEY_ID: ${{ secrets.SA_PRIVKEY_ID }}
        SA_PRIVKEY: ${{ secrets.SA_PRIVKEY }}
        SA_CLIENTMAIL: ${{ secrets.SA_CLIENTMAIL }}
        SA_CLIENT_X509_URL: ${{ secrets.SA_CLIENT_X509_URL }}
        DEEPSEEK_APIKEY: ${{ secrets.DEEPSEEK_APIKEY }}
      run: |
        python detailed_scrape_multi.py --debug
```

- [ ] **Step 3: Verify the workflow file now exists and points at the correct branch**

```bash
python - <<'PY'
from pathlib import Path

content = Path(".github/workflows/detailed_scrape_multiprocess_mrsd.yml").read_text()
assert "Detailed Scrape Multiprocess Mrsd" in content
assert "ref: detailed-scrape-mrsd" in content
for cron in ["45 15 * * *", "55 0 * * *", "30 5 * * *", "0 8 * * *"]:
    assert cron in content, f"missing cron {cron}"
PY
```

Expected: no output and exit code `0`

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/detailed_scrape_multiprocess_mrsd.yml
git commit -m "Add mrsd detailed scrape workflow"
```

### Task 4: Verify both git contexts are ready

**Files:**
- Modify: none

- [ ] **Step 1: Verify `main` branch status**

```bash
git status --short --branch
```

Expected: `main` with only intended commits and no accidental file drift from the worktree

- [ ] **Step 2: Verify `detailed-scrape-mrsd` branch status**

```bash
git -C .worktrees/detailed-scrape-mrsd status --short --branch
```

Expected: `detailed-scrape-mrsd` with only intended commits and no unexpected modifications

- [ ] **Step 3: Verify the new workflow syntax**

```bash
python - <<'PY'
from pathlib import Path
import yaml

workflow = Path(".github/workflows/detailed_scrape_multiprocess_mrsd.yml")
yaml.safe_load(workflow.read_text())
PY
```

Expected: no output and exit code `0`

- [ ] **Step 4: Verify the `mrsd` branch scraper values one final time**

```bash
python - <<'PY'
from pathlib import Path

base = Path(".worktrees/detailed-scrape-mrsd")
for path in [base / "detailed_scrape_multi.py", base / "detailed_scrape.py"]:
    content = path.read_text()
    assert 'TARGET_CHAT_ID = "-1003854188399"' in content
    assert "'AMMN'" in content
    assert "'BULL'" in content
PY
```

Expected: no output and exit code `0`
