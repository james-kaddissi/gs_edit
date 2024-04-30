from setuptools import setup, find_packages
from setuptools_rust import Binding, RustExtension
setup(
    name='GS-Edit', 
    version='0.2.6',
    description='The Best Code Editor - GS',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',  
    author='James Kaddissi',
    author_email='jameskaddissi@gmail.com',
    url='https://github.com/james-kaddissi/gsedit',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    package_data={
        'gsedit': ['css/*.qss', 'images/*.png', 'images/*.svg', 'images/*.qrc'],
    },
    rust_extensions=[RustExtension("gsedit.vc", "src/vc/Cargo.toml", binding=Binding.PyO3)],
    install_requires=[
        'PyQt5',
        'QScintilla',
        'jedi',
        'PyQt5-Frameless-Window'
    ],
    entry_points={
        'console_scripts': [
            'gs=gsedit.cli:run', 
        ],
    },
    python_requires='>=3.6',
)
