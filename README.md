# ContentForge

AI-powered content generation toolkit. Blog posts, product descriptions, email sequences, and social media posts.

![Python](https://img.shields.io/badge/Python-3.8+-blue) ![License](https://img.shields.io/badge/License-MIT-green) ![Version](https://img.shields.io/badge/Version-1.0.0-orange)

## Features

| Feature | Free | Premium |
|---------|:----:|:-------:|
| Blog post generation | Yes | Yes |
| Up to 500 words | Yes | Yes |
| Ollama (free local AI) | Yes | Yes |
| Markdown output | Yes | Yes |
| **Unlimited word count** | - | Yes |
| **Product descriptions** | - | Yes |
| **Email sequences** | - | Yes |
| **Social media posts** | - | Yes |
| **Humanization pass** | - | Yes |
| **Keyword optimization** | - | Yes |
| **OpenAI & Anthropic backends** | - | Yes |

**30-day free trial** includes all Premium features.

## Supported AI Backends

| Backend | Cost | Setup |
|---------|------|-------|
| **Ollama** (default) | Free | `ollama serve` + `ollama pull llama3.1` |
| OpenAI | Pay per token | `--backend openai --api-key sk-...` |
| Anthropic | Pay per token | `--backend anthropic --api-key sk-ant-...` |

## Install

```bash
pip install requests
# For free local AI:
# Install Ollama from https://ollama.ai
ollama pull llama3.1
```

## Quick Start

```bash
# Generate a blog post (free)
python content_forge.py --topic "AI trends 2026" --output article.md

# Product description (Premium)
python content_forge.py --topic "Wireless headphones" --type product --words 300

# Email drip campaign (Premium)
python content_forge.py --topic "SaaS onboarding" --type email-sequence --count 5

# Social media posts (Premium)
python content_forge.py --topic "Fitness tips" --type social --count 10

# With humanization (Premium)
python content_forge.py --topic "Remote work" --words 1500 --humanize

# With keyword optimization (Premium)
python content_forge.py --topic "Best CRM software" --keywords "crm,sales,automation"
```

## Content Types

- **blog** - Full blog posts with headings, tips, and CTAs (default)
- **product** - Benefit-driven product descriptions
- **email-sequence** - Multi-email drip campaigns with subject lines
- **social** - Platform-optimized social media posts with hashtags

## Activate Premium

```bash
python content_forge.py --activate YOUR-LICENSE-KEY
```

Get your key at [tirandev.gumroad.com](https://tirandev.gumroad.com)

## License

MIT License - free for personal and commercial use.
Premium features require a license key after the 30-day trial.
