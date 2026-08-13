---
title: "Godot Wild Jam  66 postmortem"
date: 2024-02-19T19:23:34-04:00
slug: "godot-wild-jam"
tags:
  - "Brakes Escape"
source_url: "https://rossk.micro.blog/2024/02/19/godot-wild-jam.html"
---

<img src="/uploads/2024/screenshot-from-2024-02-19-18-03-14.png" width="600" height="156" alt="">

Some lessons learned from my recent game jam experience:

- Don't wait until the very end of the jam to download the [export templates bundle](https://docs.godotengine.org/en/stable/tutorials/export/exporting_projects.html#export-templates) (see screenshot).
- The last few hours of the jam are NOT the right time to learn shaders
- The last few hours of the jam are NOT the right time to learn parallax backgrounds
 
 Godot features I attempted to re-create (poorly)

- Path2D (i was trying to move platforms back and forth by tracking points and managing velocity, before I figured out that Path2D could do this for me)
- One-way collisions (I had used an Area2D and code to manage what collision layers a platform is, to create the effect where you could jump through a platform from below, while it acts as if it's solid when you land on it. Turned out this was built in, and a matter of checking [one goddamned checkbox](https://docs.godotengine.org/en/stable/classes/class_collisionshape2d.html#class-collisionshape2d-property-one-way-collision).

 Godot features and nodes that I had never used before (besides Path2D/PathFollow2D and one-way collisions)

- ParallaxBackground and ParallaxLayer (though I messed this up somehow, my background that is supposed to repeat stops repeating at some point)
- The ability to place limits on camera movement, which I'd previously done myself via code.

The only add-on I used was [Godot State Charts](https://godotengine.org/asset-library/asset/1778), which continues to be the bees knees.
