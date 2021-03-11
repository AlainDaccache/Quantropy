# print(Filing.objects.as_pymongo())  # returns list of all filing objects

    # get filings for which assets > $100
    # filings = Filing.objects(BalanceSheet__Assets__TotalAssets__gt=100)
    # print(filings.as_pymongo())

    # won't work because Company is a Reference document for Filings, not embedded document
    # print(Filing.objects(company__cik__="0123456789"))  # returns filings for company with cik
    # this will:
    # companies = Company.objects(cik="0123456789")
    # filings = Filing.objects().filter(company__in=companies)
    # print(filings.as_pymongo())
