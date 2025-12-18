import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from market_price_checker.scrapers import search_all, parse_price

def test_parse_price():
    assert parse_price("1,000円") == 1000
    assert parse_price("¥9,800") == 9800
    assert parse_price("価格: 500") == 500
    assert parse_price("無料") == 0
    assert parse_price("") == 0

@pytest.mark.asyncio
async def test_search_all_mocked():
    # Mock the individual search functions to avoid network calls and flaky tests
    with patch('market_price_checker.scrapers.search_amazon', new_callable=AsyncMock) as mock_amazon, \
         patch('market_price_checker.scrapers.search_yahoo', new_callable=AsyncMock) as mock_yahoo, \
         patch('market_price_checker.scrapers.search_rakuten', new_callable=AsyncMock) as mock_rakuten, \
         patch('market_price_checker.scrapers.search_bic', new_callable=AsyncMock) as mock_bic, \
         patch('market_price_checker.scrapers.async_playwright') as mock_playwright:

        # Setup mock returns
        mock_amazon.return_value = [{"site": "Amazon", "title": "A", "price": 1000, "url": "url_a"}]
        mock_yahoo.return_value = [{"site": "Yahoo", "title": "Y", "price": 1200, "url": "url_y"}]
        mock_rakuten.return_value = [{"site": "Rakuten", "title": "R", "price": 900, "url": "url_r"}]
        mock_bic.return_value = [{"site": "BicCamera", "title": "B", "price": 1100, "url": "url_b"}]

        # Setup playwright mock context
        mock_p_instance = AsyncMock()
        mock_playwright.return_value.__aenter__.return_value = mock_p_instance
        mock_browser = AsyncMock()
        mock_p_instance.chromium.launch.return_value = mock_browser
        mock_context = AsyncMock()
        mock_browser.new_context.return_value = mock_context

        keyword = "test item"
        results = await search_all(keyword)

        assert len(results) == 4
        # Verify sorting by price (Rakuten 900 -> Amazon 1000 -> Bic 1100 -> Yahoo 1200)
        assert results[0]['site'] == "Rakuten"
        assert results[0]['price'] == 900
        assert results[1]['site'] == "Amazon"
        assert results[3]['site'] == "Yahoo"
