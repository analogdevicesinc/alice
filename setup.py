import re

import setuptools

# From: https://github.com/smartcar/python-sdk/blob/master/setup.py
def _get_version():
    """Extract version from package."""
    with open("alice/__init__.py") as reader:
        match = re.search(
            r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', reader.read(), re.MULTILINE
        )
        if match:
            return match.group(1)
        else:
            raise RuntimeError("Unable to extract version.")


try:
    with open("README.md", "r") as fh:
        long_description = fh.read()
except:
    long_description = "Active Learning Interface (for) Circuits (and) Electronics"

setuptools.setup(
    name="alice",
    version=_get_version(),
    author="Doug Mercer",
    description="Active Learning Interface (for) Circuits (and) Electronics",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/analogdevicesinc/alice",
    packages=setuptools.find_packages(),
    package_data={"alice": ["resources/*"]},
    python_requires=">=3.6",
    install_requires=["numpy", "tk"],
    scripts=[
        "alice-desktop-1.3.pyw",
        "dc-meter-source-tool-1.3.pyw",
        "ohm-meter-vdiv-1.3.pyw",
        "strip-chart-tool-1.3.pyw",
        "data-logger-tool-1.3.pyw",
        "volt-meter-tool-1.3.pyw",
    ],
    zip_safe=False,
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
