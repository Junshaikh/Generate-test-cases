# Generate Gherkin Test Cases CLI Tool

A simple command-line tool to generate clean Gherkin-format software test cases from natural language requirements using Google's Gemini API, and optionally upload them to GitHub.

---

## 🚀 Features

* Generate test cases in plain, clean Gherkin format
* No markdown or extra labels like `**Scenario 1**`
* Auto-suggest filenames from requirement
* Prevent overwriting existing files
* Optional upload to GitHub (configurable)
* CLI arguments support
* .env-based configuration for secrets and environment variables

---

## 📦 Installation

### 1. Clone the Repo

```bash
git clone https://github.com/your-org/generate-tests-cli.git
cd generate-tests-cli
```

### 2. Set Up Environment Variables

Copy the example file:

```bash
cp .env.example .env
```

Then edit `.env` to add your credentials:

```env
GOOGLE_API_KEY=your-gemini-api-key
GITHUB_TOKEN=your-github-token
GITHUB_REPO_OWNER=your-github-username-or-org
GITHUB_REPO_NAME=your-repository-name
GITHUB_BRANCH=main
```

> ✅ Use `.env.example` for sharing config format and add `.env` to `.gitignore`

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Install Locally as CLI

```bash
pip install -e .
```

---

## 🧪 Usage

### Basic

```bash
generate-tests -r "Reset password" -s "squad-auth" -f "reset_password"
```

### With GitHub Upload Disabled

```bash
generate-tests -r "Reset password" -s "squad-auth" -f "reset_password" --no-github
```

### CLI Options

| Flag                  | Description                          |
| --------------------- | ------------------------------------ |
| `-r`, `--requirement` | Requirement description *(required)* |
| `-s`, `--squad`       | Squad nam                            |

