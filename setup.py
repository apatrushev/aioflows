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
    license='MIT',

    packages=[
        'aioflows',
    ],
    package_dir={
        '': 'src',
    },
    install_requires=[
        'cached-property',
    ],
    extras_require={
        'dev': [
            'isort<5',
            'pytest-asyncio',
            'spherical-dev[dev]>=0.1.0,<0.2',
        ],
    },
    zip_safe=True,
)
