from bs4 import BeautifulSoup

from byte.domain.web.parser.base import BaseWebParser


class GenericParser(BaseWebParser):
	"""Generic fallback parser for any HTML content.

	This parser attempts to extract the main content from common HTML structures
	like <main>, <article>, or <body> tags. It always returns True for can_parse
	so it can be used as a last resort fallback.
	"""

	def __init__(self, exclude_links_ratio: float = 1.0) -> None:
		"""Initialize the generic parser.

		Args:
			exclude_links_ratio: Maximum ratio of link text to total text (0.0 to 1.0).
				Pages exceeding this ratio will return empty content.
		"""
		self.exclude_links_ratio = exclude_links_ratio

	def can_parse(self, soup: BeautifulSoup, url: str) -> bool:
		"""Always returns True as this is a fallback parser.

		Args:
			soup: BeautifulSoup object containing the HTML content
			url: The URL of the page being parsed

		Returns:
			Always True to serve as a fallback

		Usage: `if parser.can_parse(soup, url)` -> True
		"""
		return True

	def parse(self, soup: BeautifulSoup) -> str:
		"""Extract text from common HTML content containers.

		Tries to find content in this order:
		1. <main> tag
		2. <article> tag
		3. <div role="main">
		4. <body> tag

		Args:
			soup: BeautifulSoup object containing the HTML content

		Returns:
			Cleaned text content as a string

		Usage: `text = parser.parse(soup)` -> cleaned text
		"""
		# Try common content containers in order of preference
		content_selectors = [
			("main", {}),
			("article", {}),
			("div", {"role": "main"}),
			("body", {}),
		]

		element = None
		for tag, attrs in content_selectors:
			element = soup.find(tag, attrs)
			if element is not None:
				break

		# If we found an element and it passes the link ratio check
		if element is not None and self._get_link_ratio(element) <= self.exclude_links_ratio:
			return self._to_markdown(element)
		else:
			return ""
