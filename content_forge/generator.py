"""Core content generation engine for Content Forge."""

import json
import os
import re
from dataclasses import dataclass, field
from typing import Optional

from content_forge.licensing import check_limit, get_tier


@dataclass
class ContentResult:
    content_type: str
    title: str
    body: str
    word_count: int
    metadata: dict = field(default_factory=dict)
    seo_keywords: list = field(default_factory=list)


# Default templates for content generation (used when no AI API key is configured)
TEMPLATES = {
    "blog_post": {
        "structure": [
            "# {title}",
            "",
            "## Introduction",
            "{intro}",
            "",
            "## {section_1_title}",
            "{section_1_body}",
            "",
            "## {section_2_title}",
            "{section_2_body}",
            "",
            "## {section_3_title}",
            "{section_3_body}",
            "",
            "## Conclusion",
            "{conclusion}",
        ],
    },
    "social_media": {
        "structure": [
            "{hook}",
            "",
            "{body}",
            "",
            "{cta}",
            "",
            "{hashtags}",
        ],
    },
    "email": {
        "structure": [
            "Subject: {subject}",
            "",
            "Hi {recipient},",
            "",
            "{opening}",
            "",
            "{body}",
            "",
            "{cta}",
            "",
            "Best,",
            "{sender}",
        ],
    },
    "product_description": {
        "structure": [
            "# {product_name}",
            "",
            "{tagline}",
            "",
            "## Features",
            "{features}",
            "",
            "## Benefits",
            "{benefits}",
            "",
            "{cta}",
        ],
    },
}


class ContentGenerator:
    """Generate various types of content using AI or templates.

    Supports OpenAI and Anthropic APIs. Falls back to structured templates
    when no API key is configured.
    """

    def __init__(self, api_key=None, provider="openai", model=None):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY") or os.environ.get("ANTHROPIC_API_KEY")
        self.provider = provider
        self.model = model
        self._ai_available = bool(self.api_key)

    def generate(self, content_type, topic, tone="professional", word_count=500,
                 keywords=None, context=None):
        """Generate content.

        Args:
            content_type: Type of content (blog_post, social_media, email, etc.)
            topic: The topic or subject to write about.
            tone: Writing tone (professional, casual, persuasive, etc.)
            word_count: Target word count.
            keywords: SEO keywords to include.
            context: Additional context or instructions.

        Returns:
            ContentResult with the generated content.
        """
        # Check tier limits
        allowed, msg = check_limit("content_type", content_type)
        if not allowed:
            raise PermissionError(msg)

        allowed, msg = check_limit("max_words", word_count)
        if not allowed:
            raise PermissionError(msg)

        if self._ai_available:
            return self._generate_with_ai(content_type, topic, tone, word_count, keywords, context)
        else:
            return self._generate_with_template(content_type, topic, tone, word_count, keywords)

    def humanize(self, text):
        """Make AI-generated text sound more human (Premium feature).

        Args:
            text: The text to humanize.

        Returns:
            Humanized text string.
        """
        allowed, msg = check_limit("humanize")
        if not allowed:
            raise PermissionError(msg)

        if not self._ai_available:
            # Basic humanization without AI: vary sentence length, add transitions
            return self._basic_humanize(text)

        return self._ai_humanize(text)

    def batch_generate(self, tasks):
        """Generate multiple pieces of content (Premium feature).

        Args:
            tasks: List of dicts, each with keys matching generate() params.

        Returns:
            List of ContentResult objects.
        """
        allowed, msg = check_limit("batch_generation")
        if not allowed:
            raise PermissionError(msg)

        results = []
        for task in tasks:
            result = self.generate(**task)
            results.append(result)
        return results

    def _generate_with_ai(self, content_type, topic, tone, word_count, keywords, context):
        prompt = self._build_prompt(content_type, topic, tone, word_count, keywords, context)

        if self.provider == "openai":
            body = self._call_openai(prompt)
        elif self.provider == "anthropic":
            body = self._call_anthropic(prompt)
        else:
            raise ValueError(f"Unsupported provider: {self.provider}")

        return ContentResult(
            content_type=content_type,
            title=topic,
            body=body,
            word_count=len(body.split()),
            seo_keywords=keywords or [],
        )

    def _build_prompt(self, content_type, topic, tone, word_count, keywords, context):
        prompt = (
            f"Write a {content_type.replace('_', ' ')} about: {topic}\n"
            f"Tone: {tone}\n"
            f"Target word count: {word_count}\n"
        )
        if keywords:
            prompt += f"SEO keywords to include: {', '.join(keywords)}\n"
        if context:
            prompt += f"Additional context: {context}\n"
        return prompt

    def _call_openai(self, prompt):
        try:
            import openai
            client = openai.OpenAI(api_key=self.api_key)
            response = client.chat.completions.create(
                model=self.model or "gpt-4o-mini",
                messages=[
                    {"role": "system", "content": "You are a professional content writer."},
                    {"role": "user", "content": prompt},
                ],
            )
            return response.choices[0].message.content
        except ImportError:
            raise ImportError("OpenAI provider requires: pip install openai")

    def _call_anthropic(self, prompt):
        try:
            import anthropic
            client = anthropic.Anthropic(api_key=self.api_key)
            response = client.messages.create(
                model=self.model or "claude-sonnet-4-20250514",
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.content[0].text
        except ImportError:
            raise ImportError("Anthropic provider requires: pip install anthropic")

    def _generate_with_template(self, content_type, topic, tone, word_count, keywords):
        template = TEMPLATES.get(content_type)
        if not template:
            body = (
                f"# {topic}\n\n"
                f"[Content about {topic} in {tone} tone]\n\n"
                f"Note: Configure an API key (OPENAI_API_KEY or ANTHROPIC_API_KEY) "
                f"for AI-generated content."
            )
        else:
            lines = template["structure"]
            body = "\n".join(lines)
            body = body.replace("{title}", topic)
            # Fill remaining placeholders with instructional text
            body = re.sub(
                r"\{(\w+)\}",
                lambda m: f"[{m.group(1).replace('_', ' ').title()} - configure AI API key for auto-generation]",
                body,
            )

        return ContentResult(
            content_type=content_type,
            title=topic,
            body=body,
            word_count=len(body.split()),
            seo_keywords=keywords or [],
            metadata={"ai_generated": False, "template": True},
        )

    def _basic_humanize(self, text):
        transitions = [
            "Honestly, ", "Here's the thing - ", "Look, ",
            "The truth is, ", "What's interesting is that ",
        ]
        sentences = text.split(". ")
        result = []
        for i, s in enumerate(sentences):
            if i > 0 and i % 3 == 0 and len(transitions) > 0:
                idx = i % len(transitions)
                s = transitions[idx] + s[0].lower() + s[1:] if s else s
            result.append(s)
        return ". ".join(result)

    def _ai_humanize(self, text):
        prompt = (
            "Rewrite the following text to sound more natural and human. "
            "Vary sentence lengths, add conversational elements, "
            "and make it feel like a real person wrote it:\n\n" + text
        )
        if self.provider == "openai":
            return self._call_openai(prompt)
        elif self.provider == "anthropic":
            return self._call_anthropic(prompt)
        return text
