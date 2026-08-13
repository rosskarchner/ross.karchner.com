---
title: "More Zummoning"
date: 2024-04-19T19:24:02-04:00
slug: "more-zummoning"
tags:
  - "Ludum Dare 55"
source_url: "https://rossk.micro.blog/2024/04/19/more-zummoning.html"
---

I'm cleaning up "The Zummoning" for submission to Godot Wild Jam this weekend (The GWJ folks usually disallow games submitted to other jams, but make exceptions sometimes when schedules completely overlap, which was the case with Ludum Dare this month).

Tonight, I hope to improve the card-combining systems and remove some of the annoying gaps.

If I get more time before the deadline (Sunday night), I hope to add some UI improvements (primarily, make it less mysterious what the cards do, alone and in combination). I'd also like to make it clearer what's actually happening during the combat phase.


<img src="/uploads/2024/4f562889b9.png" width="600" height="335" alt="">

As the screenshot shows, I've at least added a background image and improved the layout, since the LD submissions. Not obvious from the screenshot, the color of the spooky forest background gradually shifts between a handful of hues. It's stupid simple, but I find the effect really pleasing. The (gdscript) code is just:

```gdscript
func next_color():
	var colors = [
		Color.DARK_RED,
	 	Color.DARK_GREEN, 
		Color.DARK_BLUE, 
		Color.DARK_ORANGE, 
		Color.DARK_OLIVE_GREEN, 
		Color.DARK_MAGENTA]
	var tween = get_tree().create_tween()
	tween.tween_property($SpookyForest,"modulate", colors.pick_random(),15)
```

The `next_color` function is connected to a timer that fires every 15 seconds.
