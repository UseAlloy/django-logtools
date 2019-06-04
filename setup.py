from setuptools import setup, find_packages

setup(
    name='django-logtools',
    version='0.0.7',
    description='Tools to help with logging in Django.',
    url='https://github.com/usealloy/django-logtools',
    author='Scott Clark',
    author_email='scott@alloy.co',
    license='MIT',
    packages=find_packages('logtools'),
    install_requires=['setuptools'],
    zip_safe=False)
