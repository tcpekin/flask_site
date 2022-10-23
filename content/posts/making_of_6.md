---
title: The making of this blog, part 6 - Interactive plots
date: 2022-10-20
description:
    Using Plotly with Flask and Flask-Flatpages to create interactive charts
tags:
    [
        python,
        web,
        making_of,
        flask,
        plotly,
        flask_flatpages,
        dash,
        pandas,
        data_visualization,
    ]
---

[Part 5]({{ url_for('post', name='making_of_5') }})

_Note, this page will only work with Javascript... sorry._

One of the goals I had for this site when starting was the ability to have
interactive plots. Making a beautiful figure is nice, but it is so much more fun
when you can zoom, have floating tooltips, and take advantage of the fact that
you're on a computer, not staring at a piece of printed paper.

## Plotting library comparison - why Plotly?

Basic plotting and data visualization in Python is not really such a contested
topic - just use [Matplotlib](https://matplotlib.org/), or
[Seaborn](https://seaborn.pydata.org/) if you're feeling fancy. I'm comfortable
using Matplotlib, and while
[I guess you can use it to create interactive HTML](https://www.freecodecamp.org/news/how-to-embed-interactive-python-visualizations-on-your-website-with-python-and-matplotlib/),
it's not really the right tool for the job if you want more full fledged
interactivity. While this post won't show the use of callbacks (the ability to
load different data at the press of a button on the same chart), it will show
some things with tooltips that (to my knowledge) are not really possible on the
web using Matplotlib.

<figure>
<img async src="{{url_for('static',filename='/assets/img/making_of_6/matplotlib.svg')}}" alt="Matplotlib line plot">
<figcaption><b>Fig. 1</b> Example of a very basic Matplotlib line plot, exported to SVG.</figcaption>
</figure>

<figure>
<img async src="{{url_for('static',filename='/assets/img/making_of_6/seaborn.svg')}}" alt="Seaborn line plot">
<figcaption><b>Fig. 2</b> The same plot, using the Seaborn <code>dark_grid</code> theme, exported to SVG.</figcaption>
</figure>

If you're willing to move beyond Matplotlib, there are a host of packages that
will help you achieve your goals. The major ones to me seem to be Plotly and
Bokeh, with Altair as a third option (see
[here](https://colab.research.google.com/notebooks/charts.ipynb) for a Google
Colab with all examples). I've played (briefly) with all three, but for the
purposes of this blog, I'll be using Plotly.

Why Plotly over Bokeh or another alternative? Based on the research I did, I
liked the structure of a Flask + Plotly project seen
[here](https://towardsdatascience.com/web-visualization-with-plotly-and-flask-3660abf9c946),
and the comparison done
[here](https://pauliacomi.com/2020/06/07/plotly-v-bokeh.html) seemed to make it
clear that Plotly would be better for me, as I'm not building a dashboard, think
native 3D support could be nice, and I don't want to (yet) mess with state. For
those reasons, I started with Plotly.

There will likely be another post where I make some of the same plots or a
dashboard with Bokeh...

## Integrating Plotly into my site's architecture

Once again - this site's
[source code](https://github.com/tcpekin/flask_site/tree/19bc882115424265e115c0358637774b21fa57b0).

At first I just kind of followed the tutorial linked in the previous section.
However, that tutorial is focused on making a chart on a specific page, or
route. That is all well and good, but not as flexible as I wanted it to be. It
relies on Flask's `render_template`, and passing in the JSON that describes the
chart during the page rendering. I realized this would be a problem, as I wanted
figures to be in my blog posts as well, which are Markdown files that are
rendered via
[Flask-Flatpages](https://flask-flatpages.readthedocs.io/en/latest/). Each post
is rendered with the following code:

```python
@app.route("/posts/<name>/")
def post(name):
    logger.info(f"{request.remote_addr} - {request.full_path} - {request.referrer}")
    path = "{}/{}".format(POST_DIR, name)
    post = flatpages.get_or_404(path)
    return render_template("post.html", post=post)
```

As you can see, the only optional variable that gets passed into
`render_template` is `post=post`, and I didn't see a good way of extending that
to include the plot JSON, in the case where a Plotly figure was in the `.md`
file.

I guess I could have an optional parameter, like `chart_data_list`, which is a
list, default of `None`, and some custom parser of `post` right before the
return that checks if there is any chart, and if so, calls the right url and
gets the JSON, appending it to the `chart_data_list`... but that idea just came
to me now, after everything is done and I think it wouldn't work in practice
anyways.

Another option might be to make a route that generates the whole plot, and then
just somehow linking that within a blog post? I will have to explore that idea
more too.

Anyways, here's what I did instead.

### Making the plot

I first started with the example plot in the tutorial (copied below), and it
worked very well.

```python
@app.route('/')
def notdash():
   df = pd.DataFrame({
      'Fruit': ['Apples', 'Oranges', 'Bananas', 'Apples', 'Oranges',
      'Bananas'],
      'Amount': [4, 1, 2, 2, 4, 5],
      'City': ['SF', 'SF', 'SF', 'Montreal', 'Montreal', 'Montreal']
   })
   fig = px.bar(df, x='Fruit', y='Amount', color='City',
      barmode='group')
   graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
   return render_template('notdash.html', graphJSON=graphJSON)
```

For clarification, if you don't want to click on the tutorial, `pd` is `pandas`,
`px` is `plotly.express`, and `json` is a Python standard library package.

However, I didn't want to return a rendered template from my route, but rather
just the JSON that could then be requested. In order to do so, I added
`from flask import Response`, and then replaced the return line with
`return Response(graphJSON, mimetype="application/json")`. Now, if you
[visit](<{{url_for('covid_graph')}}>) the endpoint that I was building, you'll
see that it's just a JSON response. Creating the response was now complete.

### Flatpages (markdown) + JavaScript + jQuery 😥

Now, how to get the JSON into a Flask-Flatpages-rendered page? I banged my head
against this problem for a while, as I didn't want to add more Javascript to the
site, or import any more libraries on the Javascript side, like jQuery, but in
the end, I couldn't figure out a good way to do so while avoiding that. What the
site needed to do is render the Markdown into HTML (Flask-Flatpages), and then
when/while the HTML is being served, populate the correct `<div>` that has the
plot with the required JSON from Flask. In the end, that meant doing something
with either Javascript, or using jQuery as a convenience.

My approach can be seen in this page's source in the repository, but I'll show
and describe it below. In the end it was relatively simple (but only after lots
of trial and error though, and thanks Pablo). First, the implementation:

```html
<div id="chart" class="chart"></div>
<script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>

<script type="text/javascript">
    $.getJSON("/sine_graph/").done(function (data) {
        var layout = {};
        data.config = {
            responsive: true,
            showTips: false,
        };
        Plotly.newPlot("chart", data, layout);
    });
</script>
```

So, what is happening here? First, I create a `<div>` with `id='chart'`, which
will be used to tell Plotly where to put the chart (it searches for `<div>`s
with the correct name). Then I source two Javascript libraries (_sigh_), the
first being Plotly, which is great, and the second being jQuery, which is
helpful, but not ideal as I wanted to minimize outside dependencies in order to
keep everything running snappily. In the end, when I profile the code though,
the Plotly library is about 1 Mb, while jQuery is about 80 kb, which I think is
ok.

Then comes the script that loads the plot - I get the data using jQuery's
`.getJSON` function. (`$` stands for jQuery, which has always been confusing to
me.) After not understanding the
[documentation](https://api.jquery.com/jQuery.getJSON/) of this function really
at all, I kind of hacked something together. In my understanding, the
function/callback `.done` runs upon a successful completion of getting the JSON,
and so I put my plotting code there. If the JSON isn't retrieved, it won't plot.

*Edit - I have added more explanation to what jQuery is doing/how it works in the [next post]({{ url_for('post', name='making_of_6_quick_note') }}).*

The `.done` function somehow has an input `data` from the `getJSON` function -
this I don't understand at all. But I can create a variable `layout` for Plotly,
as well as update the `config` of the returned JSON `data`, (to turn off an
annoying pop up when interacting with the graph, and to turn on responsiveness
in sizing), and then `Plotly.newPlot` the returned JSON... and it just works! It
feels like magic so far, I have almost 0 understanding of where the `data`
argument comes from. But we're in business 🎉!

Quickly I can define `/sine_graph/` in my app, which is called above:

```python
@app.route("/sine_graph/")
def sine_graph():
    import plotly.express as px

    x = np.linspace(0, 2 * np.pi, 100)
    y = np.sin(x) + np.random.normal(scale=0.3, size=100)
    fig = px.scatter(
        x=x,
        y=y,
    )
    fig.add_scatter(
        x=x,
        y=np.sin(x),
        mode="lines",
    )
    fig.update_layout(showlegend=False)
    fig["data"][1]["line"]["width"] = 5  # this is magic
    graphJSON = fig.to_json()
    # note the change here - we are no longer rendering a template!
    return Response(graphJSON, mimetype="application/json")
```

And now we've reproduced the static plots above in Plotly, which means it's now
interactive!

_Note - there is no legend.. it seemed too hard to make when using Plotly
express and I just wanted a quick demo before the real plot._

<div id='sine_chart' class='chart'></div>
<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>

<script type='text/javascript'>
  $.getJSON('/sine_graph/').done(function(data) {
    var layout = {};
    data.config = {
      responsive: true,
      showTips: false,
    };
    Plotly.newPlot('sine_chart', data, layout)});
</script>

## Making an actual chart

Throughout Covid, Berlin has used a stoplight system in order to determine what
restrictions are in place, and their (non-interactive) dashboard can be seen
[here](https://data.lageso.de/lageso/corona/corona.html#corona-ampel). It always
frustrated me that I couldn't zoom into their graphs, and so I decided to
recreate it. Later, I found that they kind-of have an
[interactive version](https://data.lageso.de/lageso/corona/corona.html#zeitlicher-verlauf),
but it still wasn't what I wanted.

First was to find the data - it was in German so I had to do some googling
around, but eventually found the
[data source](https://www.berlin.de/lageso/gesundheit/infektionskrankheiten/corona/tabelle-indikatoren-gesamtuebersicht/).
Initially I downloaded the data myself, but to keep it updated, I automated the
download if the file was over a day old. That can be seen below, and note some
packages need to be imported.

```python
@app.route("/covid_graph/")
def covid_graph():  # TODO - look into doing plotting in javascript instead

    data_path = os.path.join("static/assets/data", "fallzahlen_und_indikatoren.csv")
    try:
        file_age = time.time() - os.path.getmtime(data_path)
    except:
        file_age = 90000

    if file_age > 86400:
        print("Downloading data")
        url = "https://www.berlin.de/lageso/_assets/gesundheit/publikationen/corona/fallzahlen_und_indikatoren.csv"
        response = requests.get(url)
        with open(data_path, "wb") as f:
            f.write(response.content)
    else:
        print(
            f"Data has already been recently downloaded {file_age/86400:.3f} days ago."
        )
```

I then do some extremely minor data wrangling,

```python
    data = pd.read_csv(data_path, sep=";", decimal=",")
    data["Datum"] = pd.to_datetime(data["Datum"], format="%d.%m.%Y")
```

and then generate the plot.

```python
    # import graph_objects from plotly package
    import plotly.graph_objects as go

    # import make_subplots function from plotly.subplots
    # to make grid of plots
    from plotly.subplots import make_subplots

    # use specs parameter in make_subplots function
    # to create secondary y-axis
    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # plot a scatter chart by specifying the x and y values
    # Use add_trace function to specify secondary_y axes.
    fig.add_trace(
        go.Scatter(
            x=data["Datum"], y=data["7-Tage-Inzidenz"], name="7 day incidence rate"
        ),
        secondary_y=False,
    )

    # Use add_trace function and specify secondary_y axes = True.
    fig.add_trace(
        go.Scatter(
            x=data["Datum"],
            y=data["7-Tage-Hosp-Inzidenz"],
            name="7 day hospital incidence rate",
        ),
        secondary_y=True,
    )

    # Adding title text to the figure and make over compare both lines
    fig.update_layout(title_text="Covid in Berlin", hovermode="x")

    # Naming x-axis
    fig.update_xaxes(title_text="Date")

    # Naming y-axes
    fig.update_yaxes(title_text="# of cases", secondary_y=False)
    fig.update_yaxes(title_text="# of hospitalizations ", secondary_y=True)
    fig.update_layout(
        legend=dict(orientation="h", yanchor="top", y=1.12, xanchor="left", x=0.01)
    )

    # graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    graphJSON = fig.to_json()
    return Response(graphJSON, mimetype="application/json")
```

Success - the end result is the chart below!

<div id='covid_chart' class='chart'></div>
<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>

<script type='text/javascript'>
  $.getJSON('/covid_graph/').done(function(data) {
    var layout = {};
    data.config = {
      responsive: true,
      showTips: false,
    };
    Plotly.newPlot('covid_chart', data, layout)});
</script>

Some notes - you can click on the legend to remove one (or both) of the lines.
You can also click and drag in the plot area to zoom into a subregion, and
double click to reset zoom.

[Source code](https://github.com/tcpekin/flask_site/tree/19bc882115424265e115c0358637774b21fa57b0)

## Conclusions and future areas for improvement and exploration

There is a lot to improve here, and a lot more that I want to try. In no
particular order:

-   Try Bokeh - maybe build a dashboard?
-   Implement callbacks - how can I let users make new charts from a larger set
    of data?
-   Save the case data in a database instead of a CSV file, and store
    incremental updates, so that if my download messes up, I don't lose all the
    data
-   Can I make a button to open the plot in a new tab, would this mean changing
    the `covid_graph` path to return a Plotly plot full screen rather than just
    the JSON? Or a button to expand the Plotly size? It's a little small right
    now (sounds like Javascript 💀).
-   Can I create a graph that updates much more quickly in response to data?
    Live-streamed data?
-   Refactor how charts are made - is it the best way to have a route and all
    the plotting code per chart? What if I have lots of charts? Seems like it
    would make `blog.py` much too crazy.

## Additional links

1. [Plotly documentation](https://plotly.com/python/)
2. [Plotly/Bokeh comparison](https://plotly.com/compare-dash-shiny-streamlit-bokeh/)
3. [Main guide I followed, pt. 1](https://towardsdatascience.com/web-visualization-with-plotly-and-flask-3660abf9c946)
4. [Main guide I followed, pt. 2](https://towardsdatascience.com/an-interactive-web-dashboard-with-plotly-and-flask-c365cdec5e3f) -
   this will be explored more in a another post.
5. [Berlin Covid data source](https://www.berlin.de/lageso/gesundheit/infektionskrankheiten/corona/tabelle-indikatoren-gesamtuebersicht/)
6. [p5.js - another visualization library I want to try out... but javascript 😭](https://p5js.org/)

[Part 6.1]({{ url_for('post', name='making_of_6_quick_note') }})
