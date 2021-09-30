# RALogin
Python web server that enables RAs to perform simple tasks on lab server


## Setup

THe Flask app is located on the server in `/home/ph/ralogin`. 
It is behind a NGinx server listening on on port 5001.

A symbolic link was created like so:

`sudo ln -s /etc/nginx/sites-available/ralogin /etc/nginx/sites-enabled`