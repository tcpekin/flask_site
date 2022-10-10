---
title: The making of this blog, part 2 - General framework
date: 2022-10-09
description: Initially working with Flask
tags: [python, web, making_of, flask]
---

[Part 1]({{ url_for('post', name='making_of_1') }})

The whole site source code can be seen
[here](https://github.com/tcpekin/flask_site), and I'll link to specific parts
as they come up.

## Basic ideas

With the idea of the site somewhat decided, the first step was to knock down
some small goals - figure out how Flask works at all, and generate a site
locally. Luckily there are many
[Flask tutorials](https://flask.palletsprojects.com/en/2.2.x/quickstart/) that I
could rely on, and using a combination of Flask and a Flask extension called
[Flask-FlatPages](https://flask-flatpages.readthedocs.io/en/latest/), I could
eventually (after some frustration) turn Markdown files into static pages,
perfect for a home page, About page, or the blog posts you're reading. The
process to do so is relatively simple in retrospect, but very complicated to
figure out the first time. The general idea is to create a HTML template (or
templates, they can inherit sections from each other) that has tags/sections
that can be filled in through a templating engine Jinja, and then use Flask to
give the templating engine the relevant info that to fill in at the right
position.

The first hurdle was a universal navigation bar that would be shared between all
of my pages, which requires inheritance between templates. In the end, I have a
[`layout.html`](https://github.com/tcpekin/flask_site/blob/master/templates/layout.html)
file that is the parent template that all others build off of, and this file is
the one that contains the navbar. Template inheritance is controlled by
[Jinja](https://flask.palletsprojects.com/en/2.2.x/templating/), and to be
honest, I haven't explored it a lot beyond what is necessary. In that same
folder I put the rest of my templates, some which are for a specific page, and
others that have more reusability.

## Routes - i.e. making URLs

Once the templates are set up, you want to actually see them, so you have to
configure Flask to interact with said templates. This requires making a `.py`
file, in my case
[`blog.py`](https://github.com/tcpekin/flask_site/blob/master/blog.py), in which
you instantiate a Flask `app`, and then define routes, to which it will react.
This is one by using a `@app.route` decorator, which contains the endpoint/url
which you want to serve, and decorates a function that takes an arbitrary number
of inputs. These inputs can then be used to do some computation, but the
`return` of this function is the function `render_html` (imported from `Flask`),
which takes a template name and additional arguments corresponding to blocks in
the HTML template that should be filled in.

With the help of a blog or two, it is pretty <s>easy</s> possible to set up this
and Flask Flatpages to server Markdown files as HTML. In doing so, I was exposed
to how Flask uses `@app.route('/path/<variable>)`, where `<variable>` in the
decorator is in `<>` pointy brackets, which then transfers the variable part of
the url to the decorated function. This is a very handy way to get arguments
from a URL to your function, and I thought it could be used to do the dynamic
part of my site, the selected area diffraction simulation.

## Interactivity - responding to requests

First, I needed to be able to pass user input information to my app, so I
decided after testing both `POST` and `GET` requests,
[to go with `GET`](https://github.com/tcpekin/flask_site/blob/a3052b2a59e6f7b2f0d683eae802315b8a7498ab/templates/dp_sim.html#L4),
as it is more user transparent. The nuances are lost on me, but the big
differences seem to be a `POST` request sends information to the server without
changing the URL, and can send hidden stuff, files, etc., whereas a `GET`
request modifies the url after a `/?`, with each parameter in a `key=value`
pair, separated by `&`s. Flask has a function `request` that can parse these
from the url, which can be used within the body of the decorated function, which
is great. To actually get the user input, I used an HTML form that had two
inputs, one for the structure and the second for the orientation. The
orientation one could take any series of numbers, either in `hkl` format or
`h,k,l` format, and the structure box you can type in any Materials Project
identifier, with a dropdown box with the most common options pre-populated.
Getting these to retain state upon hitting submit wasn't the simplest, but was
doable, using the `success` flag mentioned in the next paragraph. This area
still has room for improvement, there must be a much more ergonomic way to 🤷‍♂️.

Getting py4DSTEM to output the correct output was the next challenge, but wasn't
in retrospect so hard. I got the simulation functions first working in a Jupyter
notebook, and then put them into my main `blog.py` file. These functions took
the structure as well as orientation and originally saved an image. This had to
be modified to work for the web. Since I didn't want to be changing the url on
the user a lot, I made a
[section](https://github.com/tcpekin/flask_site/blob/a3052b2a59e6f7b2f0d683eae802315b8a7498ab/templates/dp_sim.html#L49)
on the main simulation HTML template that only showed if a `success` flag was
set to `True`. In this block, I load two images, which correspond to the
diffraction pattern and the crystal in real space, with paths like
`/dp_sim/img/<structure>_<h>_<k>_<l>_dp_plot.png`. These routes then correspond
to my Python
[functions](https://github.com/tcpekin/flask_site/blob/e3e227d23c53a0ba6894d72f0897447e96adc321/blog.py#L84)
that call py4DSTEM with the proper `structure` and `h,k,l` orientation! So, if
the user submits a good input, there is a section of the HTML template that is
activated. This requests two images, which are then generated by my functions!

### Matplotlib oddities... as expected

A couple of tricky things emerged at this point - you can't use the regular
Matplotlib backend when you don't have a GUI interface. This means that instead
I had to create a SVG figure canvas, which can take a Matplotlib figure and
print a SVG from it (all hail vector graphics). This was printed to an `io`
object, which then was sent back as a Flask `Response`. It follows
[this StackOverflow post](https://stackoverflow.com/questions/50728328/python-how-to-show-matplotlib-in-flask)
pretty closely, but switches the backend from `FigureCanvasAgg` to
`FigureCanvasSVG`. To be honest, this is all still pretty confusing to me, but
it works well in practice! Then it was just a little bit of CSS to make things
look <s>good</s> not bad, and the bones were there!

Regarding CSS - this is still the most confusing. Just not knowing the syntax is
difficult, how things inherit from their parent `div`s or whatever, and how
classes work. The CSS needs to really be improved for the site. Once I
understand it a bit more, or if I do anything interesting with it, I will either
make a new post or just extend this section.

However, at this point, everything was running well locally - structures could
be pulled in from the Materials Project, then their corresponding orientations
and diffraction patterns were simulated, and finally served up as SVG images!

[Part 3]({{ url_for('post', name='making_of_3') }})
