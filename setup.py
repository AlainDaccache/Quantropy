import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="AlainDaccache",
    version="0.0.1",
    author="Alain Daccache",
    author_email="alain.daccache@mail.mcgill.ca",
    description="Package to research, develop, and deploy investment strategies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AlainDaccache/Quantropy/",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
