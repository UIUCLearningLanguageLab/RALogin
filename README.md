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
Environment="PATH=/home/ph/RALogin/venv/bin"
ExecStart=/home/ph/RALogin/venv/bin/gunicorn --workers 3 --bind unix:/home/ph/RALogin/ralogin.sock -m 007 wsgi:app
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
A symbolic link was created like so:

```bash
sudo ln -s /etc/nginx/sites-available/ralogin /etc/nginx/sites-enabled
```


## Update 

To update the app, do:

```bash
cd /home/ph/RALogin
git pull
sudo systemctl restart nginx
```