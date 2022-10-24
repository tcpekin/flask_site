This is my personal site built using Flask.

# Build Notes

## How to create a [conda lockfile](https://github.com/conda-incubator/conda-lock) from a Mac to a Linux server

```sh
# Install `conda-lock` in the correct conda environment.
conda install -c conda-forge conda-lock

# Generate a `.yml` file that describes what you installed _manually_.
conda env export --from-history > env_name.yml

# Convert the `.yml` file to a lockfile. -p signifies what architecture you're targeting
conda lock -f env_name.yml -p linux-64
```

This will output a file titled `conda-linux-64.lock`.

## Docker notes

1. Images are collected programs and things you install - they are a fixed base
   for later execution in containers.
2. When you execute code, you use a container. A container is based off an
   image, and then runs the `CMD` line.
    1. Since this is our flask server, it does not return. Otherwise it returns
       and (I think) exits.
3. Use `conda` to install everything, using the lockfile.
    1. Give it a prefix with the `-p` argument.
    2. Reference it later in the `CMD` line by its full path - this is simplest.
4. `ADD` vs. `COPY`
    1. `ADD` has some extra magic, mainly extracting `.tar.gz` files, and the
       ability to add things from URLs. s
    2. `COPY` is preferred and is simpler to understand.
5. To build a Docker image, first create a Dockerfile. This feels very arcane to
   me. In the Dockerfile, you set up your computing infrastructure - use a
   `FROM` statement to base your image off another (like getting Ubuntu or
   Debian), execute some code with `RUN`, set up an `ENTRYPOINT` and/or a `CMD`
   (see
   [here](https://stackoverflow.com/questions/21553353/what-is-the-difference-between-cmd-and-entrypoint-in-a-dockerfile)
   for the differences), and then build the image.
6. To build the image, run `docker build --tag <tag_name>`, in my case
   `python-docker`. The tag name simply names the container.
7. `docker ps` lists running containers.
8. The name returned from the previous command can be used to execute random
   code in the running container. The command is
   `docker exec -it <name> /bin/bash`, which then drops you into a terminal.
9. To run the container on an M1 Mac, run
   `docker run --platform linux/amd64 --rm --publish 5001:5001 python-docker`.
    1. The `--platform` part is required to run on the M1 chip, I don't know
       exactly why
    2. `--rm` removes the container after shutdown, otherwise it just hangs
       around.
    3. `--publish local_port:container_port` links the two ports, and the local
       port comes first. This can be more complex (auto-assignment, assigning
       ranges, etc. See documentation)
    4. `python-docker` is simply the tag of our image when we built it.

After all this, I have switched to a Docker compose style deployment. Why is
this? It is because Docker containers (to my knowledge) can only run/be left
running with one command that speaks to the outside world. I needed therefore
two containers, 1 for the app and 1 for nginx, to pass things to the app. This
is a multi-container deployment, and it gets hard to manage this using the CLI.
A compose file, one for local development and one for production is the path
forward. In that, you can expose ports (`expose`d ports only talk to other
containers, not the outside world, unlike `publish`ed ports), provide platform
names, and set container dependencies. It makes making the containers talk to
each other much simpler actually, but then you need to write more slightly more
code.

Once I decided on this, it is relatively simpler to get the application/website
up and running - to build and run I simply call
`docker compose -f docker-compose.dev.yaml up --build`, and to take down,
`docker compose -f docker-compose.dev.yaml down -v`. Everything else is defined
in the config file. Some details are shown
[here](https://www.python4networkengineers.com/posts/python-intermediate/how_to_run_an_app_with_docker/).

With regards to logging - this required me to set up a mount point, so that data
could persist after shutting down the container. This is relatively simple in
the `compose.yaml` file, I simply added the following lines:

```yaml
  web:
    ...
    volumes:
      - type: bind
        source: ./logs/
        target: /logs
```

The type is `bind`, which means it is a mount, not a Docker Volume, which is
more for like SQL databases that persist between containers. The mount is better
for data you want to extract outside of the container at the end of the day,
perfect for a log.

The source is the location on the actual hardware - I had to create a `logs`
folder, one way to keep it around in git is to include a `.gitignore` file
within the folder itself. See
[here](https://stackoverflow.com/questions/115983/how-do-i-add-an-empty-directory-to-a-git-repository)
for details. Finally, the `target` is just the folder (absolute location) in the
container itself. So since everything is pretty much always in the root
directory, it is there.

With regards to environment variables - in order to protect my secret API
key(s), I put them into a `.env` file and then just `scp`'d that file to my
remote server
(`scp -i ~/Downloads/ssh-key.key ./.env ubuntu@###.##.##.###:/home/ubuntu/flask_site/`).
You can load this file as environment variables in the Docker `compose` file!
This again just required adding

```yaml
  web:
  ...
    env_file:
      - ./.env
```

and then my API key will be loaded into the environment!

Useful links:

-   [How to shrink `conda` docker builds](https://uwekorn.com/2021/03/01/deploying-conda-environments-in-docker-how-to-do-it-right.html)

## Flask notes

1. There is a difference between running `python app.py` and
   `flask --app app run`, and the main one to my knowledge is that
   `__name__ == "__main__"` only in the first case! Otherwise, `__name__` is
   equal to the filename!
2. Flask has some very helpful environment variables (see `.flaskenv`). This
   makes the command simple to execute (`flask run`), and gives you control of
   ports and hosts.
3. Flask's default port is `127.0.0.1:5000`. When this is executed in a Docker
   container, that is only available to the container, and is not passed through
   to the outside. To fix this, you have to set the host for the app to
   `0.0.0.0`, and then it serves it to every open port. It's output is as
   follows:

    ```
     * Running on all addresses (0.0.0.0)
     * Running on http://127.0.0.1:5001
     * Running on http://172.17.0.2:5001
    ```

    This is ok (not sure if it is the best). Then, you can use Docker as before
    to publish/pass through the correct ports:
    `docker run --platform linux/amd64 --rm --publish 5001:5001 python-docker`

I am not sure yet if I need to
[deal with proxy headers](https://flask.palletsprojects.com/en/2.2.x/deploying/proxy_fix/)
on the Flask side of things.

[How to use blueprints to modularize a Flask app](https://stackoverflow.com/questions/15231359/split-python-flask-app-into-multiple-files)

## Gunicorn notes

1. We use `gunicorn` to actually server our content, and not the development
   Flask server. This changes our `CMD` to
   `CMD [ "/opt/env/bin/gunicorn", "-w", "2", "--bind", "0.0.0.0:5001", "blog:app" ]`.
   The main differences are that we can have a number of workers, `-w`, and we
   bind a specific port, to keep things still always on `5001`. Finally, we run
   our app in `blog.py` by finishing with `blog:app`.

## Nginx notes

I still have no idea at all how to use nginx. It seems 1000% arcane.
`proxy_pass` started working after I put a trailing slash on the `proxy_pass`
address.

I believe it works (in Docker) by defining an upstream server and port
(`flask_site` and `web:5001` in our case, where web is the name of the _Docker_
container. How it knows this I have no idea). Then nginx listens for anything on
port 80 (default port for `https`), and then passes it to `flask_site`, defined
upstream. Some headers are set, not sure what they do.

In order to make this work, I had to make a separate nginx container, located in
`services/nginx`, with its own Dockerfile and a `nginx.conf` file that replaces
the default. This _seemed_ to work.

Useful links:

-   [`proxy_pass` info](https://dev.to/danielkun/nginx-everything-about-proxypass-2ona)
-   [Difference between `0.0.0.0`, `127.0.0.1` and `localhost`](https://stackoverflow.com/questions/20778771/what-is-the-difference-between-0-0-0-0-127-0-0-1-and-localhost)
-   [Reverse proxy docs](https://docs.nginx.com/nginx/admin-guide/web-server/reverse-proxy/)
-   [Configuring nginx for a Flask application](https://www.patricksoftwareblog.com/how-to-configure-nginx-for-a-flask-web-application/)
-   [How to use the official nginx image](https://www.docker.com/blog/how-to-use-the-official-nginx-docker-image/)
-   [How to use nginx with Flask](https://linuxhint.com/use-nginx-with-flask/)

## Cloud notes

I've chosen the Oracle free tier for hosting. To get the virtual private server
(VPS) speaking to the outside world I used
[this tutorial](https://docs.oracle.com/en-us/iaas/developer-tutorials/tutorials/apache-on-ubuntu/01oci-ubuntu-apache-summary.htm).

Other useful links:

-   [Ubuntu+Docker on Oracle Cloud](https://medium.com/oracledevs/run-always-free-docker-container-on-oracle-cloud-infrastructure-c88e36b65610)
-   [Install Docker on Ubuntu](https://docs.docker.com/engine/install/ubuntu/)
-   [Fix Docker permissions](https://www.digitalocean.com/community/questions/how-to-fix-docker-got-permission-denied-while-trying-to-connect-to-the-docker-daemon-socket)

## TODO

-   [ ] Logging/analytics
-   [ ] HTTPS - via docker?
-   [ ] `nginx` static files update
-   [ ] Simulation **g** vectors
-   [ ] Simulation table of most common zone axes
-   [ ] CSS Update
-   [ ] Modularize `blog.py`
