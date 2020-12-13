import csv
import datetime
import json
import logging
import os

from typing import List, Mapping

from options_scraper.scraper import NASDAQOptionsScraper
from options_scraper.utils import batched


__all__ = ['NASDAQOptionsSerializer']

LOG = logging.getLogger(__name__)


class NASDAQOptionsSerializer:
    def __init__(self,
                 ticker: str,
                 root_dir: str,
                 serialization_format: str = "csv",
                 batch_size: int = 100):

        self.ticker = ticker
        self.serialization_format = serialization_format
        self.serializer = (self._to_json
                           if serialization_format == "json" else self._to_csv)
        self.output_file_date_fmt = "%Y-%m-%dT%H-%M-%S-%f"

        output_path = os.path.join(root_dir, ticker)
        if not os.path.exists(output_path):
            os.mkdir(output_path)
        self.output_path = output_path

        self.batch_size = batch_size
        self._scraped_records = 0
        self._scraper = NASDAQOptionsScraper()

    def serialize(self, **kwargs):
        records_generator = self._scraper(self.ticker, **kwargs)
        for items in batched(records_generator, batch_size=self.batch_size):

            if items:
                timestamp = datetime.datetime.utcnow().strftime(
                    self.output_file_date_fmt)
                file_name = f"{self.ticker}_{timestamp}.{self.serialization_format}"
                self.serializer(items, os.path.join(self.output_path,
                                                    file_name))
                LOG.info("Scraped batch %s records", len(items))

                self._scraped_records += len(items)

        LOG.info("Scraped a total of %s records for %s", self._scraped_records, self.ticker)

    @staticmethod
    def _to_json(items: List[Mapping], file_path: str):
        items_to_serialize = {"items": items}
        with open(file_path, "w") as output_file:
            json.dump(items_to_serialize, output_file, indent=4)

    @staticmethod
    def _to_csv(items: List[Mapping], file_path: str):
        with open(file_path, "a") as csv_file:
            headers = list(items[0])
            writer = csv.DictWriter(csv_file,
                                    delimiter=",",
                                    lineterminator="\n",
                                    fieldnames=headers)
            writer.writeheader()  # file doesn't exist yet, write a header
            for item in items:
                writer.writerow(item)