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
2. Configure API Keys (providers.json)
All API configurations and access credentials are managed directly inside the providers.json file. Open providers.json with your preferred text editor and add your API keys to the "api_key" field for the providers that require authorization:
```bash
{
  "unsplash": {
    "endpoint_url": "[https://api.unsplash.com/photos/random](https://api.unsplash.com/photos/random)",
    "auth_type": "param",
    "key_param": "client_id",
    "api_key": "YOUR_UNSPLASH_ACCESS_KEY",
    ...
  },
  "pexels": {
    "endpoint_url": "[https://api.pexels.com/v1/search](https://api.pexels.com/v1/search)",
    "auth_type": "header",
    "header_name": "Authorization",
    "api_key": "YOUR_PEXELS_API_KEY",
    ...
  }
}
```
## Usage
Basic Command Syntax
```bash
python3 fetch_photo_url.py -u <ENDPOINT_URL> -q <QUERY> -o <ORIENTATION>
```
## Examples
1. Query a random street photograph from Unsplash with log level DEBUG and log file:
```bash
python3 fetch_photo_url.py \
  -u unsplash \
  -q "street photography" \
  -o landscape \
  --log-level DEBUG \
  --log-file 20260907.log
```
2. Obtain a random architecture photograh from Pixabay (Grayscale Filtered) with WARNING logging:
```bash
python3 fetch_photo_url.py \
  -u pexels \
  -q "architecture" \
  --log-level WARNING
```
3. Obtain a random impressionism artwork from Pexels (Grayscale Filtered) with WARNING logging:
```bash
python3 fetch_photo_url.py \
  -u artic \
  -q "impressionism" \
  --log-level WARNING
```
## Piping and Script Integration
Fetch the URL and download the image directly to disk
```bash
IMAGE_URL=$(python3 fetch_photo_url.py -u unsplash -q "monochrome")
curl -s "$IMAGE_URL" -o output.jpg
```


