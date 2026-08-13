---
microblog: true
date: 2024-10-31T21:05:42-04:00
slug: "not-much-obvious"
tags:
  - "SpinDoc"
source_url: "https://rossk.micro.blog/2024/10/31/not-much-obvious.html"
---

Not much obvious has changed since my last post about SpinDoc-- I did rework a lot of how the wands work behind the scenes. I had been rotating the wand with code, but now it's a [RigidBody2d](https://docs.godotengine.org/en/stable/classes/class_rigidbody2d.html), with rotation being handled by the physics engine.
<video src="/uploads/2024/screencast-from-2024-10-31-21-02-19.mp4" controls="controls" preload="metadata"></video>
