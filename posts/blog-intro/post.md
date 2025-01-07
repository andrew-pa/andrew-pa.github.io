---
title: "Beginning to Blog"
pub_date: "2025-01-07T12:00:00-08:00"
tags: ["meta"]
summary: "Why I’m starting a blog and how I'm rendering it with an AI-generated static site generator."
---
I've had the idea to start a blog in the past a few times, but so far I haven't followed through, mostly because writing is hard and I don't usually get past the hurdle of setting up the website due to bike-shedding. In 2025 one of my goals is to become more publicly visible, and I think blogging is a good way to do that. Also, generative AI has made doing blogging a million times easier than previously, between getting it setup and doing the proofreading, generative AI makes becoming a blog writer a lot more tenable.

I've been an avid blog reader now for a while. In my opinion the best blog posts are the ones that tell a compelling story, even if they are technical. I hope that this blog  helps my personal projects become more legible for others as I tell the story of building them. Personal programming projects are tricky because the code never tells the full story of how and why they came about. I'm hoping that this blog will help make my efforts and ideas more human-readable, and hopefully also somewhat interesting/entertaining. I also hope that blogging helps me organize and record my own ideas, which I am finding increasingly important as the depth/scope of my projects grows and as I have more ideas that feel worthwhile to keep around.

## Building A Blog

Of course, being a software engineer, I am initially mostly concerned about the software necessary to publish. There are really only a few essential features for me: Markdown rendering, RSS feed generation, tags, and supporting analytics. Also, having good aesthetic taste, preferably a minimal, modern looking one, is really important.

I've looked into a couple of static site generators before (Hugo, Jekyll) and while they seem great and have many happy users, I've always found them somewhat lacking. My biggest problems with them is that they are too opaque and fail to consistently support the features I find important. It is crazy to have different themes support different features that I would consider essential. Also, creating your own theme for these systems is a huge chore from what I could tell, and it can be hard to predict how changing the input parameters will affect the outputs. I'm sure if I invested more time in reading the documentation I'd eventually get it right, but it uses up time that could just as well be spent doing something more interesting.

Fortunately now days we can just use AI to write a static site generator with effectively zero effort, so that's what I did!

### Generating a Static Site Generator

First, I wrote up a rough list of requirements for the generator:

- Turn markdown with front matter into blog posts
- Blog post has title, pub date, body text, tags
- Home page, archive/list view, list per tag
- Blog posts can also have pictures and other embeds which should be stored next to each post.
- Posts should be nicely organized on disk
- Posts should be converted into static HTML suitable for GitHub Pages
- Posts should have correct OpenGraph tags for nice link previews as well
- RSS feed should be generated
- Social links for quick sharing
- Page analytics (using a 3rd party)
- Navigation bar
- Use HTML templating for pages that are not blog content
- Centralized CSS for whole site
- Copy/optimize public assets (favicons, etc) into output directory as well
- The generator should be able to run in GitHub Actions

Then I gave this list of requirements to ChatGPT 4o and asked it to write a specification.
This specification was mostly unremarkable but did concertized some of the finer details that I didn't really care about like the exact directory structure.
I then took the specification and gave it to ChatGPT o1 and asked it for a complete implementation using Python.

The initial o1 implementation was entirely functional out of the box, which I still find quite incredible.
Seeing the initial implementation caused me to realize that there were still a few things missing, and o1 did not write any CSS (which I wanted because CSS is very easy and I'd need to tweak it to get it just right anyways).

The two big changes were:

- Changing the in-repository directory structure for posts from `/<year>/<month>/<post slug>/` only using the post slug.
  The year/month organization seemed redundant and would possibly mean moving a post after writing it, which is unnecessary. I should have caught this in the specification phase but it was easy to have the AI fix it. This also ensures that the publication date has a single source of truth from the post metadata.
- Showing the set of tags on the home page so people can directly jump to a list of related posts.

After those changes and some CSS, the generator was pretty much ready to go.
Integrating with GitHub Actions/Pages was remarkably smooth, which was refreshing.
You can check out the (current) source code [here](https://github.com/andrew-pa/andrew-pa.github.io/blob/main/generate.py).

## Conclusion

I think that this mostly AI-generated static site generator turned out pretty well, considering the effort required. In the future, there will probably be more features and fixes, especially if/when the number of posts/tags grows large enough to warrant optimization. But for now, it works pretty well. I think that this application of AI is pretty exciting, being able to generate software that fits your exact requirements is really nifty and makes computers a lot more fun to use. I have found myself creating a lot more software to fit specific needs since the cost is so low, which has made a lot of one-off workflows a lot less burdensome. Some of these may become future posts!
