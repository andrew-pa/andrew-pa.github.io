---
title: "Cavern Progress Report #1"
pub_date: "2025-03-11T12:00:00-08:00"
tags: ["programming", "os-dev", "Cavern", "Rust"]
summary: "Like digging a tunnel for fun, building an OS for fun is mostly a lot of hard work."
---
I've always wanted to write an operating system since I was a kid.
Now that've gotten a little older, I've been able to fulfill that dream.
Of course, I've also gained a lot more understanding of what that actually means.
Recently I've been working on a new operating system project called [Cavern](https://github.com/andrew-pa/cavern), and I'm really excited about the progress that I've made so far.
Cavern is a microkernel-inspired operating system written in Rust, targeting the ARM64 (Aarch64) ISA.
My goal is to build a hobby OS platform where I can experiment with building various operating system components easily, and one where a majority of the effort can last for a long time even if some components come and go.
The name "Cavern" is inspired by hobby tunneling, something I have occasionally fantasised about doing, although it seems risky enough to keep me from attempting it.
Like digging a tunnel for fun, building an OS for fun is a lot of largely unrecognized hard work that few can really understand or even comprehend.
But, it is fulfilling in its own way!
Learning about operating system internals and the practical experience of actually implementing one is helpful in building your world model about how systems work.
It is great practice for thinking at multiple levels of abstraction at the same time, which I belive to be a core skill of computer science.
In this post, I'm going to talk about the history of how the Cavern project got started, some of my thoughts on the design, how implementation has been going so far, and what plans I have for the future.

# History
The Cavern project got its start after I had taken about a six-month break from my [previous OS project named `k`](https://github.com/andrew-pa/k).
I had become disillusioned with the monolith design and the heaps of spaghetti it had created, seasoned with an unhealthy dose of Rust `async` complexity.[^1]
At some point, one of my friends was telling me that they were starting an OS project, which got me thinking about it again.
This caused me to write a [document](https://github.com/andrew-pa/cavern/blob/main/spec/README.md), maybe a manifesto of sorts, that explained how things would be different this time.
I was heavily inspired by the sans-IO philosophy, and particularly [this blog post about it](https://www.firezone.dev/blog/sans-io), which introduced the policy/mechanism distinction.
This document eventually led to some rudimentary design specifications, which my friend helped revise.
I was starting to feel a lot more optimistic about the project, so I started an implementation, which I have been working on for the last year or so, on and off.

[^1]: Don't get me wrong I love Rust, but I frequently find myself wishing it had been created just a few years later so that it could have a proper composible [effects system](https://en.wikipedia.org/wiki/Effect_system). Perhaps one day, if we are lucky.

# Design
The Cavern design is a microservices/microkernel design, but aims to be at least somewhat more pragmatic than some academic implementations (not that these are bad, but they are rarely very performant).
The design aims to be hackable, maintainable, robust, extensible and performant, in roughly that order.
Additionally, composible, testable components are favored, ideally keeping "policy" and "mechanism" code separate.
Overall, I'm hoping that this is the "last" OS project, in the sense that I can use Cavern as a springboard to explore lots of systems/low-level programming projects like device drivers, file systems, etc.
I'll touch on these briefly, though more detailed explainations can be found in the specification.

One of the most important requirements I aim to meet with the design is what I call "hackability", a kind of maintainability where the system retains its fun, extensible nature over time.
This means things like having good documentation, extensive testing, making debugging easy, and aiming for more composible components.
The goal of having a hackable system is really to make sure that continuing to work on this as a fun side project stays fun as time wears on, and to make taking breaking possible without losing too much precious mental context.
Since it is a big project, both time spent total and the number of breaks taken are expected to be pretty big, so hackability is very important.

Another important goal for the design was to separate "policy" and "mechanism" code as much as possible, while still being performant.
The idea is that policy code represents what needs to be done to respond to an input, where as the mechanism code is the part that actually performs the effects of a policy.
This is similar to the idea of pure and impure/effectful code.
The benefit of doing this is that it makes the system remarkably more testable, and also makes it a lot easier to reason about what components are doing abstractly (i.e. you can assume the mechanism works correctly and just reason in terms of its effects as directed by policy.)
At a high level, you can look at the user space as "policy" and the kernel itself as the "mechanism" that actually implements various necessary effects as directed by user space.

The Cavern kernel is tasked with managing the basics of space (memory managment) and time (process/thread scheduling) in the system.
It also provides an inter-process communication (IPC) mechanism via message passing augmented with opaque shared memory buffers.
Messages are sent asynchronously via system calls, and can also include shared buffers as an attachment.
I was not originally sold on message passing, but it is a nice way to separate system components in a unified way, and can be made efficient (Cavern only requires one copy to get a message from the sender to the receiver, for instance).
A shared buffer is a way to name a region of memory in a sending process so that a receiver process can copy bytes to and from that region via system calls without the overhead of a message.
This was inspired by the idea of a "DMA transfer" between hardware devices and the main system memory.
These mechanisms should enable a rich ecosystem of user space policies.

Actually having a design process (with writing!) was something of a first for me for a hobby project, but I think was a big improvement.
It really is a lot easier to change the language in a design document than rework an implementation!
This hackable, well-organized design will hopefully allow Cavern to grow into a nice platform for further experimentation.

# Implementation
I started working on building the kernel component after finishing the specification.
For the most part, that has gone remarkably smoothly, and of course the experience and code from the `k` project has been a big help.
As a rough measure, the Cavern repository currently has 12,000 lines of code right now, including the ~800 lines of specifications.
This is fairly sizable, but the more organized design has made it feel a lot more managable.
I anticipate that the kernel will probably end up getting just a bit bigger.

AGI has been a huge help in building the kernel (mostly ChatGPT o1 and o3), especially for writing unit tests and creating implementations of "textbook" algorithms and data structures.
Writing unit tests is pretty magical, I'm not very enthusiastic about writing tests even though I think they're important because they tend to be very repetitive.
However, GPT has no problem cranking out tests against an interface as long as you give it enough context, and then you can massively boost your confidence that the implementation is correct with little effort.
Another thing GPT is really good at is implementing data structures that are well known, like allocators or collections.
Doing these by hand tends to be something of a chore, and the process is largely uninteresting.
However, it can be difficult to reuse some of these components because their implementation is heavily dependent on their environment, so using GPT to specialize them into your specific codebase from their platonic ideal is a huge speed boost.
Obviously these implementations can be hard to verify, but if you also have GPT generate a unit test suite (in an independent context), then you can usually be pretty sure that they're right.
GPT is not very good yet at building the more cross-cutting components in the system, it is hard to give it sufficent context and instructions to get something nice, and I usually feel like in the time/language I would use to explain it to GPT, I could code it myself just as well.
Some ideas are just most quickly expressed in code.

Another thing I am really happy about is the existence of unit tests in the system.
There are currently 772 unit tests[^2], and they all run independent of the actual kernel or target system which makes them a lot easier to integrate into the development process.
Having tests often exposes hard to find bugs in core algorithms early, so that they don't crop up when you're debugging something different, which is really nice.
One place this has really come in handy is the page table implementation.
Getting the various algorithms that manipulate page tables correct can be tricky, due to their low level and somewhat awkward layout.
Nothing is worse than trying to debug something else and finally discovering that its because a page mapping happened incorrectly (which happened more than once in `k`), so using unit tests to really make sure this part of the system was correct has helped a lot.
There is still a lot of code that doesn't have test coverage, which would be a good thing to improve in the future.
But just having tests in what is typically a constrained environment w.r.t. tooling/testing is fantastic.

[^2]: Many of these are instances of a single parameterized test. I am a huge fan of parameterized testing, it makes tests much less redundent and makes getting wide coverage of the space of possible behaviors so much easier!

One constant struggle between implementation and the design is that at the kernel level, a lot of "effects" end up looking like a pointer write.
This leads to tension between seperating out these effects as a mechanism behind an interface and just letting what is otherwise "policy" code write directly memory.
It would be exceptionally slow to batch up or request all of your memory writes one at a time, and make the code rather cumbersome, so a balanced approach had to be taken.
I did abstract memory writes when a system call needs to access user space memory as a mechanism.
This made centralizing the mapping check code much easier, and also made it possible to unit test system call handlers without too many hacks.
However in most places policy "takes for granted" writing to a pointer as an effect, which could be a place for future improvement as I think this is a bit sloppy.

The kernel component is now "finished", except for features required for driver services like handling interrupts from user space and mapping arbitrary ranges of memory, and support for devices other than QEMU's `virt` board.[^3]
A lot of the algorithms/data structures (scheduler, allocators) in the kernel are not performance-optimal yet, but it was a tradeoff for faster development time.
I anticipate returning at some point to these and replacing these draft components with more efficient versions as it becomes important.
I have now shifted my focus to building the necessary system services in user space.

[^3]: I've been meaning to get things running on Raspberry Pi for a while as it should be pretty straightforward, but I have been waiting until there's at least something interesting to interact with in user space first, since debug cycles are a lot shorter with QEMU.

# Future Plans
The next step is constructing user space while I finish various kernel features "on-demand".
I've been working on at least small specifications for the various necessary user space components like logging, process supervision and service/resource discovery ([in this PR](https://github.com/andrew-pa/cavern/pull/32)).
These system components are pretty integral to every other service, so once they are complete, Cavern is really going to start to feel like a real system.
There is something of a tricky chicken-and-egg situation going on where each of these services depends on the others in some way, so I'm planning on introducing another "egg" service that starts as the first process and provides some minimal services just to get things started.
These will be like reading from the initial RAM disk and spawning/monitoring the root supervisor and resource discovery services, and spawning driver processes for devices discovered via the Device Tree Blob.

After these core system services, it's mostly a matter of implementing the various device drivers and system services that I find interesting.
I'm particularly interested in building a rudimentary network stack[^4], which is of course its own huge project although I could see reusing an existing Rust TCP/IP implementation.
Once you have networking you can really start doing interesting stuff like load testing or running basic but real-world services, and that's pretty exciting!
Another thing I'm interested in doing is building a user space Linux system call shim, ideally in such a way that you could run OCI containers within a Cavern user space mostly transparently.
This is also a huge project (although ChatGPT claims there are only ~40 different required system calls to get 80% compatibilty), but of course it also massively increases the utility of the system.

[^4]: [tragically relevant OSDev Wiki humor](https://wiki.osdev.org/What_Order_Should_I_Make_Things_In%3F#Nick_Stacky)

# Conclusion
Building Cavern has already been an incredibly rewarding journey.
There's a particular satisfaction in crafting an operating system: like slowly carving out a tunnel by hand, you uncover new insights and hidden surprises at every turn.
Each new component not only brings the system closer to life but also deepens your understanding of foundations of computing.

Looking ahead, I'm excited about the possibilities Cavern holds as a sandbox where operating systems ideas can freely evolve, grow, and even fail productively.
The pragmatic yet principled design is something I'm proud of, and I'm eager to see where it leads next.
The microkernel approach, with its clean separation of policy and mechanism, continues to offer me clarity of thought and implementation efficiency, which was exactly what I hoped for when embarking on this project.
I'll continue documenting the progress and insights as I delve deeper into user space components, drivers, networking, and beyond.
