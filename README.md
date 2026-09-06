# multi-provider-url-image-fetcher

A lightweight, provider-agnostic Python CLI tool that fetches raw image and artwork URLs from multiple public APIs (Unsplash, Pixabay, Pexels, Art Institute of Chicago, Giphy, and more). 

Designed specifically for e-Paper / e-Ink displays (like Waveshare) and automation pipelines where only a clean URL string is needed on `stdout`.

## Features

- **Provider Agnostic:** Configured via a simple `providers.json` mapping file using dot-notation JSON paths.
- **Clean Piping (`stdout` vs `stderr`):** Outputs strictly the resolved image URL string to `stdout`, while logging HTTP request inspection details and errors to `stderr`.
- **Built-in Security:** Automatically masks sensitive API keys in debug/logging output to prevent credentials leakage in logs.
- **Flexible Precedence:** Resolves API Keys via CLI argument > `API_KEY` env variable > `UNSPLASH_ACCESS_KEY` env variable > `.env` file.

---

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rbustos567/multi-provider-url-image-fetcher.git
   cd multi-provider-url-image-fetcher
---

1. Install dependencies
```bash
pip install requests
```
2. (Optional) Configure environment variables:
   Create a .env file in the root directory:
```bash
API_KEY=your_generic_api_key_here
```
