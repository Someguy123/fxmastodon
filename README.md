# FxMastodon - Fix Mastodon Embeds

FxMastodon is a web application similar to the popular FxTwitter and VxTwitter services, which allow you to
put fx or vx infront of a twitter URL to fix the embeds on discord, especially for videos and multi-image posts
on mobile.

But unlike those, this is designed for Mastodon, and works across all Mastodon instances that have the standard
statuses API available.

Currently, there's just one instance of FxMastodon deployed, which is managed by the creator of FxMastodon - Someguy123,
and is available at [https://fxmas.to/](https://fxmas.to/)

## How to use FxMastodon

As a random example, we'll use the following post from `@wonderofscience` on mastodon.social:

```
https://mastodon.social/@wonderofscience/110723800573904226
```

To pass this through FxMastodon, simply prepend the FxMastodon domain to the start, followed by a slash,
for example with the main fxmas.to instance:

```
https://fxmas.to/mastodon.social/@wonderofscience/110723800573904226
```

Much like Fx/VxTwitter, fxmas.to will output appropriate meta tags to ensure the image/video is embedded properly on Discord
and other platforms, even if the content is marked sensitive.

If a user clicks on the fxmas.to link, it will redirect them to the original post, in this case, on mastodon.social

## How do I run my own FxMastodon instance?

This project is quite simple to deploy, and it's code is also very simple, so it's easy to modify if you wanted to do so.

You'll need:

- A Linux or Unix system (may work on Windows but YMMV!)
- Python 3.7 or newer (pipenv assumes you have 3.9 but you can override it in Pipenv if needed)
- Basic command line knowledge

First make sure you have Python 3.9 (or at least 3.7+) installed:

```
sudo apt update
sudo apt install python3.9 python3.9-pip
```

### Option 1. - Using Pipenv (Strongly recommended, otherwise the systemd service will not work)

NOTE: If you're not using Python 3.9.x you'll need to adjust the python version in the `Pipenv` file, and run `pipenv install --ignore-lockfile` instead of `pipenv install`

Become root if you aren't already:

```
sudo su -
```

Install Pipenv for the version of python you're using, if you have Python 3.9 we recommend using that so that you don't need to mess with the Pipenv file:

```
python3.9 -m pip install -U pipenv
```

For production use, create an account called `fxmastodon` and log into that user before cloning the repo, which will line up
with the default systemd service config:

```
adduser --gecos "" --disabled-password fxmastodon

su - fxmastodon
```

Clone the repo and enter it:

```
git clone https://github.com/Someguy123/fxmastodon.git
cd fxmastodon
```

Install the requirements:

```
pipenv install
```

Activate the virtual environment to be able to run the app in development mode:

```
pipenv shell
```

Create a `.env` file incase you need to set any environmental variables:

```
touch .env
```

For development/testing, you can simply run app.py directly:

```
./app.py
```

The dev server will listen on 127.0.0.1:5000 which you can use for testing it out before putting it in production

For production, you should use the systemd service, or another method of running the following command in the background:

```
./run.sh serve
```

Once you've got the server running smoothly, it's time to install the systemd service so that it automatically starts
on boot and runs in the background with auto-restart if it crashes.

Log out of fxmastodon user:

```
exit
```

Now as root, we can install the systemd service:

```
cp /home/fxmastodon/fxmastodon/fxmastodon.service /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now fxmastodon
```

It should now be running in the background, listening on 127.0.0.1:8285 - you can verify the service is working properly
with the following command:

```
systemctl status fxmastodon
```

Once it's up and running, you can now plug it into a webserver such as Caddy or Nginx for production.

With Caddy it's as simple as putting the following config into /etc/caddy/Caddyfile :

```
mydomain.com, www.mydomain.com {
    reverse_proxy 127.0.0.1:8285
}
```

### Option 2. - Standard Pip (WARNING: Not compatible with the systemd service)

If for whatever reason you can't get pipenv working, it's possible to use standard `pip` to install the requirements,
as well as normal folder virtualenv, but be aware that the systemd service and run.sh script aren't designed for this,
so you'd need to modify run.sh to use a standard virtualenv instead of pipenv, or edit the systemd service to run it directly.

The steps are mostly the same as Option 1., however instead of using `pipenv install` and `pipenv shell`, you'd do:

Clone the repo, cd into it, then create a normal virtualenv:

```
git clone https://github.com/Someguy123/fxmastodon.git
cd fxmastodon

python3.9 -m venv venv
```

Activate the virtualenv:

```
./venv/bin/activate
```

Install requirements inside the venv:

```
pip3 install -r requirements.txt
```

Run the dev server by hand (you can't use run.sh serve unless you modify it):

```
./app.py
```

To be able to use the systemd service after using this method, you'll have to modify the `serve` section of `run.sh` so that
it activates the virtualenv manually and runs gunicorn within it


## License

This project is licensed under MIT X/11 license - see the file `LICENSE` for full license info.

TLDR of the license: you can do what you want, as long as you always display the original MIT license in the project,
and you can't hold us responsible if you're harmed by the project in some way.


