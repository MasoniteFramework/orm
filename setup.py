from setuptools import setup, find_packages

setup(
    name='masonite-orm',

    # Versions should comply with PEP440.  For a discussion on single-sourcing
    # the version across setup.py and the project code, see
    # https://packaging.python.org/en/latest/single_source_version.html
    version='0.0.1',
    package_dir={'': 'src'},

    description='Basic Boilerplate Package',
    long_description='Basic Boilerplate Package',

    # The project's main homepage.
    url='https://github.com/masoniteframework/orm',

    # Author details
    author='Your Name',
    author_email='you@example.com',

    # Choose your license
    license='MIT',

    # If your package should include things you specify in your MANIFEST.in file
    # Use this option if your package needs to include files that are not python files
    # like html templates or css files
    include_package_data=True,

    # List run-time dependencies here.  These will be installed by pip when
    # your project is installed. For an analysis of "install_requires" vs pip's
    # requirements files see:
    # https://packaging.python.org/en/latest/requirements.html
    install_requires=[
        'inflection==0.3.1'
    ],

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers
    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 3 - Alpha',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'Environment :: Web Environment',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: MIT License',

        'Operating System :: OS Independent',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',

        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

    # What does your project relate to?
    keywords='space separated keywords like this',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages().
    packages=find_packages(exclude=[
        'tests*',
        'app',
        'bootstrap',
        'config',
        'databases',
        'resources',
        'routes',
        'storage'
        ]),

    # List additional groups of dependencies here (e.g. development
    # dependencies). You can install these using the following syntax,
    # for example:
    # $ pip install -e .[dev,test]
    # $ pip install your-package[dev,test]
    extras_require={
        'test': ['coverage', 'pytest'],
    },

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    ## package_data={
    ##     'sample': [],
    ## },

    # Although 'package_data' is the preferred approach, in some case you may
    # need to place data files outside of your packages. See:
    # http://docs.python.org/3.4/distutils/setupscript.html#installing-additional-files # noqa
    # In this case, 'data_file' will be installed into '<sys.prefix>/my_data'
    ## data_files=[('my_data', ['data/data_file.txt'])],

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    ## entry_points={
    ##     'console_scripts': [
    ##         'sample=sample:main',
    ##     ],
    ## },
)
