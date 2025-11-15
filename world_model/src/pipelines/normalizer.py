"""Document normalizer - first step in the pipeline."""

import re
import hashlib
from typing import Optional, Dict, Any
from datetime import datetime
from urllib.parse import urlparse, unquote

from bs4 import BeautifulSoup
import html2text
from loguru import logger

from ..models.document import RawDocument


class ContentNormalizer:
    """Handles text content normalization."""

    def __init__(self):
        self.html_converter = html2text.HTML2Text()
        self.html_converter.ignore_links = False
        self.html_converter.ignore_images = False
        self.html_converter.body_width = 0  # Don't wrap lines

    def strip_html(self, html_content: str) -> str:
        """Convert HTML to clean markdown text."""
        try:
            # First pass with BeautifulSoup to clean up
            soup = BeautifulSoup(html_content, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Convert to markdown
            text = self.html_converter.handle(str(soup))

            return text.strip()
        except Exception as e:
            logger.warning(f"HTML stripping failed, using fallback: {e}")
            # Fallback to basic text extraction
            soup = BeautifulSoup(html_content, 'html.parser')
            return soup.get_text(separator=' ', strip=True)

    def expand_urls(self, text: str) -> str:
        """Expand shortened URLs (placeholder - would integrate with URL unshortener)."""
        # TODO: Integrate with URL expansion service
        # For now, just decode URL encoding
        url_pattern = re.compile(r'https?://[^\s]+')

        def decode_url(match):
            url = match.group(0)
            try:
                return unquote(url)
            except:
                return url

        return url_pattern.sub(decode_url, text)

    def normalize_whitespace(self, text: str) -> str:
        """Normalize whitespace and line breaks."""
        # Replace multiple spaces with single space
        text = re.sub(r'\s+', ' ', text)
        # Replace multiple newlines with double newline
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text.strip()

    def normalize_unicode(self, text: str) -> str:
        """Normalize unicode characters."""
        # Remove zero-width characters
        text = re.sub(r'[\u200b\u200c\u200d\ufeff]', '', text)
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        text = text.replace(''', "'").replace(''', "'")
        # Normalize dashes
        text = text.replace('—', '--').replace('–', '-')
        return text

    def remove_boilerplate(self, text: str, source: str) -> str:
        """Remove common boilerplate based on source."""
        boilerplate_patterns = {
            'twitter': [
                r'^\s*RT\s+@\w+:\s*',  # Retweet prefix
                r'\s*pic\.twitter\.com/\w+\s*$',  # Twitter image links
            ],
            'reddit': [
                r'^\s*\[deleted\]\s*$',  # Deleted content
                r'^\s*\[removed\]\s*$',  # Removed content
            ],
        }

        patterns = boilerplate_patterns.get(source, [])
        for pattern in patterns:
            text = re.sub(pattern, '', text, flags=re.MULTILINE)

        return text


class Normalizer:
    """Main normalizer that orchestrates all normalization steps."""

    def __init__(self):
        self.content_normalizer = ContentNormalizer()

    def normalize(self, raw_data: Dict[str, Any]) -> RawDocument:
        """
        Normalize raw input data into a RawDocument.

        Args:
            raw_data: Dictionary with raw content from any source

        Returns:
            Normalized RawDocument ready for deduplication
        """
        # Extract and normalize body text
        body = raw_data.get('body', '') or raw_data.get('content', '') or raw_data.get('text', '')

        # Apply normalization pipeline
        if raw_data.get('is_html', False):
            body = self.content_normalizer.strip_html(body)

        body = self.content_normalizer.expand_urls(body)
        body = self.content_normalizer.normalize_unicode(body)
        body = self.content_normalizer.normalize_whitespace(body)

        source = raw_data.get('source', 'unknown')
        body = self.content_normalizer.remove_boilerplate(body, source)

        # Generate document ID and checksum
        timestamp = raw_data.get('published_at', datetime.utcnow())
        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))

        # Create checksum from normalized content
        checksum = self._generate_checksum(body)

        # Generate document ID
        doc_id = f"src_{source}_{timestamp.strftime('%Y%m%d_%H%M%S')}_{checksum[:8]}"

        # Create RawDocument
        doc = RawDocument(
            doc_id=doc_id,
            source=source,
            url=raw_data.get('url'),
            author_handle=raw_data.get('author_handle'),
            author_name=raw_data.get('author_name'),
            published_at=timestamp,
            ingested_at=datetime.utcnow(),
            lang=raw_data.get('lang', 'en'),
            title=raw_data.get('title'),
            body=body,
            media=raw_data.get('media', []),
            checksum=checksum,
            metadata=raw_data.get('metadata', {})
        )

        logger.info(f"Normalized document {doc.doc_id} from {source}")
        return doc

    def _generate_checksum(self, content: str) -> str:
        """Generate SHA256 checksum of content."""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()