"""Class for querying the Google Serper API."""

import random
import time
from typing import Any, Optional, Literal

import requests

_SERPER_URL = 'https://google.serper.dev'
NO_RESULT_MSG = 'No good Google Search result was found'


class SerperAPI:
  """Class for querying the Google Serper API."""

  def __init__(
      self,
      serper_api_key: str,
      gl: str = 'us',
      hl: str = 'en',
      k: int = 1,
      tbs: Optional[str] = None,
      search_type: Literal['news', 'search', 'places', 'images'] = 'search',
  ):
    self.serper_api_key = serper_api_key
    self.gl = gl
    self.hl = hl
    self.k = k
    self.tbs = tbs
    self.search_type = search_type
    self.result_key_for_type = {
        'news': 'news',
        'places': 'places',
        'images': 'images',
        'search': 'organic',
    }

  def run(self, query: str, **kwargs: Any) -> str:
    """Run query through GoogleSearch and parse result."""
    assert self.serper_api_key, 'Missing serper_api_key.'
    results = self._google_serper_api_results(
        query,
        gl=self.gl,
        hl=self.hl,
        num=self.k,
        tbs=self.tbs,
        search_type=self.search_type,
        **kwargs,
    )

    return self._parse_results(results)

  def _google_serper_api_results(
      self,
      search_term: str,
      search_type: str = 'search',
      max_retries: int = 3,  # Reduced from 20
      **kwargs: Any,
  ) -> dict[Any, Any]:
    """Run query through Google Serper."""
    headers = {
        'X-API-KEY': self.serper_api_key or '',
        'Content-Type': 'application/json',
    }
    params = {
        'q': search_term,
        **{key: value for key, value in kwargs.items() if value is not None},
    }
    response, num_fails, sleep_time = None, 0, 0

    print(f'    🔍 Searching: "{search_term[:50]}..."' if len(search_term) > 50 else f'    🔍 Searching: "{search_term}"')

    while not response and num_fails < max_retries:
      try:
        response = requests.post(
            f'{_SERPER_URL}/{search_type}', headers=headers, params=params,
            timeout=30  # Add 30 second timeout
        )
        print(f'    ✅ Search completed (status: {response.status_code})')
      except AssertionError as e:
        raise e
      except Exception as e:  # pylint: disable=broad-exception-caught
        print(f'    ⚠️ Search failed (attempt {num_fails + 1}/{max_retries}): {type(e).__name__}')
        response = None
        num_fails += 1
        sleep_time = min(sleep_time * 2, 10)  # Reduced max sleep
        sleep_time = random.uniform(1, 3) if not sleep_time else sleep_time
        time.sleep(sleep_time)

    if not response:
      raise ValueError('Failed to get result from Google Serper API')

    response.raise_for_status()
    search_results = response.json()
    return search_results

  def _parse_snippets_with_links(self, results: dict[Any, Any]) -> list[dict]:
    """Parse results with links."""
    items = []

    if results.get('answerBox'):
      answer_box = results.get('answerBox', {})
      answer = answer_box.get('answer')
      snippet = answer_box.get('snippet')
      link = answer_box.get('link', '')

      if answer and isinstance(answer, str):
        items.append({'snippet': answer, 'link': link, 'title': 'Answer Box'})
      if snippet and isinstance(snippet, str):
        items.append({'snippet': snippet.replace('\n', ' '), 'link': link, 'title': 'Answer Box'})

    if results.get('knowledgeGraph'):
      kg = results.get('knowledgeGraph', {})
      title = kg.get('title', '')
      entity_type = kg.get('type')
      description = kg.get('description')
      link = kg.get('descriptionLink', kg.get('website', ''))

      if entity_type:
        items.append({'snippet': f'{title}: {entity_type}.', 'link': link, 'title': 'Knowledge Graph'})

      if description:
        items.append({'snippet': description, 'link': link, 'title': title})

      for attribute, value in kg.get('attributes', {}).items():
        items.append({'snippet': f'{title} {attribute}: {value}.', 'link': link, 'title': title})

    result_key = self.result_key_for_type[self.search_type]

    if result_key in results:
      for result in results[result_key][:self.k]:
        title = result.get('title', 'Search Result')
        link = result.get('link', '')
        
        if 'snippet' in result:
          items.append({'snippet': result['snippet'], 'link': link, 'title': title})

        for attribute, value in result.get('attributes', {}).items():
          items.append({'snippet': f'{attribute}: {value}.', 'link': link, 'title': title})

    if not items:
      return [{'snippet': NO_RESULT_MSG, 'link': '', 'title': 'No Result'}]

    return items

  def _parse_snippets(self, results: dict[Any, Any]) -> list[str]:
    """Parse results (legacy, returns only snippets)."""
    items = self._parse_snippets_with_links(results)
    return [item['snippet'] for item in items]

  def _parse_results(self, results: dict[Any, Any]) -> str:
    """Parse results with links included."""
    items = self._parse_snippets_with_links(results)
    formatted = []
    for item in items:
      if item['link']:
        formatted.append(f"{item['snippet']} [Source: {item['link']}]")
      else:
        formatted.append(item['snippet'])
    return ' '.join(formatted)

