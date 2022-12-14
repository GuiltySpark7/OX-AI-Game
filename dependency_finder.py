import os
import pydot
from IPython.display import Image, display


def dirFolderList(path):
    folders = []
    for item in os.listdir(path):
        if os.path.isdir(path + item):
            folders.append(path+item+'/')
    return folders

def folderTreeScan(path, depth=10):
    folderList = set(dirFolderList(path))
    previousLayerFolders = [folderList]
    while depth > 0:
        nextLayerFolders = []
        for folder in previousLayerFolders:
            nextLayerFolders.extend(dirFolderList(folder))
        previousLayerFolders = nextLayerFolders
        folderList.union(nextLayerFolders)
        depth -= 1
        if len(nextLayerFolders) < 1:
            depth = 0

    return folderList

a = set(['a', 'b'])
b = ['c', 'd', 'a', 'f']
a
a.union(b)
help(a)
path = '/home/doug/Documents/projects/OXgame/OX-AI-Game/'
folderTreeScan(path)
print(a)
dirFolderList(path)
path = dirFolderList(path)[0]
path
def removeTrippleQuotes(string):
    searching = True
    while searching:
        if string.find('"""') > -1:
            startOfTrippleQuote = string.find('"""')
            string = string.replace('"""', '   ', 1)
            endOfTrippleQuote = string.find('"""')
            string = string.replace(string[startOfTrippleQuote: endOfTrippleQuote + 3], '')
        else:
            searching = False
        searching = True
        while searching:
            if string.find("'''") > -1:
                startOfTrippleQuote = string.find("'''")
                string = string.replace("'''", '   ', 1)
                endOfTrippleQuote = string.find("'''")
                string = string.replace(string[startOfTrippleQuote: endOfTrippleQuote + 3], '')
            else:
                searching = False
    return string


def removeHashComments(string):
    string = string.splitlines()
    newString = []
    for line in string:
        hashLocation = line.find('#')
        if hashLocation > -1:
            line = line[0:hashLocation]
        newString.append(line)
    return '\n'.join(newString)


def removeCommentsAndSplitLines(fileTextBlock):
    fileTextBlock = removeTrippleQuotes(fileTextBlock)
    fileTextBlock = removeHashComments(fileTextBlock)
    fileText = fileTextBlock.splitlines()
    return fileTextBlock, fileText


def importDetection(fileTextBlock):
    fileTextblock, fileText = removeCommentsAndSplitLines(fileTextBlock)

    fileImports = {}

    lineNo = 0
    for line in fileText:
        splits = [',', '=', '+', '-', '*', '/', '(', '[', '{', ')', ']', '}']

        """ handle 'import' and 'import ... as'"""
        if line.startswith('import '):
            words = line.split()

            # identify imported module
            imported = words[1]
            if line.count(' as ') > 0:
                alias = words[3]
            else:
                alias = words[1]

            # check for module uses
            uses = set()
            for line2 in fileText:
                if line2.count(alias) > 0:
                    for split in splits:
                        line2 = line2.replace(split, ' ')
                    useCheck = line2.rsplit()
                    for word in useCheck:
                        if word.startswith(alias + '.'):
                            use = word[len(alias)+1:]
                            uses.add(use)
            fileImports[imported] = [*uses]

        if line.startswith('from '):
            words = line.split()
            imported = words[1]
            uses = set(words[3:])
            fileImports[imported] = [*uses]

        lineNo += 1
    return fileImports


def classDetection(fileTextBlock):
    fileTextblock, fileText = removeCommentsAndSplitLines(fileTextBlock)

    fileClasses = {}

    lineNo = 0
    for line in fileText:

        if line.startswith('class '):

            # identify the class text block
            classText = []
            for line2 in fileText[lineNo+1:]:
                if line2.startswith(' ') is False and len(line2.split()) > 0:
                    break
                else:
                    classText.append(line2)

            # identify the class functions
            classFunctions = []
            for line2 in classText:
                words = line2.split()
                if len(words) > 0:
                    if words[0] == 'def':
                        lineStart = line2.find('def')
                        classFunctions.append(line2[lineStart+4:-1])
            fileClasses[line[6:-1]] = classFunctions
        lineNo += 1
    return fileClasses


def functionDetection(fileTextBlock):
    fileTextblock, fileText = removeCommentsAndSplitLines(fileTextBlock)

    fileFunctions = []

    for line in fileText:
        if line.startswith('def '):
            fileFunctions.append(line[4:-1])

    return fileFunctions


def find_deps_in_folder(path):
    files = {}
    if isinstance(path, type('')):
        path = [path]

    for path in path:
        for file in os.listdir(path):
            if file.endswith('.py'):
                fileName = file[:-3]
                fileTextBlock = open(path+file).read()
                fileImports = importDetection(fileTextBlock)
                fileClasses = classDetection(fileTextBlock)
                fileFunctions = functionDetection(fileTextBlock)

                files[fileName] = {'imports': fileImports,
                                   'functions': fileFunctions,
                                   'classes': fileClasses}
    return files

def saveGraphImage(Graph, GraphName):
    with open(GraphName, "wb") as png:
        png.write(Graph.create_png())


# want node of intrest and detail level 1,2,3
def createPydotGraph(path=None,
                     plotExternals=True,
                     headLabels=False,
                     headDetLvl=1,
                     tailLabels=True,
                     tailDetLvl=1,
                     labels=True,
                     labelDetLvl=1):

    files = find_deps_in_folder(path)
    Graph = pydot.Dot(graph_type='digraph', compound='true', nodesep=0.5, ranksep=3, overlap='scale')

    colourList = ['aquamarine','brown1','chartreuse1','crimson','cornflowerblue','darkgoldenrod1','darkgreen','deeppink','firebrick2','gold2','greenyellow','indianred2']
    colourRange = len(colourList)

    libraries = set()
    for file in files:
        libraries.add(file)
        file = files[file]
        if plotExternals is True:
            for imports in file['imports']:
                libraries.add(imports)

    # Nodes
    color = 0
    nodeColours = {}
    for library in libraries:
        colourInd = color % colourRange
        nodeColours[library] = colourList[colourInd]
        label = library
        Graph.add_node(pydot.Node(library, label=label, fontsize=28, style='filled', color=colourList[colourInd]))
        color += 1

    # Nodes
    for library in files:
        classStr = []
        for fileClass in files[library]['classes']:
            newClass = []
            newClass.append('<FONT POINT-SIZE="10">'+fileClass+'</FONT>')
            for classFunc in files[library]['classes'][fileClass]:
                newClass.append('<FONT POINT-SIZE="10">  '+classFunc+'</FONT>')
            classStr.append('<BR ALIGN="LEFT"/>'.join(newClass))
        classStr = '<BR ALIGN="LEFT"/>'.join(classStr)
        funcStr = []
        for func in files[library]['functions']:
            funcStr.append('<FONT POINT-SIZE="10">'+func+'</FONT>')
        funcStr = '<BR ALIGN="LEFT"/>'.join(funcStr)

        label = '<{<FONT POINT-SIZE="28"><B>'+library+'</B></FONT>|{<FONT POINT-SIZE="15">Class</FONT><BR ALIGN="LEFT"/>'+classStr+'|<FONT POINT-SIZE="15">Func</FONT><BR ALIGN="LEFT"/>'+funcStr+'}}>'
        Graph.add_node(pydot.Node(library, shape='record', label=label, style='"rounded,filled"', color='black', fillcolor=nodeColours[library]))

    # Edges
    for fileName in files:
        file = files[fileName]
        for imported in file['imports'].keys():
            if imported in libraries:
                #label = '\l'.join(files[fileName]['imports'][imported])
                Edge = pydot.Edge(imported, fileName,
                                  labelfontcolor=nodeColours[fileName],
                                  labeldistance=10,
                                  decorate='true',
                                  fontsize=13,
                                  penwidth=4,
                                  color='"'+nodeColours[fileName]+';0.3:'+nodeColours[imported]+'"',
                                  fontcolor=nodeColours[imported])
                if labels is True:
                    if labelDetLvl == 1:
                        label = '<<B>' + imported + ' -- ' + fileName + '</B>>'
                    else:
                        label = ['<B>' + imported + ' -- ' + fileName + '</B>'] + files[fileName]['imports'][imported]
                        label = '<' + '<BR ALIGN="LEFT"/>'.join(label) + '>'
                    Edge.set('label', label)

                if headLabels is True:
                    if headDetLvl == 1:
                        headLabel = imported
                    else:
                        headLabel = ['<B>'+imported+'</B>'] + files[fileName]['imports'][imported]
                        headLabel = '<' + '<BR ALIGN="LEFT"/>'.join(headLabel) + '>'
                    Edge.set('headlabel', headLabel)

                if tailLabels is True:
                    if tailDetLvl == 1:
                        tailLabel = fileName
                    else:
                        tailLabel = ['<B>'+fileName+'</B>'] + files[fileName]['imports'][imported]
                        tailLabel = '<' + '<BR ALIGN="LEFT"/>'.join(tailLabel) + '>'
                    Edge.set('taillabel', tailLabel)

                Graph.add_edge(Edge)

    return Graph
dirFolderList(path)
path = '/home/doug/Documents/projects/acorn/acorn-precision-farming-rover/vehicle/'
path = '/home/doug/Documents/projects/OXgame/OX-AI-Game/'
path = ['/home/doug/Documents/projects/serialgui code/', '/home/doug/Documents/projects/OXgame/OX-AI-Game/']
Graph = createPydotGraph(path=path, plotExternals=False, headLabels=True, tailLabels=False, labels=False,
                                                         headDetLvl=2,    tailDetLvl=1,    labelDetLvl=2)

im = Image(Graph.create_png())

display(im)


saveGraphImage(Graph, 'latest try 4.png')

print(Graph.to_string())
help(pydot.Edge())


'''
-----------------------------Archive--------------------------------------------


# toyGraph

Graph = pydot.Dot(graph_type='digraph')
Graph.add_node(pydot.Node('test1', label='HelloWorld'))
Graph.add_node(pydot.Node('test2'))
edge = pydot.Edge('test2', 'test1')
edge.obj_dict['attributes']
edge.set_dir('both')
edge.set_color('"red:blue"')
Graph.add_edge(edge)
print(Graph.to_string())

subGraph = pydot.Cluster('Hello World', label='FileName')
subGraph.add_node(pydot.Node('classes', label='Classes', shape='square', comment='i wonder what this does'))
subGraph.add_node(pydot.Node('functions', label='Functions', shape='square'))
Graph.add_subgraph(subGraph)

# Nodes for nodes
color = 0
nodeColours = {}
for library in libraries:
    colourInd = color%colourRange
    nodeColours[library] = colourList[colourInd]
    Graph.add_node(pydot.Node(library, label=library, fontsize=25, color=colourList[colourInd]))
    color += 1

# Nodes for subgraph
colour = 0
nodeColours = {}
for library in libraries:
    colourInd = colour%colourRange
    nodeColours[library] = colourList[colourInd]
    subGraph = pydot.Cluster(library, label=library, fontsize=35, color=colourList[colourInd])
    classes = pydot.Node(library+' classes', label='Classes', shape='square', style='filled', color='oldlace')
    functions = pydot.Node(library+' functions', label='Functions', shape='polygon', sides=4, skew=0.2, style='filled', color='mintcream')
    subGraph.add_node(functions)
    subGraph.add_node(classes)
    subGraph.add_node(pydot.Node(library+'_out', label='', shape='circle', width=0.12, height=0.12, fontsize=1))
    subGraph.add_node(pydot.Node(library+'_in', label='', shape='circle', width=0.12, height=0.12, fontsize=1))
    subGraph.add_edge(pydot.Edge(library+'_in', library+' classes'))
    subGraph.add_edge(pydot.Edge(library+'_in', library+' functions'))
    subGraph.add_edge(pydot.Edge(library+' classes', library+'_out'))
    subGraph.add_edge(pydot.Edge(library+' functions', library+'_out'))
    Graph.add_subgraph(subGraph)
    colour += 1

# Edges for subgraph
for fileName in files:
    file = files[fileName]
    for imported in file['imports'].keys():
        label = '\n'.join(files[fileName]['imports'][imported])
        Graph.add_edge(pydot.Edge(imported+'_out', fileName+'_in', lhead='cluster_'+fileName, ltail='cluster_'+imported, tailport='s', headport='n', label = label, decorate='true', color=nodeColours[imported], fontcolor=nodeColours[imported]))


def find_deps_in_folder():
    for file in os.listdir():
        if file.endswith('.py'):
            fileName = file
            fileTextBlock = open(file).read()
            fileTextBlock = removeTrippleQuotes(fileTextBlock)
            fileTextBlock = removeHashComments(fileTextBlock)
            fileText = fileTextBlock.splitlines()

            print('\n')
            print(fileName)
            fileImports = {}
            fileFunctions = []
            fileClasses = {}
            lineNo = 0
            for line in fileText:
                splits = [',', '=', '+', '-', '*', '/', '(', '[', '{', ')', ']', '}']

                """ handle 'import' and 'import ... as'"""
                if line.startswith('import '):
                    for split in splits:
                        line = line.replace(split, ' ')
                    words = line.split()

                    # identify imported module
                    imported = words[1]
                    print(imported)
                    if line.count(' as ') > 0:
                        alias = words[3]
                    else:
                        alias = words[1]

                    # check for module uses
                    uses = set()
                    for line2 in fileText:
                        if line2.count(alias) > 0:
                            for split in splits:
                                line2 = line2.replace(split, ' ')
                            useCheck = line2.rsplit()
                            for word in useCheck:
                                if word.startswith(alias + '.'):
                                    use = word[len(alias)+1:]
                                    uses.add(use)
                    fileImports[imported] = [*uses]

                if line.startswith('def '):
                    fileFunctions.append(line[4:-1])

                if line.startswith('class '):
                    # identify the class text block
                    classText = []
                    for line2 in fileText[lineNo+1:]:
                        if line2.startswith(' ') is False and len(line2.split()) > 0:
                            break
                        else:
                            classText.append(line2)

                    # identify the class functions
                    classFunctions = []
                    for line2 in classText:
                        words = line2.split()
                        if len(words) > 0:
                            if words[0] == 'def':
                                lineStart = line2.find('def')
                                classFunctions.append(line2[lineStart+4:-1])
                    fileClasses[line[5:-1]] = classFunctions

                lineNo += 1



            print(fileImports)
            print(fileFunctions)
            print(fileClasses)
'''
