![](media/crowbar/crowbar-flat.svg)
# well-intentioned crowbar
The **well-intentioned crowbar** is a desktop task automation tool with an intuitive visual boxes-and-arrows workflow interface.

This document explains some of the things that might happen to the project in the future.

## Roadmap

### [0.0.1]

- Teach myself PyQt skills.
- The app can get up and running.

### [0.0.2]

- Doesn't alter your computer.
- UI is more or less complete; shows intent.
  - Flowchart canvas pane is working visually, but not connected to any back end.
  - File manager pane can list files; flows can be saved and loaded.

### [0.0.3]

- Doesn't alter your computer.
- Flows can be 'executed'; flow progression is visualized, but still no actual system integration.

### [0.0.4]

- Start system integration; be sufficiently cautious to be confidently harmless.
- Triggers:
  - Time: simple recurrence
  - Network:
    - dis/connect
    - wifi hotspot list changed (does not imply an actual connection to any network)
  - File or directory changed

### [0.1.0]

- Can alter your computer!
- At least one simple flow can exist and run automatically.

### [0.2.0]

- User can create some reasonable amount of scripting for Operation components.

### The heap

Current sticky-notes on the white-board; highly unorganized yet vaguely descending in priority:

- Add logging for debugging etc.
- Decide and adhere to public|private variable|method NAMING: snake_case or camelCase?
- Create a dummy folder/flow data structure, and play with the left pane
- Make resources work like they do in Designer
- Component titles should be centered (needs using text instead of static text?)
- Moving a Component must also cause all attached wires to adjust
- Deleting a Component must delete all attached Wires.
- External links in README should point to archive.org
- Figure out how to reasonably test UI operations such as autowiring
- Give arrows rounded corners. Nice to have, but also helps discerning routing when wires visually overlap.

#### Layers

I wanted to ensure that connector lines are drawn behind boxes, but I think the Qt layer model involves only "foreground" and "background", plus a z-axis that seems to be not well integrated into graphic items. So I tried just putting all the boxes into one group, and all the connectors into another -- but that screws up the ability to grab-and-drag the boxes around on the canvas. Bummer. So the groups went away again (leaving just the one for the background grid).

#### MISC. NOTES

('cuz I'm still a Python newbie)

- https://www.bogotobogo.com/Qt/Qt5_QTreeWidget.php
- When moving a selection of several items, perhaps need to temporarily wrap them in a group.
