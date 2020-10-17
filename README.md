# LoL Data

I made some scripts to pull from a public API and store the data into a database. I then made a front end to display that data and do some other things. Tried to learn some new things along the way.

Now comes with a Docker file, but you'll have to modify config.toml and resources/python/general.cfg to point to a database. The server binds to port 5000 by default, so when running the image, make sure you use 

`docker run --publish {port}:5000  name:tag`

to access the site via localhost:{port} 

Find it here: Paulzplace.asuscomm.com

