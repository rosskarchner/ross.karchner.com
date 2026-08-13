---
title: "Troubleshooting before coffee"
date: 2023-11-22T08:01:08-04:00
slug: "troubleshooting-before-coffee"
source_url: "https://rossk.micro.blog/2023/11/22/troubleshooting-before-coffee.html"
---

I spent at least 30  minutes trying to figure out why the score in my game wasn't updating past the first point. It would go from 0 to 1, but then stayed at 1. I had a setter on the score variable, to update the score label shown to the user whenever the score changed.

It turned out, my setter wasn't actually *setting*, so to score was always zero, and the incoming new score was always 1.

The missing line in the "set" code below is `SCORE=new_score`

<img src="/uploads/2023/screenshot-from-2023-11-22-06-55-15.png" width="531" height="86" alt="some gdscript code that sets a text label when a variable is changed (but neglects to actually store the new value)">
