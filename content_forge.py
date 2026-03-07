#!/usr/bin/env python3
"""
ContentForge - AI-powered content generation toolkit.
Blog posts, product descriptions, email sequences, social media posts.

Free tier:  500 words max, blog posts only
Premium:    Unlimited words, all content types, humanization pass, keyword optimization

Usage:
  content-forge --topic "AI trends 2026" --output article.md
  content-forge --topic "Running shoes" --type product --words 300
  content-forge --topic "Email marketing" --type email-sequence --count 5
  content-forge --activate YOUR-LICENSE-KEY
"""

__version__ = "1.0.0"

import argparse
import json
import sys
from pathlib import Path
from datetime import datetime

try:
    import requests
except ImportError:
    print("Install dependencies: pip install requests")
    sys.exit(1)

sys.path.insert(0, str(Path(__file__).parent))
try:
    from license_gate import LicenseGate
except ImportError:
    class LicenseGate:
        def __init__(self, n): pass
        def check(self, silent=False): return "trial"
        def is_premium(self): return True
        def require_premium(self, f=""): return True
        def handle_activate_flag(self, a=None): return None
        @staticmethod
        def add_activate_arg(p): p.add_argument('--activate', help='License key')

gate = LicenseGate("content-forge")

FREE_WORD_LIMIT = 500


# ===== LLM BACKENDS =====

def query_ollama(prompt, model='llama3.1'):
    try:
        resp = requests.post('http://localhost:11434/api/generate', json={
            'model': model, 'prompt': prompt, 'stream': False,
            'options': {'temperature': 0.7, 'num_predict': 4096}
        }, timeout=180)
        resp.raise_for_status()
        return resp.json().get('response', '')
    except requests.ConnectionError:
        print("Ollama not running. Start with: ollama serve")
        print("Then pull a model: ollama pull llama3.1")
        sys.exit(1)
    except Exception as e:
        print(f"Ollama error: {e}")
        sys.exit(1)


def query_openai(prompt, api_key, model='gpt-4o-mini'):
    resp = requests.post('https://api.openai.com/v1/chat/completions', headers={
        'Authorization': f'Bearer {api_key}',
        'Content-Type': 'application/json'
    }, json={
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 0.7,
        'max_tokens': 4096
    }, timeout=60)
    resp.raise_for_status()
    return resp.json()['choices'][0]['message']['content']


def query_anthropic(prompt, api_key, model='claude-sonnet-4-20250514'):
    resp = requests.post('https://api.anthropic.com/v1/messages', headers={
        'x-api-key': api_key,
        'anthropic-version': '2023-06-01',
        'Content-Type': 'application/json'
    }, json={
        'model': model,
        'max_tokens': 4096,
        'messages': [{'role': 'user', 'content': prompt}]
    }, timeout=60)
    resp.raise_for_status()
    return resp.json()['content'][0]['text']


def query_llm(prompt, backend='ollama', model=None, api_key=None):
    if backend == 'ollama':
        return query_ollama(prompt, model or 'llama3.1')
    elif backend == 'openai':
        return query_openai(prompt, api_key, model or 'gpt-4o-mini')
    elif backend == 'anthropic':
        return query_anthropic(prompt, api_key, model or 'claude-sonnet-4-20250514')
    else:
        raise ValueError(f"Unknown backend: {backend}")


# ===== CONTENT GENERATORS =====

def generate_blog_post(topic, words, keywords=None, backend='ollama', model=None, api_key=None):
    kw_section = f"\nNaturally incorporate these keywords: {keywords}" if keywords else ""
    prompt = f"""Write a comprehensive, engaging blog post about: {topic}

Requirements:
- Approximately {words} words
- Include an engaging introduction that hooks the reader
- Use H2 and H3 subheadings to organize the content
- Include practical tips, examples, or data points
- Write in a conversational but authoritative tone
- End with a clear conclusion and call-to-action
- Format in Markdown{kw_section}

Write the complete article now:"""

    return query_llm(prompt, backend, model, api_key)


def generate_product_description(topic, words, backend='ollama', model=None, api_key=None):
    prompt = f"""Write a compelling product description for: {topic}

Requirements:
- Approximately {words} words
- Start with a benefit-driven headline
- Highlight key features and benefits
- Use sensory and emotional language
- Include a clear value proposition
- End with a call-to-action
- Format in Markdown

Write the product description now:"""

    return query_llm(prompt, backend, model, api_key)


def generate_email_sequence(topic, count, backend='ollama', model=None, api_key=None):
    prompt = f"""Create a {count}-email drip campaign sequence about: {topic}

For each email, provide:
- Subject line (compelling, under 50 chars)
- Preview text (under 100 chars)
- Email body (150-300 words)
- Call-to-action

The sequence should build progressively:
- Email 1: Introduction / value proposition
- Email 2: Problem awareness / pain points
- Email 3: Solution presentation
- Email 4: Social proof / case study
- Email {count}: Urgency / final CTA

Format each email clearly with "## Email X:" headers in Markdown.

Write the complete email sequence now:"""

    return query_llm(prompt, backend, model, api_key)


def generate_social_media(topic, count, backend='ollama', model=None, api_key=None):
    prompt = f"""Create {count} social media posts about: {topic}

For each post provide:
- Platform suggestion (Twitter/LinkedIn/Instagram/Facebook)
- Post text (platform-appropriate length)
- 3-5 relevant hashtags
- Suggested image description

Mix of formats: tips, questions, stats, quotes, stories.
Format clearly with "### Post X:" headers in Markdown.

Write all {count} posts now:"""

    return query_llm(prompt, backend, model, api_key)


def humanize_content(text, backend='ollama', model=None, api_key=None):
    prompt = f"""Rewrite the following text to sound more natural and human-written.
Keep the same meaning, structure, and key points.
Make it sound like a knowledgeable person wrote it conversationally.
Vary sentence length. Use some informal transitions. Add minor imperfections that feel natural.
Do NOT add any commentary - just output the rewritten text.

Text to humanize:
{text}"""

    return query_llm(prompt, backend, model, api_key)


def main():
    parser = argparse.ArgumentParser(
        description='ContentForge - AI-powered content generation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""Examples:
  content_forge --topic "AI trends 2026" --words 1500 --output article.md
  content_forge --topic "Running shoes" --type product --words 300
  content_forge --topic "Email tips" --type email-sequence --count 5
  content_forge --activate YOUR-KEY""")
    parser.add_argument('--topic', help='Topic to write about')
    parser.add_argument('--type', '-t', choices=['blog', 'product', 'email-sequence', 'social'],
                        default='blog', help='Content type')
    parser.add_argument('--words', '-w', type=int, default=1000, help='Approximate word count')
    parser.add_argument('--count', type=int, default=5, help='Number of items (emails/social posts)')
    parser.add_argument('--keywords', '-k', help='Comma-separated keywords to include')
    parser.add_argument('--output', '-o', default='content.md', help='Output file')
    parser.add_argument('--backend', '-b', choices=['ollama', 'openai', 'anthropic'],
                        default='ollama', help='LLM backend (default: ollama = free)')
    parser.add_argument('--model', '-m', help='Model name override')
    parser.add_argument('--api-key', help='API key for openai/anthropic')
    parser.add_argument('--humanize', action='store_true', help='[Premium] Run humanization pass')
    parser.add_argument('--version', '-v', action='version', version=f'ContentForge {__version__}')
    LicenseGate.add_activate_arg(parser)
    args = parser.parse_args()

    gate.handle_activate_flag(args)
    if hasattr(args, 'activate') and args.activate:
        return

    gate.check()

    if not args.topic:
        parser.print_help()
        return

    # Premium feature gates
    if args.type != 'blog' and not gate.require_premium(f"{args.type} content type"):
        print("  Free tier supports blog posts only. Generating blog post instead.")
        args.type = 'blog'

    if args.humanize and not gate.require_premium("Humanization pass"):
        args.humanize = False

    if args.keywords and not gate.require_premium("Keyword optimization"):
        args.keywords = None

    # Word limit for free tier
    if not gate.is_premium() and args.words > FREE_WORD_LIMIT:
        print(f"  Free tier: limited to {FREE_WORD_LIMIT} words (requested {args.words})")
        print(f"  Upgrade for unlimited: https://tirandev.gumroad.com")
        args.words = FREE_WORD_LIMIT

    print(f"  Generating {args.type} content about: {args.topic}")
    print(f"  Backend: {args.backend} | Target: ~{args.words} words")

    if args.type == 'blog':
        content = generate_blog_post(args.topic, args.words, args.keywords,
                                     args.backend, args.model, args.api_key)
    elif args.type == 'product':
        content = generate_product_description(args.topic, args.words,
                                               args.backend, args.model, args.api_key)
    elif args.type == 'email-sequence':
        content = generate_email_sequence(args.topic, args.count,
                                          args.backend, args.model, args.api_key)
    elif args.type == 'social':
        content = generate_social_media(args.topic, args.count,
                                        args.backend, args.model, args.api_key)

    if args.humanize:
        print("  Running humanization pass...")
        content = humanize_content(content, args.backend, args.model, args.api_key)

    header = f"""---
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}
Topic: {args.topic}
Type: {args.type}
Backend: {args.backend}
---

"""

    Path(args.output).write_text(header + content, encoding='utf-8')
    word_count = len(content.split())
    print(f"  Saved to {args.output} | {word_count} words")


if __name__ == '__main__':
    main()
