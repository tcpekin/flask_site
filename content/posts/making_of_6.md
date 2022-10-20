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

One of the goals I had for this site when starting was the ability to have
interactive plots. Making a beautiful figure is nice, but it is so much more fun
when you can zoom, have floating tooltips, and take advantage of the fact that
you're on a computer, not staring at a piece of printed paper.

## Plotting library comparison - why Plotly?

## Integrating Plotly into my site's architecture

### Flatpages (markdown) + JavaScript + jQuery 😥

### Other required changes

## Making of the plot

<div id='chart' class='chart'></div>
<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>

<script type='text/javascript'>
  var graphs = $.getJSON('/covid_graph/');
  graphs.done(function(data) {
    var layout = {};
    data.config = {
      responsive: true,
      showTips: false,
    };
    Plotly.newPlot('chart', data, layout)});
</script>

no more graph

## Conclusions and future areas for improvement/exploration

## Links

1. [Plotly documentation](https://plotly.com/python/)
2. [Main guide I followed, pt. 1](https://towardsdatascience.com/web-visualization-with-plotly-and-flask-3660abf9c946)
3. [Main guide I followed, pt. 2](https://towardsdatascience.com/an-interactive-web-dashboard-with-plotly-and-flask-c365cdec5e3f) -
   this will be explored more in a second post.
4. [Berlin Covid data source](https://www.berlin.de/lageso/gesundheit/infektionskrankheiten/corona/tabelle-indikatoren-gesamtuebersicht/)
5. [p5.js - another visualization library I want to try out... but javascript 😭](https://p5js.org/)
