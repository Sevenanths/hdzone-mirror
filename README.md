# hdzone-mirror

This script mirrors any source from the Main Zone on your Pioneer receiver to the HD Zone. It turns the HD Zone on and off automatically depending on whether a source needs to be mirrored or not.

## How to use

First, install the single dependency using `pip install -r requirements.txt`.

Then, you activate the loop as follows (example):

`python hdzone-mirror.py 192.168.0.100 mirrored_sources.txt`

- The first argument is the **IP of the receiver** (you can find this by pressing the STATUS button)
- The second argument is the path to the **text file which contains the sources that need to be mirrored**.

Example file content:
```
Switch
Wii
Wii U
PlayStation 2
```

Each source should be a separate line. Make sure that the casing for each source is correct.

## Background

I use the HD Zone for sending my receiver's output to my capture card. To be able to keep the surround sound on the primary output and downmix the audio on the second output, I enabled HD Zone for the second output. HD Zone is fully separate from the Main Zone and has an independent input switcher. I don't care for this feature; I just need it to mirror my main sources. I wrote this application to automatically turn on and off the HD Zone, and mirror the main source if necessary. I think the code could be improved, but it works well enough for my purposes right now.

Tested and implemented for Pioneer VSX-930.