from setuptools import setup

setup(name='govtrack2csv',
      version='1.0.1',
      description='Toolset for converting govtrack data to csv.',
      url='http://github.com/hackthefed/govtrack2csv',
      status='alpha',
      author='Hack The Fed',
      author_email='vance@hackthefed.com',
      license='GPL',
      packages=['govtrack2csv'],
      scripts=['bin/convert_congress'],
      install_requires=[
          'pandas',
          'pyyaml'
      ],
      zip_safe=False)
