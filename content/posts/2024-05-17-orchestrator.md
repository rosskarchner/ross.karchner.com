---
title: "Orchestrator"
date: 2024-05-17T17:07:53-04:00
slug: "orchestrator"
source_url: "https://rossk.micro.blog/2024/05/17/orchestrator.html"
---

I spent some time last night and this morning learning about [Orchestrator](https://orchestrator.vahera.com), a visual scripting plugin for Godot.  I was mostly taking a look to see if my son might want to try it out, as an alternative to "regular" coding. He knows Scratch pretty well, but hasn't taken to written coding yet. I thought Orchestrator might offer him a way to make stuff happen in Godot, using a style of programming he's used to.

At first, I was amused and appalled that in an example, this short line of gdscript:

```gdscript
rotation += angular_speed * delta
```

... equated to [a six-node graph](https://docs.vahera.com/orchestrator/img/step-by-step/apply-rotation.png). After completing the [step by step](https://docs.vahera.com/orchestrator/getting-started/step-by-step/) tutorial, I appreciated it more.  

I'm missing the words for describing this coherently, but, to me, it encourages a different way of thinking about the functions you write.  Instead of the step-wise, imperative march from input (or not) to return value (or not), you kind of need to start at the end, with the impact you want to cause, and *then* work out the information and logic needed to inform that action.

I haven't spent much time studying (let alone doing) functional programming, but... is that what functional programming is like?

I'm not sure I'll reach for Orchestrator  in my own projects, and I'm not sure the kiddo will either. I did show him the results I was able to get it, and if he wants to learn more I'll certainly work with him.  I was wrong to assume that it's anything like Scratch, and I don't think it really improves on gdscript in terms of reducing the cognitive work involved in programming. Orchestrator doesn't simplify Godot.
