#!/usr/bin/env python
# -*- coding:utf-8 -*-

#############################################
# File Name: setup.py
# Author: shierlou
# Mail: manbugv@gmail.com
# Created Time: 2019-08-27 10:27:00
#############################################


from setuptools import setup, find_packages

setup(
    name="wulaisdk",
    version="1.1.9",
    description="Laiye Wulai SDK for Python Programming Language",
    long_description="Laiye Wulai SDK for Python Programming Language",
    license="LICENSE Apache 2.0",

    url="https://github.com/laiye-ai/wulai-openapi-sdk-python",
    author="shierlou",
    author_email="manbugv@gmail.com",

    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=["requests"]
)
