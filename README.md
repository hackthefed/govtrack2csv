# "Hello World!"

This toolset convert the JSON Documents produced by govtrack.us into csv files.
CSV are a format that is more amenable to tools like pandas, spark, R,
and even the work horse of simple statistics, Microsoft Excel.

We are currently in 1.0-alpha. This release has been tested on OS X 10.10 using
python 3.4 and 3.5 and also in our python-datakit docker image. Alpha in this
release has mostly to do with a lack documentation.

TL;DR

```
pip3 install govtrack2csv
mkdir data_home
cd data_home
mkdir congress_home
cd congress_home
rsync -avz --delete --delete-excluded --exclude **/text-versions/ --exclude **data.xml --exclude **pdf govtrack.us::govtrackdata/congress/114  ./congress/
rsync -avz --delete  govtrack.us::govtrackdata/congress-legislators  .
cd ..
mkdir csv
convert_congress ./congress_home ./csv
```



## Requirements

Python 3.4+
Pandas and it's requirements.

For some reason people seem to have difficulty installing Pandas. Given there
are packages for all linux's and it builds easily from brew on OS X, we really
don't understand this. However if you are having difficulty, try our python-datakit
docker image https://hub.docker.com/r/hackthefed/python-datakit. The image you
contains all the tools required to work with all our data science projects

That is as much support as you can expect from us on this topic. We made the
tools we use avaliable to you and we wish you luck.


## Installation

The easy way.

`pip3 install govtrack2csv`

The hard way

```
git clone git@github.com:hackthefed/govtrack2csv.git
cd govtrack2csv
pip3 install .
```

## Get the Govtrack.us data set

Govtrack is a pretty big data set. The JSON files that this project works on
total 10 GB. If you pull the whole data set you'll need 40GB to store it. One of
the reasons this projects exists is to pear down that dataset to what is
necessary to do analysis. The fist step is to pull only what we need from
govtrack.us.

We suggest you start out with just one congress.  You can add the others later.
Depending on your internet connection the following rsync could take from
5 minutes to an hour.

There are two root folders  we are going to want to pull; congress and
congress-legislators.

'''
mkdir congress
rsync -avz --delete --delete-excluded --exclude **/text-versions/ --exclude **data.xml --exclude **pdf govtrack.us::govtrackdata/congress/114  ./congress/

rsync -avz --delete  govtrack.us::govtrackdata/congress-legislators  ./congress-legislators
'''

When you are ready you call pull the rest of the congresses:

'''
rsync -avz --delete --delete-excluded --exclude **/text-versions/ --exclude **data.xml --exclude **pdf --exclude=**committee --exclude=**fdsys --exclude=**upcoming govtrack.us::govtrackdata/congress  .
'''

## Convert the data

This process can take awhile. I run it on a 2012 Macbook Pro with a 512 read
SSD. To do the whole congress it takes aobut 30 min. To do the 114th it take
about 5 minutes. On my 2008 Mac Pro with 8 cores and an SSD the data set takes
about 12 minutes. If you are a a 7200 rpm disk, it will take about 4 hours. If
you have a multi-core machine you'll want to set --threads. The default is 3.


```
convert_congress /path/to/base/dir /path/to/csv/dir
```

If what you are interested in is the resulting data, I'll have that up in a
few days. Follow @hackthefed  on twitter for updates.


License
-------
This project is GPL v3 and that matters. This project is not business friendly.
In fact, you're next. @hackthefed
