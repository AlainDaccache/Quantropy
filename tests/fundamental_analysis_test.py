import unittest
from datetime import datetime

from data.database.db_crud import get_atlas_db_url, connect_to_mongo_engine
from fundamental_analysis import financial_statements_entries as entries


class TestFinancialStatementsEntries(unittest.TestCase):
    def setUp(self):
        atlas_url = get_atlas_db_url(username='AlainDaccache', password='qwerty98', dbname='matilda-db')
        self.client = connect_to_mongo_engine(atlas_url)

    def test_current_assets(self):
        asserts = [76219000000, 89378000000, 304441000000, 0]
        for i, period in enumerate(['Q', 'FY', 'TTM', 'YTD']):
            with self.subTest(i=i):
                self.assertEqual(entries.total_current_assets(stock='AAPL', date=datetime(2016, 1, 1), period=period),
                                 asserts[i])

    def tearDown(self):
        self.client.close()


if __name__ == '__main__':
    unittest.main()
