"""
Flask-Pony
----------

PonyORM for your Flask application.

GitHub
------

`Uses and documentation <https://github.com/kyzima-spb/flask-pony>`_

"""
from setuptools import setup, find_packages


setup(
    name='Flask-Pony',
    version='2.0.0',
    url='https://github.com/kyzima-spb/flask-pony',
    license='Apache-2.0',
    author='Kirill Vercetti',
    author_email='office@kyzima-spb.com',
    description='PonyORM for your Flask application',
    long_description=__doc__,
    packages=find_packages(),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'flask',
        'pony-database-facade'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
