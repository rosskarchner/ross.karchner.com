---
title: "Crossing the streams"
date: 2025-10-13T07:56:30-04:00
slug: "crossing-the-streams"
tags:
  - "AI, LLM, Agents, etc"
source_url: "https://rossk.micro.blog/2025/10/13/crossing-the-streams.html"
---

At work, I've been diving into AI/LLM stuff, and I'm still pretty much always using coding assistants when I work on DC Tech Events. I hadn't really attempted to bring that into game development, though. Last week, I decided to try it on my current roguelike project. 

This game began life as part of a 10-day game jam, and I was beginning to regret some of the architectural compromises I made under the time pressure. In particular, the lines of responsibility were pretty murky between the class that generated maps, and the one that displayed the map and tracked positions.  I gave Github Copilot some direction on what functionality belonged where, and it did a credible job cleaning things up, which made it easier for me to move on. Neat.

This led to some excitement and further experimentation, which resulted in *two* [MCP](https://modelcontextprotocol.io/) servers, which allow a coding assistant more visibility and control of a a running Godot project. [This one](https://github.com/rosskarchner/godot-mcp/) runs outside of Godot, and connects to the debugging port and language server, while [the other](https://github.com/rosskarchner/godot-mcp-plugin) is a Godot Plugin, and provides an HTTP server that allows for an agent to manipulate the node tree, and even send input. It's cool when it's all working.

As a "big swing" experiment, I created an empty project with [a single spritesheet](https://kenney.nl/assets/puzzle-pack), and asked copilot to make a match 3 game. The game itself turned out OK, but across many attempts it completely failed to identify which parts of the sheet should be used as game pieces. Score one for humanity!

I've started a lot of projects and finish basically none of them-- I think the promising thing for me is that I can use coding agents to get past the annoying/tedious tasks that cause me to lose interest and move on, and finish more games. For example, at one point I started "CISO Clicker", meant to be an idle/clicker game that hopefully imparts some wisdom about the asymmetric nature of cybersecurity. I never really got past [generating some company names](https://ross.karchner.com/2024/07/15/im-working-on.html).

With a few prompts, I've got a start on exactly the sort of simulation I've been thinking about:

<img src="/uploads/2025/screenshot-from-2025-10-13-00-15-29.png" alt="Auto-generated description: A retro-style computer game interface shows a cybersecurity simulation from 1995, featuring active threats and security measures with respective severities and costs.">
