# harmonyparser

A project file parser for Toon Boom Harmony

Tested on Harmony 21.

## What is it for?

Harmony xstage files are just huge XML files that you can easily read using a conventional approach.
This parser attempts to organize the structure of the project with an object-oriented approach.  

It currently supports:
* Columns discovery ([Harmony documentation](https://docs.toonboom.com/help/harmony-21/premium/layers/about-layer-column.html))
* Elements discovery ([Harmony documentation](https://docs.toonboom.com/help/harmony-21/premium/reference/node/generator/element-node.html))
* Graph traversal

## Basic Usage

```python
import harmonyparser

# Loading the scene project 
scene = harmonyparser.parse("/path/to/harmonyproject.xstage")

# Get scene information
scene_id = scene.id
start_frame = scene.start_frame
end_frame = scene.end_frame

# Get the elements (i.e. resources) used in the scene
elements = list(scene.iter_elements())

# Get the columns of the scene (i.e. use of elements)
columns = list(scene.iter_columns())

# Get the graph of the scene
graph = scene.get_graph()

# which can be traversed
for node in graph.iter_children(recursive=True):
    node_type = node.type
    node_path = node.get_path()

# Every object of the parser keep a reference to the xml node it is referring to
# You can use it to access data that is not exposed by the parser
harmony_version = scene.xml_node.attrib["version"]
```

