# epaper-image-fetcher

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
   git clone [https://github.com/rbustos567/epaper-image-fetcher.git](https://github.com/your-username/epaper-image-fetcher.git)
   cd epaper-image-fetcher
