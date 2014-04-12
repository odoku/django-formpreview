from setuptools import setup, find_packages


setup(
    name='django-formpreview',
    version='0.1.0',
    description='Previewable class based form views for Django.',
    author='odoku',
    author_email='contact@odoku.net',
    keywords='django,form,preview',
    url='http://odoku.net',
    packages=find_packages(exclude=['example.*']),
)
