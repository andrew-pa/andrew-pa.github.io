* History of the project so far
    - wanted to build an OS as a kid (lol)
        - mostly thought it was just the UI, Dad explained it was more Complicated than that
    - various early attempts didn't go very far
        - hard to debug compared to application programming
        - annoying backwards compatibility for x86
        - hard to know "where to go" ie what the plan was
        - hard to setup virtual machines suitable for testing
    - decided to finally "just do it" in December 2023(?) during winter break
        - didn't have anything else I was excited about doing at the time
        - Rust made it easier to write correct code, setup a working build environment, import dependencies
        - better grasp of what components were necessary
    - the `k` project: a monolith OS project
        - made a lot of progress
        - got a lot better at reading datasheets/hardware documentation
        - figured out how to debug things in QEMU with GDB, which is really cool
        - eventually things became too chaotic and it started to feel like it was time for a rewrite
            - used `async` Rust to handle in-kernel concurrency, but that made it very difficult to reason about concurrency questions when you've got hardware device concurrency (interrupts), concurrency between different CPUs, concurrency between threads *and* concurrency between kernel tasks, all overlapping
            - hard to switch my focus between components because if the monolith was broken, it was broken
    - gave up for a while and worked on other stuff
    - eventually a friend was chatting with me about doing OS dev and I decided to get back into it, but be more organized this time
    - the `Cavern` project: a microkernel/microservices OS project
        - switch to microkernel architecture
            - makes it easier to work on different pieces of the system even if some parts are broken
            - components become "finished" faster
            - creates a clear interface boundary for designs, maintainability, testing
            - easier to reason about concurrency
        - wrote spec first
            - seperate mechanism and policy as much as possible/"sans-io" philosophy AKA dependency injection where dependency=effect
              - the kernel provides mechanisms for user space to manage time/space
                - not a minimalist design: kernel should still make things easy for user space
            - concerned that message passing would be too slow but came up with some clever ideas:
                - can pass a message in one copy if you store messages in the receiver's address space directly
                - allow processes to define "DMA" regions so that a buffer in one process can be the source/destination of a kernel-orchestrated memcpy started by another process. Lets you implement things like `read()`/`write()` easily without passing data via messages. A monolith would have to do roughly the same thing anyways.
            - spec is definitely easier to change than code for an OS!
        - started working on building the kernel component, using code from `k` to speed things up where possible
* Overall design/requirements summary
* What has been done so far
  * We boot (on QEMU)
  * We manage memory, time, and interruptions
  * We have processes and threads
  * We have system calls 
  * IPC: message passing & transfers
* Where we go next
  * Driver infrastructure 
  * User space daemons (supervisor, resource broker, logging)
* Future vision
  * Device drivers
  * Containers
  * Linux system call compatibility layer
