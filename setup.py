"""
Flask-Pony
-------------


"""
from setuptools import setup


setup(
    name='Flask-Pony',
    version='0.0.4',
    url='https://github.com/kyzima-spb/flask-pony',
    license='BSD',
    author='Kirill Vercetti',
    author_email='office@kyzima-spb.com',
    description='',
    long_description=__doc__,
    py_modules=['flask_pony'],
    # if you would be using a package instead use packages instead
    # of py_modules:
    # packages=['flask_pony'],
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
