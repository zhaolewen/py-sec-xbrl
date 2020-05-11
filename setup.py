import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
     name='py-sec-xbrl',
     version='0.1',
     author="Lewen Zhao",
     author_email="zhaolewen@gmail.com",
     description="SEC Edgar Parser based on Python 3",
     long_description=long_description,
   long_description_content_type="text/markdown",
     url="https://github.com/zhaolewen/py-sec-xbrl",
     packages=setuptools.find_packages(),
     classifiers=[
         "Programming Language :: Python :: 3",
         "License :: OSI Approved :: MIT License",
         "Operating System :: OS Independent",
     ],
 )
