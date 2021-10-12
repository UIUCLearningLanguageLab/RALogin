# RALogin
Python web server that enables RAs to perform simple tasks on lab server


## Setup

The Flask app is located on the UIUC lab file server in `/home/ph/ralogin`. 

The app is exposed by Gunicorn, which was setup with:
```bash
gunicorn --bind 0.0.0.0:5001 wsgi:app
```

The app is run continuously as a service. 
The config file for the service is located in `/etc/systemd/system/ralogin.service` and contains:

```
[Unit]
Description=A Python FLask app served by Gunicorn to login RAs to a multi-purpose interface
After=network.target
[Service]
User=ph
Group=www-data
WorkingDirectory=/home/ph/RALogin
Environment="PATH=/home/ph/RALogin/bin"
ExecStart=/home/ph/RALogin/bin/gunicorn --timeout 60 --workers 3 --bind unix:/home/ph/RALogin/ralogin.sock -m 007 wsgi:app
[Install]
WantedBy=multi-user.target
```

This means we can control the service with:

```bash
sudo systemctl start flaskapp
sudo systemctl enable flaskapp
sudo systemctl status flaskapp
```

NGinx was setup to pass web requests on port 5001 to the socket provided by the service.
To do so, modify `/etc/nginx/sites-available/ralogin`:

```
server {
        listen 5001;

        location / {
                proxy_pass http://unix:/home/ph/RALogin/ralogin.sock;
                include proxy_params;
        }
}
```

The line `include proxy_params;` is necessary so that the redirect after form submission works correctly.

A symbolic link was created like so:

```bash
sudo ln -s /etc/nginx/sites-available/ralogin /etc/nginx/sites-enabled
```


## Update 

To update the app, push local changes to GitHub, and then, on the server:

```bash
cd /home/ph/RALogin
git pull
sudo systemctl restart ralogin
sudo systemctl restart nginx
```