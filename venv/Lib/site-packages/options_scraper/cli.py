import argparse
import logging
import os
from pprint import pformat

from options_scraper.serializer import NASDAQOptionsSerializer

LOG = logging.getLogger(__name__)


def main():
    """
    Description:
        Entry point to the options scraper

    """

    parser = argparse.ArgumentParser()
    parser.add_argument("-l",
                        "--log-level",
                        default="INFO",
                        choices=list(logging._nameToLevel.keys()))
    parser.add_argument("-t", "--ticker", help="Ticker Symbol")
    parser.add_argument("-o", "--odir", help="Output directory")
    parser.add_argument("-b",
                        "--batch_size",
                        help="Batch Size",
                        default=100,
                        type=int)
    parser.add_argument("-c", "--callput", choices=["call", "put"])
    parser.add_argument("-m",
                        "--money",
                        default="all",
                        choices=["all", "in", "out", "near"])
    parser.add_argument("-e", "--excode", help="excode")
    parser.add_argument("-x",
                        "--expir",
                        choices=["week", "stan", "quart", "cebo"])
    parser.add_argument(
                        "-s",
                        "--serialize",
                        help="Serialization format",
                        default="csv",
                        choices=["json", "csv"])
    args = parser.parse_args()

    logging.basicConfig(
        level=logging._nameToLevel[args.log_level],
        format="%(asctime)s :: [%(levelname)s] :: [%(name)s] :: %(message)s",
    )

    if args.ticker is None:
        raise ValueError("Ticker symbol not passed")

    if args.odir is None:
        raise ValueError("Output Directory not passed. Provide the complete path where you want to save the files")

    if not os.path.exists(args.odir):
        raise IOError("Path {0} does not exists".format(args.odir))

    kwargs = {
        "money": args.money.lower(),
        "expir": args.expir.lower() if args.expir else None,
        "excode": args.excode.lower() if args.excode else None,
        "callput": args.callput.lower() if args.callput else None,
    }

    LOG.info("VERIFY: arguments passed %s", pformat(kwargs))
    LOG.info("Serialization format is %s", args.serialize.upper())
    LOG.info("Batch Size is %s", args.batch_size)

    serializer = NASDAQOptionsSerializer(
        ticker=args.ticker,
        root_dir=args.odir,
        serialization_format=args.serialize.lower(),
    )
    serializer.serialize(**kwargs)
    LOG.info("Finished Scraping")