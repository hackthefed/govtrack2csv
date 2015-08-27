"Hello World!"
--------------

This toolset is intented to convert the JSON Documents produced by govtrack.us
into csv files, a format that is more amenable to tools like pandas, spark, R,
and even the work horse of simple statistics, Microsoft Excel.

This project is in early development and is being shared mostly in an attempt to
gather feedback and ideas for shaping it's further growth.

**Requirements**

Intermediate Python Skills. If you have those then you know where to look, it's
kinda obvious. If you hate installing those requirements, I'm working on docker
image. Almost ready.

While govtrack2csv is pip installable it is not yet on pypi. It's also beyond
my willingness at this moment to explain how to install or use it. If you can
read code, most of what you need to know is in bin/convert_congress.__main__
If you can't read code, come back later, while I have much love for you, I'm
just not ready for you yet.. "I" needs to be "we" first.

You'll also need the data to act on.  Here is an rsync command you can run.
If you are just playing around, I recommend only grabbing one congress. That
way you don't tax the servers of a non-profit and save yourself several hours
of waiting.

`rsync -avz --delete --delete-excluded --exclude **/text-versions/ --exclude **data.xml --exclude **pdf govtrack.us::govtrackdata/congress/114  ./congress/114`

If what you are interested in is the resulting data, I'll have that up in a
few days. Follow @hackthefed  on twitter for updates.


License
-------
This project is GPL v3 and that matters. This project is not business friendly.
In fact, you're next. @hackthefed
