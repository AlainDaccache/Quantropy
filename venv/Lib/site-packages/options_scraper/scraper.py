import logging
import re
import urllib.parse

import requests
from lxml import etree

from options_scraper.utils import batched, get_text

LOG = logging.getLogger(__name__)

__all__ = ['NASDAQOptionsScraper']

last_number_pattern = re.compile(r"(?<=&page=)\d+")
nasdaq_base_url = "https://old.nasdaq.com"


class NASDAQOptionsScraper:

    @staticmethod
    def gen_pages(url):
        """
        Description:
            If for a given query the results are paginated then
            we should traverse the pages too. This function exactly does that.

        Args:
            URL - The main URL

        Returns:
            Generator - All the other pages in the search results if present.

        """
        response = requests.get(url)
        tree = etree.HTML(response.content)
        for element in tree.xpath("//*[@id='quotes_content_left_lb_LastPage']"):
            if element is not None:
                last_url = element.attrib["href"]
                page_numbers = re.findall(last_number_pattern, last_url)
                if page_numbers:
                    last_page = int(page_numbers[0])
                    for i in range(2, last_page + 1):
                        url_to_scrap = "{0}&page={1}".format(url, i)
                        yield url_to_scrap

    @staticmethod
    def gen_page_records(url):
        """
        Description:
            Scrape Options data from the given URL.
            This is a 2 step process.
                1. First, extract the headers
                2. Then, the data rows.

        Args:
            url: NASDAQ URL to scrape

        Returns:
            Generator: Data records each as a dictionary

        """
        response = requests.get(url)
        tree = etree.HTML(response.content)
        headers = []
        # First, we will extract the table headers.
        for element in tree.xpath(
                "//div[@class='OptionsChain-chart borderAll thin']"):
            for thead_element in element.xpath("table/thead/tr/th"):
                a_element = thead_element.find("a")
                if a_element is not None:
                    headers.append(a_element.text.strip())
                else:
                    headers.append(thead_element.text.strip())

        # Then, the data rows.
        for element in tree.xpath(
                "//div[@class='OptionsChain-chart borderAll thin']"):
            for trow_elem in element.xpath("//tr"):
                data_row = [get_text(x) for x in trow_elem.findall("td")]
                if len(headers) == len(data_row):
                    yield dict(zip(headers, data_row))

    def __call__(self, ticker, **kwargs):
        """
        Description:
            Constructs a NASDAQ specific URL for the given Ticker Symbol and options.
            Then traverses the option data found at the URL. If there are more pages,
            the data records on the pages are scraped too.

        Args:
            ticker: A valid Ticker Symbol
            **kwargs: Mapping of query parameters that should be passed to the NASDAQ URL

        Returns:
            Generator: Each options data record as a python dictionary till
            the last page is reached.
        """
        params = urllib.parse.urlencode(
            dict((k, v) for k, v in kwargs.items() if v is not None))
        url = f"{nasdaq_base_url}/symbol/{ticker.lower()}/option-chain?{params}"

        LOG.info("Scraping data from URL %s", url)
        for rec in self.gen_page_records(url):
            yield rec

        for url in self.gen_pages(url):
            LOG.info("Scraping data from URL %s", url)
            for rec in self.gen_page_records(url):
                yield rec

