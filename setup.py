from setuptools import find_packages, setup

setup(
    name='VIS',
    version='1.10',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)