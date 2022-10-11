---
title: The making of this blog, part 4 - Logging
date: 2022-10-11
description: Adding logs is a lot more complicated than I thought
tags: [python, web, making_of, flask, gunicorn, docker, nginx, cloud]
---

[Part 3]({{ url_for('post', name='making_of_3') }})

As of this writing, I still haven't purchased a domain name and therefore the
site is only accessible via direct IP address. Despite that, while I was looking
at the output of `nginx` on the server, I saw that the IP was actually hit!
Something requested the site!

My first thought - and still is my main thought - was that this is some sort of
web crawler/scraper that just goes through all the IPs.. it could be Google, it
could be some other search engine, or it could be private. In order to see who
is it though, or if there is a pattern, I wanted to set up some IP address
logging.

I thought this would be relatively straightforward, but ended up being anything
but. I had to 1) get the real IP address from within my application and 2), log
the IP address to a file. Seems simple right?

## Getting the real IP address

The first thing I wanted to tackle was getting the real IP address. In Flask,
there is an object you can import called
[`request`](https://tedboy.github.io/flask/generated/generated/flask.Request.html).
One of its attributes is `.remote_addr`, which is billed as being "the remote
address of the client". Straightforward, right? Import `request` and simply log
this value!

### `nginx` says not so fast

As the title suggest - this isn't really the case. Since in production we run
our app using `gunicorn` behind an `nginx` reverse proxy, if we do this naively
then we will just get the IP address of the reverse proxy, which (should be)
unchanging. Luckily, proxies can keep track of the IP addresses they see as they
pass through requests, and add this onto the request header. Unluckily, this can
be spoofed and is therefore a security concern.

In order to get around this, you have to tell Flask how many proxies it is
behind, using
[`ProxyFix`](https://werkzeug.palletsprojects.com/en/2.2.x/middleware/proxy_fix/).
This is... complicated when you don't know a ton about HTML headers. In the end
I think I pieced it together, but if this was ever to be actually put into
practice for a business, I would have someone more knowledgeable look at it.

The first step to telling Flask how many proxies there are is to correctly set
up `nginx`. I set up
[the following](https://github.com/tcpekin/flask_site/blob/9310160babbe13d362ea296f43166baa4778ec2a/services/nginx/nginx.conf)
`nginx.conf` file, setting the following headers: `X-Forwarded-For`, `Host` and
`X-Real-IP` with variables provided by `nginx`. In the end, I think the one that
matters the most is `X-Real-IP`, as it was unchanging during my testing.

Once those were set, you can now begin to access the IP(s) in the Flask app,
with the previously mentioned `request.remote_addr`. To test that this was the
correct way to go about it, I falsified some headers using `curl`
(`curl --header "X-Forwarded-For: 1.2.3.4" http://localhost:9000`, where I
tested falsifying `X-Forwarded-For`, `Host` and `X-Real-IP`), and saw what was
returned. Many tutorials online say to look at the last (or correctly numbered)
value in `request.access_route`, but this is where the falsified info went, and
it never went into `.remote_addr` _in my experience_.

Things were moving in a positive direction and the correct IP addresses were
being at least printed to `stdout`.

## Logging says not so fast

Now - time to write to a file. Luckily Python has `logging` built into the
standard library, unluckily, the Basic Config version prints too much other
stuff (mostly from Matplotlib). To make a long story short, I had to initialize
this bit of code in the beginning of my `blog.py` file:

```python
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
fh = logging.FileHandler("./logs/ip_log.log", mode="a")
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)

logger.info("Log is working.")
```

It is relatively straightforward - import `logging`, create a `logger` instance,
set the
[level](https://www.logicmonitor.com/blog/python-logging-levels-explained) for
which warnings you want, make a `FileHandler`, and `Formatter`, and attach the
formatter to the file handler (`fh`), and then the handler to the logger. Then
you can just call `logger.info("insert message here")`.

AFTER doing all of this, I found out that Flask has a logger
[built in](https://flask.palletsprojects.com/en/2.2.x/logging/). I guess room
for future improvement.

Also room for improvement - change my logging call to a function decorator.
Right now, to log the IP on each page of my site, I have
`logger.info(f"{request.remote_addr} - {request.full_path} - {request.referrer}")`
within every route that I have, so multiple times and multiple places for error.
What I need to do in the future is change that line into a part of a `@log`
decorator, so I just can decorate each of my routes.

At this point things are looking good and my text file is getting written with
the IP addresses that access the site! (Let's be real... 99% only my IP).

## Docker says not so fast

Here I am, thinking things are going great, composing my Docker image, running
it.. and... nothing. No log files!

After looking into this, it turns out it is a noob mistake - containers are
isolated, so if I don't provide a mount point outside of the container,
everything inside of the container dies when it dies.

<figure>
<img async src="https://media.tenor.com/_iJpO6jfzVcAAAAC/stand-together-die-together-star-wars.gif" alt="star wars gif">
<figcaption>Depiction of a Docker container shutting down.</figcaption>
</figure>

The solution to this is to provide a mount point, which in the end is pretty
simple. Just adding

```yaml
  web:
    ...
    volumes:
      - type: bind
        source: ./logs/
        target: /logs
```

to my `compose` file was enough. Care has to be taken with regards to paths, but
remember, everything is at the root level in the container (at least how I've
set it up), so it all works. Using a relative path in the Flask app is required
to not go insane with paths. `source` is the path on the hardware, and `target`
is the path in the container. Note the `.` indicating relative path for
`source`!

Final note - this uses a Docker `mount` (as indicated by `type: bind`), not a
`Volume`. From what I could figure out, `mounts` are good for getting data out
of the container, while `Volume` is better for data that will stay inside the
container/be read by a future container. Most of the Docker documentation
recommends Volumes for their many benefits, but ease of access to the outside
world is a big plus for a `mount`ed drive.


## Conclusion

No huge takeaways here - this was a more complicated problem than I initially expected, but by breaking it down in to small component parts, I could work my way through it until everything worked (again). This required reconfiguring my reverse proxy, understanding how that worked to access the outside users' IP address within Flask, learning about `logging` and how to set that up (with room for future improvements), and finally configuring Docker to have a persistent storage location. The combination of these things resulted in a somewhat basic IP address logging system.

To improve it, as previously mentioned, I want to turn it into a decorator based system, as well as keep more header information (particularly if the requests are from robots or actual people... not sure how to figure that out yet).