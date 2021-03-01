
# Use this command for deploy.
#   python3 setup.py sdist bdist_wheel && python3 -m twine upload --skip-existing dist/*

import io
from setuptools import find_packages, setup

setup(name='easy_athena',
      version='0.0.9',
      description='This package helps you use AWS Athena easily.',
      long_description="Please refer to the https://github.com/jaden-git/easy_athena",
      long_description_content_type="text/markdown",
      url='https://github.com/jaden-git/easy_athena',
      download_url= 'https://github.com/da-huin/jaden-git/archive/master.zip',
      author='JunYeong Park',
      author_email='dahuin000@gmail.com',
      license='MIT',
      packages=find_packages(),
      install_requires=["boto3"],
      classifiers=[
          'Programming Language :: Python :: 3',
    ]
)


