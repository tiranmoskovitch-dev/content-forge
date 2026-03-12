"""Command-line interface for Content Forge."""

import argparse
import json
import sys

from content_forge import __version__
from content_forge.generator import ContentGenerator
from content_forge.licensing import activate_license, get_status


def main():
    parser = argparse.ArgumentParser(
        prog="content-forge",
        description="Content Forge - AI-powered content generation",
    )
    parser.add_argument("--version", action="version", version=f"content-forge {__version__}")

    subparsers = parser.add_subparsers(dest="command")

    # generate command
    gen_parser = subparsers.add_parser("generate", help="Generate content")
    gen_parser.add_argument("topic", help="Topic to write about")
    gen_parser.add_argument("--type", dest="content_type", default="blog_post",
                            choices=["blog_post", "social_media", "email", "ad_copy",
                                     "product_description", "landing_page", "newsletter"])
    gen_parser.add_argument("--tone", default="professional",
                            choices=["professional", "casual", "persuasive", "friendly", "formal"])
    gen_parser.add_argument("--words", type=int, default=500, help="Target word count")
    gen_parser.add_argument("--keywords", nargs="+", default=None, help="SEO keywords")
    gen_parser.add_argument("--provider", default="openai", choices=["openai", "anthropic"])
    gen_parser.add_argument("--output", "-o", default=None, help="Output file path")

    # humanize command
    human_parser = subparsers.add_parser("humanize", help="Humanize AI text (Premium)")
    human_parser.add_argument("--input", "-i", required=True, help="Input file with text")
    human_parser.add_argument("--output", "-o", default=None, help="Output file path")

    # license command
    license_parser = subparsers.add_parser("license", help="Manage license")
    license_parser.add_argument("action", choices=["status", "activate"])
    license_parser.add_argument("--key", default=None)

    args = parser.parse_args()

    if args.command == "generate":
        gen = ContentGenerator(provider=args.provider)
        try:
            result = gen.generate(
                content_type=args.content_type,
                topic=args.topic,
                tone=args.tone,
                word_count=args.words,
                keywords=args.keywords,
            )
        except PermissionError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

        print(f"Type: {result.content_type}")
        print(f"Words: {result.word_count}")
        print(f"---")
        print(result.body)

        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result.body)
            print(f"\nSaved to: {args.output}")

    elif args.command == "humanize":
        gen = ContentGenerator()
        with open(args.input, "r", encoding="utf-8") as f:
            text = f.read()
        try:
            result = gen.humanize(text)
        except PermissionError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)
        print(result)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(result)

    elif args.command == "license":
        if args.action == "status":
            print(json.dumps(get_status(), indent=2))
        elif args.action == "activate":
            if not args.key:
                print("Error: --key required", file=sys.stderr)
                sys.exit(1)
            ok, msg = activate_license(args.key)
            print(msg)

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
