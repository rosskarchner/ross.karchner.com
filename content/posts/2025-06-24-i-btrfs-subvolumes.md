---
title: "I ♥️ BTRFS Subvolumes"
date: 2025-06-24T17:30:00-04:00
slug: "i-btrfs-subvolumes"
source_url: "https://rossk.micro.blog/2025/06/24/i-btrfs-subvolumes.html"
---

I've been mucking around with my operating system setup for reasons too tedious to describe here. _One_ hilarious bit of hijinx involved trying to use [the Nobara repository](https://copr.fedorainfracloud.org/coprs/gloriouseggroll/nobara-42/) exactly in the way it says **not** to...

> It is NOT recommended to try to upgrade your Fedora installation to Nobara and support for doing so will not be provided.

Turns out, there are _reasons_.

But, the point of this post is actually a nice thing I discovered:

- When you install fedora, by default your `/home/` directory is placed on a [BTRFS subvolume](https://btrfs.readthedocs.io/en/latest/Subvolumes.html)
- If you ever need to install again, the Fedora installer recognizes the subvolume and can preserve it.

In the past, if you wanted to re-install a distro and preserve all of your files, you either needed the foresight to put `/home'` on it's own partition or device, or have backups. Now, it's no big deal.
