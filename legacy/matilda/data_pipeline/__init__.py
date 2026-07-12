"""
The curse of data

Google and Yahoo finance have a survivorship bias -- they only include firms that are still around.
I know of no free source that provides the data you seek. I get my data from Compustat and CRSP via
the Wharton Resource Data Service, but these (or Bloomberg or Reuters) are likely too expensive for
an individual.

Not only you have to worry about survival bias, you have to deal with all sort of corporate action, like split,
spin-off and dividends. For example, if you look at the historical data for MSFT, you will see a
big drop when they paid out special dividend. Also you have to know that many companies go through
name/entity change. CRSP provide PERMNO ( permanent number) that stitches all these changes.
CRSP data is stored in a binary format so you are required to write your own loader in C or Fortran.

"""