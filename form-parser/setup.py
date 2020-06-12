from setuptools import setup

setup(
   name='Form Parser',
   version='1.0',
   description='Module for parsing HTML forms',
   license="MIT",
   author='Rubia Guerra',
   author_email='rubia-rg@users.noreply.github.com',
   packages=['formparser'],
   install_requires=['lxml', 'requests', 'selenium']
)
