---
title: The making of this blog, part 5 - Registering a domain
date: 2022-10-17
description: Setting up tcpekin.com
tags: [python, web, making_of, flask, domain]
---

[Part 4]({{ url_for('post', name='making_of_4') }})

The next part was paradoxically not so hard. I did a lot of ~~research~~
googling about to figure out who the best domain registrar was, and the
recommendations came down to
[Cloudflare](https://www.cloudflare.com/products/registrar/),
[NameCheap](https://www.namecheap.com/) and [Porkbun](https://porkbun.com/). In
the end I went with Porkbun because their site/copy seemed friendly and nice,
and when trying to register for a Cloudflare account, I couldn't verify my email
as they didn't send the necessary email for 40 minutes. 🤷‍♂️ Porkbun had a lot of
positive reviews on [HN](http://news.ycombinator.com) (my guilty pleasure), and
for the whopping sum of $9.73, [tcpekin.com](http://tcpekin.com) was mine. Now
all there was to do is connect domain to instance, how hard could it be?

## Connecting Oracle instances with my domain

WTF. "How does the internet even function" and "Does anyone even know what
they're doing on the web" were two questions that ran through my head when I
started looking up how to connect domain and IP address. First, I looked into
Oracle's documentation; they have
[this](https://blogs.oracle.com/cloud-infrastructure/post/bring-your-domain-name-to-oracle-cloud-infrastructures-edge-services)
blog post illustrating how to connect an instance to a DNS. I know next to
nothing about the cloud, and find the Oracle interface confusing as it is
already, so the blog post was in the end, practically no help to me. It doesn't
help that the screenshots occasionally have different versions of the interface
than what they currently look like... It only furthers my belief that in the
end, documentation is everything.

My next step was to look at Porkbun's documentation, and while clearer, it had a
lot of info on how to connect Etsy shops and such to a domain. Not exactly what
I was going for. However, I did find an article titled
[Transferring vs. pointing a domain at web hosting, which should I do?](https://kb.porkbun.com/article/172-transferring-vs-pointing-your-domain-at-web-hosting-which-should-i-do),
which seemed like it might lead me in the correct direction.

<figure>
<img async src="https://media3.giphy.com/media/SRx5tBBrTQOBi/giphy.gif?cid=ecf05e4768w2q7kua9gysiyboi0leyb8begs0vliwm0gxsbl&rid=giphy.gif" alt="floating dog gif">
<figcaption>Me doing internet stuff.</figcaption>
</figure>

After reading the article, I decided to point my domain at my instance, and
luckily Porkbun had
[this](https://kb.porkbun.com/article/54-how-to-use-a-records-to-point-your-domain-at-a-web-host)
helpful resource on how to use 'A records' to point at a third party host (in my
case Oracle). I followed the instructions, updated my A record (whatever that
is), waited about five minutes, and then to my astonishment, tcpekin.com was
live!

## Conclusion

in the end, this was actually simpler than I thought, at least to set up a HTTP
site. Why I wasn't able to figure out that I only needed to change one line of
configuration on my domain registrar's dashboard until after hours of googling,
I don't know. I blame my google-fu and also the complexity of the web. The more
I learn, the more some of it slowly makes sense, but at the same time, the more
I realize that at some point I'd rather make fun graphs or do science than
understand exactly what A records are or what CNAME is, or what namespace
servers do. Eventually I do want to know what they all do, but I have to go
slowly in order to not be overwhelmed and just give up. Anyways, it was a huge
success to be able to go to tcpekin.com and see something!

Next up - better analytics, HTTP**S** (so far extremely stupidly hard with
`nginx`, Docker, and Flask 🤦‍♂️), and interactive plots using
[Plotly](https://plotly.com/) (which I think might require a redesign of how I
serve blog pages ☹️). I guess that means I might learn some database skills,
whether I want to or not.
