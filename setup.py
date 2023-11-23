from setuptools import setup, find_packages

setup(
    name='chunk_pdf',
    version='0.1.1',
    description='When creating a PDF with a large number of pages using reportlab, it is slow and consumes a lot of resources. This was resolved by using chunk processing.',
    long_description='When creating a PDF with a large number of pages using reportlab, it is slow and consumes a lot of resources. This was resolved by using chunk processing.',
    author='Parkilwoo',
    author_email='bagilu3@gmail.com',
    url='https://github.com/parkilwoo/pdf_wrapper',
    install_requires=['reportlab', 'overrides'],
    packages=find_packages(exclude=[]),
    keywords=['pdf', 'reportlab'],
    python_requires='>=3.8',
    package_data={},
    zip_safe=False,
    classifiers=[
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Operating System :: OS Independent',
    ],
)