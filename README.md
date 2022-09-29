This is my personal site built using Flask.

# Build Notes

## How to create a conda lockfile from a Mac to a Linux server

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
