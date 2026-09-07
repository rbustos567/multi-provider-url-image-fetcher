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
## Configuration (providers.json)
The script dynamically matches the target URL domain against providers.json to construct query parameters, set authorization headers, and parse response JSON paths.
```bash
{
  "unsplash": {
    "domains": ["api.unsplash.com"],
    "auth_type": "param",
    "key_param": "client_id",
    "query_param": "query",
    "orientation_param": "orientation",
    "extra_params": { "color": "black_and_white" },
    "json_path": "urls.regular"
  },
  "pexels": {
    "domains": ["api.pexels.com"],
    "auth_type": "header",
    "header_name": "Authorization",
    "query_param": "query",
    "orientation_param": "orientation",
    "extra_params": { "per_page": 15 },
    "json_path": "photos.0.src.large",
    "randomize_list": "photos"
  }
}
```
## Usage
Basic Command Syntax
```bash
python3 fetch_photo_url.py -u <ENDPOINT_URL> -k <API_KEY> -q <QUERY> -o <ORIENTATION>
```
## Examples
1. Fetch from Unsplash (B&W Street Photography) with DEBUG logging and output log:
```bash
python3 fetch_photo_url.py \
  -u "https://api.unsplash.com/photos/random" \
  -k "YOUR_UNSPLASH_KEY" \
  -q "street photography" \
  -o landscape \
  --log-level DEBUG \
  --log-file 20260907.log
```
2. Fetch from Pixabay (Grayscale Filtered) with WARNING logging:
```bash
python3 fetch_photo_url.py \
  -u "https://pixabay.com/api/" \
  -k "YOUR_PIXABAY_KEY" \
  -q "architecture" \
  --log-level WARNING
```
3. Fetch from Pexels (Grayscale Filtered) with WARNING logging:
```bash
python3 fetch_photo_url.py \
  -u "https://api.pexels.com/v1/search" \
  -k "YOUR_PEXELS_KEY" \
  -q "architecture" \
  --log-level WARNING
```
4. Fetch Classic Artwork (Art Institute of Chicago - No Key Required):
```bash
python3 fetch_photo_url.py \
  -u "https://api.artic.edu/api/v1/artworks/search" \
  -q "Claude Monet"
```
## Integration with e-Paper Display Pipelines
Capture the output URL directly into a shell variable or download stream:
```bash
# Capture clean URL string
IMAGE_URL=$(./fetch_photo_url.py -q "minimalist nature")

# Download directly and pass to e-Paper rendering engine
curl -s "$IMAGE_URL" -o current_display.jpg
python3 display_render.py current_display.jpg
```
