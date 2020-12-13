from itertools import islice
from typing import Generator

from lxml import etree


def get_text(elt):
    """
    Description:
        Returns the text from tags.

    Args:
        elt: An lxml etree element

    Returns:
        Text within the element.
    """
    return etree.tostring(elt, method="text", encoding="unicode").strip()


def batched(gen: Generator,
            batch_size: int):
    """
    Description:
        A util to slice a generator in a batch_size.
        The consumer can consume the generator in batches of given batch_size

    Args:
        gen: The generator to be consumed.
        batch_size: Consume batches of what size ?

    """
    while True:
        batch = list(islice(gen, 0, batch_size))
        if len(batch) == 0:
            return
        yield batch
