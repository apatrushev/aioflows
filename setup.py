from setuptools import setup


setup(
    name='aioflows',

    use_scm_version=True,
    setup_requires=[
        'setuptools_scm',
    ],

    author='Anton Patrushev',
    author_email='apatrushev@gmail.com',
    url='https://github.com/apatrushev/aioflows',

    description='Python data flows library to build structured applications',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    license='MIT',

    packages=[
        'aioflows',
    ],
    package_dir={
        '': 'src',
    },
    install_requires=[
        'cached-property',
        'janus',
    ],
    extras_require={
        'dev': [
            'pytest-asyncio',
            'spherical-dev[dev]>=0.2.20,<0.3',
        ],
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Framework :: AsyncIO',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries',
    ],
    # upper bound required due to the problem in cached-property
    # https://github.com/pydanny/cached-property/pull/267
    python_requires='>=3.8,<3.11',
    zip_safe=True,
)
