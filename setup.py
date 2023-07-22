import README as README

setup(
    name="mlm2pro-gspro-connector",
    version="1.0.0",
    description="GSPro connector for MLM2PRO launch monitor",
    long_description=README.rd,
    long_description_content_type="text/markdown",
    url="https://github.com/springbok/MLM2PRO-GSPro-Connector",
    author="Etienne van Tonder",
    author_email="etiennevt@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    packages=["src"],
    include_package_data=True,
    install_requires=[

    ],
    entry_points={"console_scripts": ["realpython=src.__main__:main"]},
)