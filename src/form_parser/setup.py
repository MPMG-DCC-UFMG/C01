import setuptools

setuptools.setup(
    name='formparser',
    version='1.0',
    description='Module for parsing HTML forms',
    license="MIT",
    author='Rubia Guerra',
    author_email='rubia-rg@users.noreply.github.com',
    packages=setuptools.find_packages(),
    install_requires=['lxml', 'requests', 'selenium']
)
