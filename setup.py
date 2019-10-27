import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="dsbapipy",
    version="0.0.3",
    author="nerrixDE",
    author_email="nerrixde@mailfence.com",
    description="API fuer die DSBMobile Vertretungsplan-App",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nerrixDE/DSBApi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5',
)
