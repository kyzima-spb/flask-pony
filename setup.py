"""
Flask-Pony
-------------


"""
from setuptools import setup, find_packages

from flask_pony import __version__ as version


setup(
    name='Flask-Pony',
    version=version,
    url='https://github.com/kyzima-spb/flask-pony',
    license='BSD',
    author='Kirill Vercetti',
    author_email='office@kyzima-spb.com',
    description='',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'pony'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
