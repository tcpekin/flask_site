---
title: The making of this blog, part \# - Logging/analytics V2
date: 2022-10-11
description: Analytics is better than a textfile
tags: [python, web, making_of, flask, gunicorn, docker, nginx, cloud, analytics]
---
this is a test

here comes a graph



<div id='chart' class='chart js-plotly-plot'></div>
<script src='https://cdn.plot.ly/plotly-latest.min.js'></script>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.6.0/jquery.min.js"></script>

<script type='text/javascript'>
  var graphs = $.getJSON('/graph/');
  graphs.done(function(data) {Plotly.newPlot('chart',data,{})})
</script>

no more graph

