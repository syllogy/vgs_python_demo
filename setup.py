from setuptools import setup, find_packages
import sys

version = '0.0.1'

setup(
    name='homepage',
    author='Joe Viveiros',
    author_email='joe.viveiros@verygood.systems',
    version=version,
    description='VGS Demo',
    license='Other/Proprietary License',
    include_package_data=True,
    packages=['.'],
    install_requires=[
        "gunicorn==19.7.1",
        "requests==2.18.4",
        "Flask==0.12.2",
        "Flask-Admin==1.5.1",
        "Flask-SQLAlchemy==2.3.2",
   ],
)
