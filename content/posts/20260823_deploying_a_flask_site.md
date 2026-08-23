---
title: AI site refactor
date: 2026-08-23
description: A tale of Oracle limits, AI, and nginx. 
tags: [flask, docker, nginx, deployment, python, oracle]
---

On Friday I got the dreaded UptimeRobot email: your site is down. Turns out when you ignore the Oracle Always Free limits changing email, they will shut down your ~~shit~~ site. I decided that I didn't like the structure of my site, and also wanted to try code development using AI, this was as good of a chance as any to learn.

This is mostly here so that I remember what happened... but I don't think it's well written enough to actually help.

## A small refactor that changed the app structure
### AI summary

The original app lived in a big file, and over time it grew into something harder to manage. I moved it into a package structure under `app/`, with separate modules for:

- app creation
- configuration
- extensions
- routes
- services

That gave a much cleaner flow:

- the app factory creates the Flask instance
- routes are registered in one place
- data and plotting logic live in service modules
- the site is easier to extend without everything living in one file

This was a nice improvement in itself, but it also revealed a more important lesson: the server environment has to match the project structure exactly.

### My summary
I started with Gemini and uploading code files but I didn't like the back and forth, the loop really sucked with copying and pasting. So I just opened VSCode and used whatever default model they had and essentially asked it to refactor my code to whatever is better.

This worked pretty well and I think it does have a better separation, but I understand it less. Since I only update the code like yearly, I think that is ok.


## The real production problem was not only Flask
### AI summary
When I deployed the site, the web container kept failing with import errors. At first, the obvious suspect was Python path configuration. But after checking the environment more carefully, it became clear that the deeper issue was that the refactored `app/` directory was not actually on the VM in the repository state that was being deployed.

So the runtime was trying to import a package that simply did not exist in the deployed source tree.

This is the kind of problem that is easy to miss because everything can look fine from the local machine. You can have a working Flask app locally, a valid Docker setup, and still end up with a broken deployed container if the files you expect to be there are not actually in the server copy.

In short:

- the code was refactored locally
- the repo state on the VM was incomplete
- the app package was missing
- the container crashed during import

Once the correct files were committed and pushed, pulled to the server, and the image was rebuilt, the app started working again.

### My summary
Tom is dumb and didn't `git add` the new folder structure before moving it to the VM.

I also had to sign up for a paid Oracle account now that the limits are lower. You just can't get a VM allocated without a paid account now, even though I remain in the free limits. 

## Docker and nginx: the final layer of the puzzle
### AI summary

The next challenge was the reverse proxy setup. The site runs behind nginx, and nginx sits in front of the Flask application. That means the app itself must work, and the proxy must also be configured to forward traffic correctly.

The main things that matter here are:

- nginx needs to talk to the correct Docker service name, not localhost
- the certificate paths must be valid
- the ACME challenge path must work for certbot
- stale certificate files can cause a lot of confusion

A typical working setup looked like this conceptually:

- client -> nginx -> web container (Gunicorn/Flask)

The important detail is that inside Docker Compose, the app is usually reached by service name, such as `web`, not by a local port on the host machine. That is why `proxy_pass http://web:8000;` is the correct pattern in many setups.

## Why certbot and nginx caused so much trouble

Once the app was healthy, the next issue was HTTPS. The certificate setup is easy to get wrong if the folders are stale or the challenge path is not served properly.

In practice, the fix was to clear out old Let’s Encrypt state, recreate the cert files, and then restart the stack. The sequence looked roughly like this:

- stop the stack
- remove stale certificate and renewal data
- regenerate the Diffie-Hellman parameters if needed
- rerun the certificate bootstrap
- rebuild/recreate the containers
- verify the challenge endpoint and the HTTPS site

This was a good reminder that a deployment is a stack, not a single service. Even when the Flask app is correct, the surrounding TLS and proxy setup still has to be healthy.

### My summary
I still hate/do not understand nginx. It seems like caddy might be a good replacement, and it might be my next AI-driven improvement.

## Conclusion
AI "successfully" refactored my website, tbd if it is an improvement. It was a lot easier than doing it myself. Still, my own idiocy got in the way of a smooth experience.