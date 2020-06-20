from pprint import pprint
import tabula

file = 'https://blfblob.blob.core.windows.net/files/Library/Assets/Gallery/BLF/Publications/Annual%20Reports/BLF%20Reports/Download%202014%20Annual%20Report/2014-Annual-Report-Interactive%20version.pdf'
tables = tabula.read_pdf(file, pages="4", multiple_tables=True)
pprint(table.to_string() for table in tables)
