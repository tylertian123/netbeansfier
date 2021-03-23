from setuptools import setup

with open("requirements.txt", "r") as fh:
    install_requires = fh.read().splitlines()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="netbeansifier",
    version="1.0.0",
    author="Tyler Tian",
    author_email="tylertian123@gmail.com",
    include_package_data=True,
    zip_safe=False,
    description="Simple and dumb Python script that packages up Java files into a basic NetBeans project for ICS4U.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tylertian123/netbeansifier",
    packages=["netbeansifier"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=install_requires,
    python_requires=">=3.6",
    keywords=["netbeans"],
    entry_points={
        "console_scripts": ["netbeansify=netbeansifier:main"]
    }
)
