---
title: Part 6, extended - Extra info on jQuery
date: 2022-10-23
description: Answering unresolved questions from the previous post
tags:
    [python, web, making_of, flask, plotly, flask_flatpages, javascript, jQuery]
---

[Part 6]({{ url_for('post', name='making_of_6') }})

It's a short post today, based on some conversations I've had with Pablo.
Hopefully it helps me remember how jQuery works and maybe anyone else who was
just as lost as I was.

In the [last post]({{ url_for('post', name='making_of_6') }}), I wrote:

> Then comes the script that loads the plot - I get the data using jQuery's
> `.getJSON` function. (`$` stands for jQuery, which has always been confusing
> to me.) After not understanding the documentation of this function really at
> all, I kind of hacked something together. In my understanding, the
> function/callback .done runs upon a successful completion of getting the JSON,
> and so I put my plotting code there. If the JSON isn't retrieved, it won't
> plot.
>
> The `.done` function somehow has an input data from the getJSON function -
> this I don't understand at all.

This is my attempt at explaining `.done`.

## Looking at the jQuery documentation

I won't lie, I find the jQuery documentation to be very hard to understand.
[Here](https://api.jquery.com/jquery.getjson/) is the link for the `.getJSON`
function - tell me if you can off the bat understand why the `.done` method
works, and what arguments are available to the functions it calls.

The first thing to realize is that `.getJSON` is really just a convenience
wrapper for a more basic `$.ajax` function. Therefore, it makes a lot more sense
to look at the [`$.ajax` documentation](https://api.jquery.com/jQuery.ajax/)
instead.

### What is AJAX?

From [W3](https://www.w3schools.com/whatis/whatis_ajax.asp):

> AJAX is a developer's dream, because you can:

> -   Read data from a web server - after a web page has loaded
> -   Update a web page without reloading the page
> -   Send data to a web server - in the background

Glad that's all cleared up.

### What is returned by `.getJSON`?

Anyways, we make an AJAX request to the `covid_data` route, and I assumed that I
would just get some JSON data in return. That was the limit of my understanding
of the web. It would be in some sort of string representation or something that
the Plotly package could figure out.

<figure>
<img async src="https://media0.giphy.com/media/HX7pvh1mIqImc/giphy.gif" alt="Billy Madison gif">
<figcaption>This is what Chrome thinks of me.</figcaption>
</figure>

That is not the case. What is returned is a
[jqXHR](https://api.jquery.com/Types/#jqXHR:~:text=Mozilla%20Developer%20Network-,jqXHR,For%20more%20information%2C%20see%20the%20jqXHR%20section%20of%20the%20%24.ajax%20entry,-Thenable),
which is both unpronounceable and also not a string. The jQuery AJAX
documentation further states that as part of the response, there is a `.done`
callback (_note to self - what exactly is a callback_), and supplies the
following information:

> `jqXHR.done(function( data, textStatus, jqXHR ) {})`; An alternative construct
> to the success callback option, refer to `deferred.done()` for implementation
> details.

[`deferred.done()`](https://api.jquery.com/deferred.done) doesn't really help,
except to make it clear that these functions are called after a successful
request. However there is a hint, in the form of `(data, textStatus, jqXHR)` in
the function definition.

As an aside, the `.done` is necessary because Javascript tries to load
everything asynchronously, thereby populating a web page before every little
part has been loaded. Because of this, you cannot assume that Javascript will
run top to bottom, as it can skip lines if it is waiting and then come back to
them (or at least that is what I understand). The `.done` callback makes sure
that if you have code that relies on some response, the response is completed
before the code runs. In our case, the plot cannot be drawn without the data
being fetched. For completeness, there are other callbacks like `.fail`,
`.always`, and `.then`, which execute when the request fails, all the time, and
idk when, respectively.

## `success`

So, `deferred.done()` isn't very helpful, but the `.ajax` explanation of `.done`
does actually have a helpful part. Specifically, the part where it says it is
"... **an alternative construct to the success callback option**..."! Looking at
the `success` argument of `.ajax`, the documentation says the following:

> **`success`**
>
> Type: Function( Anything data, String textStatus, jqXHR jqXHR )
>
> A function to be called if the request succeeds. **The function gets passed
> three arguments**: The data returned from the server, formatted according to
> the dataType parameter or the dataFilter callback function, if specified; a
> string describing the status; and the jqXHR (in jQuery 1.4.x, XMLHttpRequest)
> object. As of jQuery 1.5, the success setting can accept an array of
> functions. Each function will be called in turn. This is an Ajax Event.

In the end this solves the mystery of what `.done` receives! The functions in
`.done` receive the response itself, which is formatted as JSON when using the
`.getJSON` wrapper, the status, and the whole jqXHR object (whose purpose I do
not know).

In Javascript, these are implicitly provided, so they can be given any name in
the order described above. For example, in my previous post with the interactive
plots, I used

```javascript
$.getJSON("/sine_graph/").done(function (data) {
    var layout = {};
    data.config = {
        responsive: true,
        showTips: false,
    };
    Plotly.newPlot("sine_chart", data, layout);
});
```

In this case, the response was called `data`, since it was the first argument
provided to `function`. I can then use it later in the function. However, it can
be called whatever I like, like `new_variable_name`,

```javascript
$.getJSON("/sine_graph/").done(function (new_variable_name) {
    var layout = {};
    new_variable_name.config = {
        responsive: true,
        showTips: false,
    };
    Plotly.newPlot("sine_chart", new_variable_name, layout);
});
```

and the code will still run. `new_variable_name` now contains the request from
the the desired URL, correctly formatted as JSON.

### Using the browser console to test code

One thing that is handy is to play around with this in the browser console. If
you open the [last post]({{ url_for('post', name='making_of_6') }}) and
[open the browser console](https://balsamiq.com/support/faqs/browserconsole/),
jQuery will be loaded and you can run something like

```javascript
$.getJSON("/covid_graph/").done(function (data) {
    console.log(data);
});
```

which will print the first argument `data` to the console. You'll see that it is
the data that Plotly requires.

If you change `data` to something else, you'll see you get the same response -
the JSON response is correctly getting passed to whatever variable you declare!
Mystery solved. I'm not entirely looking forward to a lot more jQuery/Javascript
in my future, but slowly things fit a little bit better together.

## Links

1. [jQuery.getJSON documentation](https://api.jquery.com/jquery.getjson)
2. [jQuery.ajax documentation](https://api.jquery.com/jQuery.ajax/)
3. [deferred.done documentation](https://api.jquery.com/deferred.done/)
4. [StackOverflow on `.done` arguments](https://stackoverflow.com/questions/13141028/what-arguments-are-supplied-to-the-function-inside-an-ajax-done)
5. [Difference between `success` and `.done`](https://stackoverflow.com/questions/23065907/why-does-jquery-getjson-have-a-success-and-a-done-function)
