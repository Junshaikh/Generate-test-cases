# 🔪 Generate Test Cases CLI

A command-line tool that converts software requirements into clean, production-ready Gherkin test cases using **Gemini Pro (Google Generative AI)** and optionally uploads them directly to **GitHub**.

---

## 🚀 Features

* ✅ CLI-friendly interface — ideal for CI/CD or manual QA flows
* ✨ Auto-suggested test file names
* 🧼 Clean Gherkin output (no markdown or scenario labels)
* 🔐 .env-based configuration for secure key management
* ☁️ Optional GitHub commit/upload with preview link
* 🏷️ Organized by squad folders in `test-cases/`

---

## 📆 Installation

```bash
# Clone the repo
git clone https://github.com/junshaikh/generate-test-cases.git
cd generate-test-cases

# Install the CLI locally (editable mode)
pip install -e .
```

---

## ⚙️ Required Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# Gemini API Key
GOOGLE_API_KEY=your_gemini_api_key_here
# GitHub (optional, only needed for uploads)
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_REPO_OWNER=your_github_username_or_org
GITHUB_REPO_NAME=your_repo_name
GITHUB_BRANCH=main
```

> **Note:** You can generate your Gemini key from:
> 👉 [https://aistudio.google.com/app/apikey](https://aistudio.google.com/app/apikey)

> To generate a GitHub token:
> 👉 [https://github.com/settings/tokens](https://github.com/settings/tokens)
> ✅ Enable `repo` scope (for uploading files to a repo)

---

## 🧲 Usage

Basic example:

```
generate-tests --requirement "Reset password with email" --squad "squad-auth"
```

With a custom file name:

```
generate-tests -r "Reset password" -s "squad-auth" -f "reset_password"
```

Disable GitHub upload:

```
generate-tests -r "Reset password" -s "squad-auth" --no-upload
```

---

## 📁 Output Structure

Files are saved under:

```
test-cases/
  └── squad-auth/
        └── reset_password.txt
```

---

## 🔐 Keeping .env Secure

Add `.env` to your `.gitignore` to prevent accidental commits:

```gitignore
.env
```

---

## 💡 Example Output (Gherkin)

```gherkin
Feature: Reset password

  Scenario: User resets password with email
    Given the user is on the login page
    When the user clicks "Forgot Password"
    And enters a valid email address
    Then a password reset link is sent
```

---

## 🧰 Troubleshooting

* **404 GitHub upload error?**
  Double-check your repo name, owner, and token scopes.

* **Nothing runs?**
  Make sure you’re using Python 3.8+, `.env` is loaded, and dependencies installed.

---

## ✨ Credits

Created by [@junshaikh](https://github.com/junshaikh) — inspired by manual QA pain 😅

---

## 📄 License

MIT License. Use freely and improve collaboratively.
