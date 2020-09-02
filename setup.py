import setuptools

setuptools.setup(
    name='C04',
    version='0.1',
    classifiers=["Programming Language :: Python :: 3"],
    install_requires=[
        'django==2.1', 'django-crispy-forms', 'djangorestframework',
        'scrapy', 'requests', 'pytest'
    ],
)
