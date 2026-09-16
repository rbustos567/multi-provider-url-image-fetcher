#!/usr/bin/env python3
"""Generic Multi-Provider Photo & Art URL Fetcher for e-Paper.

Fetches image URLs dynamically using a providers.json mapping configuration.
Supports target provider resolution via shorthand alias (e.g., 'pexels') or full URL.
Outputs strictly the final raw image URL string to stdout (when successful),
while logging request details and system events based on the configured log level and output.
"""

import argparse
import json
import logging
import os
import random
import sys
from pathlib import Path
from typing import Any, Dict, Optional
import requests


def setup_logging(level_name: str, log_file: Optional[str] = None) -> None:
    """Configures the root logger with specified log level and handler (file or stderr)."""
    numeric_level = getattr(logging, level_name.upper(), logging.INFO)

    handlers = []
    if log_file:
        handlers.append(logging.FileHandler(log_file, encoding="utf-8"))
    else:
        # Default to stderr to keep stdout clean for URL piping
        handlers.append(logging.StreamHandler(sys.stderr))

    # Reset any existing handlers
    logging.root.handlers = []

    logging.basicConfig(
        level=numeric_level,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=handlers,
    )


def load_env_file(env_path: str = ".env") -> None:
    """Parse key=value pairs from .env if present."""
    path = Path(env_path)
    if path.is_file():
        logging.debug("Loading environment variables from %s", env_path)
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, val = line.split("=", 1)
                    os.environ.setdefault(
                        key.strip(), val.strip().strip("\"'")
                    )


def resolve_access_key(cfg: Optional[Dict[str, Any]] = None) -> Optional[str]:
    """Resolves API Key: JSON api_key > API_KEY / UNSPLASH_ACCESS_KEY env / .env file."""
    if cfg and cfg.get("api_key"):
        logging.debug("API key resolved from provider JSON configuration.")
        return cfg["api_key"]

    load_env_file()
    key = os.getenv("API_KEY") or os.getenv("UNSPLASH_ACCESS_KEY")
    if key:
        logging.debug("API key resolved from environment variables / .env file.")
    else:
        logging.warning("No API key could be resolved from configuration or environment.")
    return key


def mask_sensitive_value(value: str) -> str:
    """Masks API Key or Token for safe logging."""
    if not value or len(value) <= 8:
        return "***MASKED***"
    return f"{value[:4]}...{value[-4:]}"


def get_nested_value(data: Any, path: str) -> Any:
    """Extracts a value from a nested dict/list using dot-notation (e.g., 'hits.0.largeImageURL')."""
    keys = path.split(".")
    curr = data
    for key in keys:
        if isinstance(curr, list):
            try:
                idx = int(key)
                curr = curr[idx]
            except (ValueError, IndexError):
                logging.debug("Failed to index list using key '%s' in path '%s'", key, path)
                return None
        elif isinstance(curr, dict):
            curr = curr.get(key)
            if curr is None:
                logging.debug("Key '%s' not found in dictionary for path '%s'", key, path)
                return None
        else:
            return None
    return curr


def load_providers(config_path: str = "providers.json") -> Dict[str, Any]:
    """Loads provider mappings from JSON file."""
    path = Path(config_path)
    if not path.is_file():
        logging.warning("Configuration file '%s' not found.", config_path)
        sys.exit(1)
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logging.debug("Successfully loaded configuration from '%s'", config_path)
            return data
    except Exception as exc:
        logging.warning("Failed to parse config file '%s': %s", config_path, exc)
        sys.exit(1)


def find_matching_provider(target: str, providers: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    """Matches provider by dictionary key first, then falls back to domain parsing."""
    # Direct match by key name (e.g., 'pexels', 'unsplash')
    if target in providers:
        logging.debug("Matched provider target by key name: '%s'", target)
        return providers[target]

    # Domain-based fallback for full URLs passed via CLI
    for name, config in providers.items():
        for domain in config.get("domains", []):
            if domain in target:
                logging.debug("Matched endpoint URL '%s' to provider '%s'", target, name)
                return config

    logging.warning("No provider mapping matched key or URL '%s'", target)
    return None


def fetch_generic_image_url(
    target: str,
    query: str,
    orientation: str = "landscape",
    config_path: str = "providers.json",
    timeout: int = 12,
) -> Optional[str]:
    """Dynamically builds the request and extracts image URL using providers.json."""
    providers = load_providers(config_path)
    cfg = find_matching_provider(target, providers)

    if not cfg:
        return None

    # Resolve target: use endpoint_url from config if target is an alias, else keep full URL
    endpoint_url = cfg.get("endpoint_url", target) if not target.startswith("http") else target

    resolved_key = resolve_access_key(cfg)

    headers: Dict[str, str] = {
        "User-Agent": "ePaperFetcher/2.0 (RaspberryPi/ESP32; Linux)"
    }
    params: Dict[str, Any] = {}

    # Authentication
    auth_type = cfg.get("auth_type", "param")
    if auth_type != "none" and not resolved_key:
        logging.warning("API Key is required for endpoint '%s' but was not provided.", endpoint_url)
        return None

    key_param_name = cfg.get("key_param")
    header_name = cfg.get("header_name")

    if auth_type == "param" and key_param_name:
        params[key_param_name] = resolved_key
    elif auth_type == "header" and header_name:
        headers[header_name] = resolved_key

    # Query & Orientation
    if cfg.get("query_param"):
        params[cfg["query_param"]] = query

    if cfg.get("orientation_param"):
        ori_val = orientation
        if "orientation_map" in cfg and orientation in cfg["orientation_map"]:
            ori_val = cfg["orientation_map"][orientation]
        params[cfg["orientation_param"]] = ori_val

    # Static Extra Params
    if "extra_params" in cfg:
        params.update(cfg["extra_params"])

    # Log Constructed Request Details
    log_params = dict(params)
    if auth_type == "param" and key_param_name and key_param_name in log_params:
        log_params[key_param_name] = mask_sensitive_value(str(log_params[key_param_name]))

    log_headers = dict(headers)
    if auth_type == "header" and header_name and header_name in log_headers:
        log_headers[header_name] = mask_sensitive_value(str(log_headers[header_name]))

    logging.info("Preparing HTTP request for endpoint: %s", endpoint_url)
    logging.debug("Constructed Params:\n%s", json.dumps(log_params, ensure_ascii=False, indent=2))
    logging.debug("Constructed Headers:\n%s", json.dumps(log_headers, ensure_ascii=False, indent=2))

    try:
        resp = requests.get(endpoint_url, params=params, headers=headers, timeout=timeout)
        logging.info("HTTP Response Status: %d", resp.status_code)
        resp.raise_for_status()
        data = resp.json()

        # Handle Randomization
        random_key = cfg.get("randomize_list")
        if random_key and isinstance(data, dict) and random_key in data:
            items = data.get(random_key, [])
            if not items:
                logging.warning("Response payload returned an empty list for key '%s'", random_key)
                return None
            logging.debug("Randomly selecting 1 item out of %d from list '%s'", len(items), random_key)
            data[random_key] = [random.choice(items)]

        # Extract value using dot-notation path
        json_path = cfg.get("json_path", "")
        raw_val = get_nested_value(data, json_path)

        if not raw_val:
            logging.warning("Could not extract image URL string using JSON path '%s'", json_path)
            return None

        # Handle URL formatting template
        if "url_template" in cfg:
            raw_val = cfg["url_template"].format(value=raw_val)

        resolved_url = str(raw_val)
        logging.info("Successfully fetched image URL: %s", resolved_url)
        return resolved_url

    except requests.exceptions.RequestException as exc:
        logging.warning("HTTP request failed: %s", exc)
    except ValueError:
        logging.warning("Response body is not a valid JSON structure.")

    return None


def main() -> None:
    """CLI Entry Point."""
    parser = argparse.ArgumentParser(
        description="Fetch photo or art URL dynamically using providers.json config."
    )
    parser.add_argument(
        "-u",
        "--url",
        default="unsplash",
        help="Provider key from providers.json (e.g. 'pexels', 'artic') or full API Endpoint URL",
    )
    parser.add_argument(
        "-q",
        "--query",
        default="black and white street photography",
        help="Search query term or subject",
    )
    parser.add_argument(
        "-o",
        "--orientation",
        default="landscape",
        choices=["landscape", "portrait", "squarish"],
        help="Target aspect ratio/orientation",
    )
    parser.add_argument(
        "-c",
        "--config",
        default="providers.json",
        help="Path to JSON configuration file (default: providers.json)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING"],
        type=str.upper,
        help="Set the logging level (default: INFO)",
    )
    parser.add_argument(
        "--log-file",
        help="Optional file path to store logs instead of writing to stderr",
    )

    args = parser.parse_args()

    setup_logging(level_name=args.log_level, log_file=args.log_file)

    image_url = fetch_generic_image_url(
        target=args.url,
        query=args.query,
        orientation=args.orientation,
        config_path=args.config,
    )

    if image_url:
        sys.stdout.write(f"{image_url}\n")
    else:
        sys.exit(2)


if __name__ == "__main__":
    main()
