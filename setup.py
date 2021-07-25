from setuptools import setup, find_packages

setup(
    name='django-sage-cache',
    packages=find_packages(exclude=['tests*']),
    include_package_data=True,
    version='0.1.0',
    license='GNU',
    description='queryset caching for Django',
    author='Sage Team',
    author_email='mail@sageteam.org',
    url='https://github.com/sageteam-org/django-sage-streaming',
    download_url='https://github.com/sageteam-org/django-sage-streaming/archive/refs/tags/0.1.0.tar.gz',
    keywords=['django', 'python', 'cache', 'SQL', 'queryset'],
    install_requires=[
        'Django',
        'django-filters',
        'djangorestframework',
        'cryptography',
        'django-redis'
    ]
)
