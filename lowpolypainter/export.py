# Python Modules
import svgwrite

# creates a svg graphic from a given mesh
def export(mesh):
    img = svgwrite.Drawing('test.svg')
    for x in range(0,len(mesh.faces)):
        # vertices for triangle
        points = [
                [mesh.vertices[mesh.faces[x].vertices[0]].x,
                 mesh.vertices[mesh.faces[x].vertices[0]].y],
                [mesh.vertices[mesh.faces[x].vertices[1]].x,
                 mesh.vertices[mesh.faces[x].vertices[1]].y],
                [mesh.vertices[mesh.faces[x].vertices[2]].x,
                 mesh.vertices[mesh.faces[x].vertices[2]].y]
                ]
        # color of the face, converted to decimal rgb values
        color = svgwrite.rgb(r=int(mesh.faces[x].color[1:3],16),
                             g=int(mesh.faces[x].color[3:5],16),
                             b=int(mesh.faces[x].color[5:7],16),
                             mode='RGB')
        # add triangle to image
        img.add(img.polygon(points=points, fill=color))
    # save image
    img.save()