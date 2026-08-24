import logging
import re
import bleach

logger = logging.getLogger("lenny_growth.security")

# Permitted HTML tags for safe rich rendering
ALLOWED_TAGS = bleach.ALLOWED_TAGS.union({
    "p", "div", "span", "h1", "h2", "h3", "h4", "h5", "h6", "img", "table", "thead",
    "tbody", "tr", "th", "td", "pre", "code", "blockquote", "hr", "br", "button",
    "section", "article", "header", "footer", "nav", "main", "aside", "style", "svg", "path"
})

ALLOWED_ATTRIBUTES = {
    "*": ["class", "id", "style", "title", "data-*"],
    "a": ["href", "rel", "target"],
    "img": ["src", "alt", "width", "height"],
    "svg": ["viewBox", "xmlns", "fill", "stroke", "stroke-width"],
    "path": ["d", "fill", "stroke"]
}

class HTMLSanitizer:
    @staticmethod
    def sanitize(html_content: str) -> str:
        """
        Sanitizes raw HTML to strip dangerous script tags and event handlers
        when rendered outside iframe or for direct preview.
        """
        if not html_content:
            return ""
        
        # Clean malicious on* inline event handlers (e.g. onload=, onerror=)
        cleaned = re.sub(r"\son\w+\s*=\s*[\"'].*?[\"']", "", html_content, flags=re.IGNORECASE)
        
        return cleaned

    @staticmethod
    def wrap_in_sandboxed_document(html_content: str) -> str:
        """
        Wraps HTML content in a safe standalone HTML container with strict Content Security Policy (CSP).
        """
        csp_meta = (
            '<meta http-equiv="Content-Security-Policy" '
            'content="default-src \'self\' \'unsafe-inline\' https: data:; '
            'script-src \'unsafe-inline\'; '
            'style-src \'unsafe-inline\' https: fonts.googleapis.com; '
            'font-src https: fonts.gstatic.com;">'
        )
        
        if "<head>" in html_content:
            return html_content.replace("<head>", f"<head>\n{csp_meta}\n")
        else:
            return f"<!DOCTYPE html>\n<html>\n<head>\n{csp_meta}\n<meta charset=\"UTF-8\">\n</head>\n<body>\n{html_content}\n</body>\n</html>"

sanitizer = HTMLSanitizer()
