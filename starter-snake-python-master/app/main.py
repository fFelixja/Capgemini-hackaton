import bottle
import os
import random

from api import *

#astar = AStar.AStar()
#astar.__init__();

import heapq

heuristic = 10

class Cell(object):
    def __init__(self, x, y,reachable):
        self.reachable = reachable
        self.reachable = reachable
        self.x = x
        self.y = y
        self.parent = None
        # g cost to move from the starting cell to this cell.
        self.g = 0
        # h estimation of the cost to move from this cell to goal cell.
        self.h = 0
        # f f = g + h
        self.f = 0

class AStar(object):

    def __init__(self):
        # The set of currently discovered nodes that are not evaluated yet.
        # Created as a heap since its an efficient priority queue.
        self.openSet = []
        heapq.heapify(self.openSet)
        # Visited cells
        self.closedSet = set()
        # A grid to hold the cells
        self.cells = []
        self.grid_height = None
        self.grid_width = None

    def init_grid(self, start, goal, walls, width, height):
        print "Init grid"
        self.grid_height = height
        self.grid_width = width
        for x in range(self.grid_width):
            for y in range(self.grid_height):
                if (x,y) in walls:
                    reachable = False
                else:
                    reachable = True
                self.cells.append(Cell(x, y, reachable))
        self.start = self.get_cell(*start)
        self.goal = self.get_cell(*goal)
        print "Start cell: (" + str(self.start.x) + "," + str(self.start.y) +")"
        print "Goal cell: (" + str(self.goal.x) + "," + str(self.goal.y)+")\n"

    def get_cell(self, x,y):
        return self.cells[x * self.grid_height + y]

    def get_heuristic(self, cell):
        return heuristic * (abs(cell.x - self.goal.x) + abs(cell.y - self.goal.y))

    def get_adjacent_cells(self, cell):
        cells = []
        # Clockwise order, start with cell above
        if cell.y > 0:
            cells.append(self.get_cell(cell.x,cell.y - 1))
        if cell.x < self.grid_width - 1:
            cells.append(self.get_cell(cell.x + 1,cell.y))
        if cell.y < self.grid_height - 1:
            cells.append(self.get_cell(cell.x,cell.y + 1))
        if cell.x > 0:
            cells.append(self.get_cell(cell.x - 1,cell.y))
        return cells

    def reconstruct_path(self):
        cell = self.goal
        path = []
        path.append((cell.x, cell.y))
        while cell.parent is not self.start:
            cell = cell.parent
            path.append((cell.x,cell.y))
        path.append((self.start.x,self.start.y))
        path.reverse()
        return path

    def update_cell(self, adj, cell):
        adj.g = cell.g + heuristic
        adj.h = self.get_heuristic(adj)
        adj.parent = cell
        adj.f = adj.h + adj.g

    def solve(self):
         # add starting cell to open heap queue
         heapq.heappush(self.openSet,(self.start.f,self.start))

         while len(self.openSet):
             # pop cell from heap queue
            f, cell = heapq.heappop(self.openSet)
            # add cell to closed list so we don't process it twice
            self.closedSet.add(cell)
            # if ending cell, return found path
            if cell is self.goal:
                return self.reconstruct_path()
            # get adjacent cells for cell
            adj_cells = self.get_adjacent_cells(cell)
            for adj_cell in adj_cells:
                if adj_cell.reachable and adj_cell not in self.closedSet:
                    if (adj_cell.f, adj_cell) in self.openSet:
                        # if adj cell in open list, check if current path is
                        # better than the one previously found
                        # for this adj cell.
                        if adj_cell.g > cell.g + heuristic:
                            self.update_cell(adj_cell, cell)
                    else:
                        self.update_cell(adj_cell, cell)
                        # add adj cell to open list
                        heapq.heappush(self.openSet, (adj_cell.f, adj_cell))





@bottle.route('/')
def static():
    return "the server is running"


@bottle.route('/static/<path:path>')
def static(path):
    return bottle.static_file(path, root='static/')


@bottle.post('/start')
def start():
    data = bottle.request.json

    print(json.dumps(data))
    return StartResponse("#00ff00")

def empty_world(width,height):
    world = []
    for i in range(width):
        tmp = []
        for j in range(height):
            tmp.append(0)
        world.append(tmp)
    return world


def addFood(foods, world):
    for food in foods:
        x = foods["data"][0]["x"]
        y = foods["data"][0]["y"]
        world[x][y] = 2
    return world


def addSnake(pos,world):
    for p in pos:
        world[p[0]][p[1]] = 1
    return world

def find_food(grid):
    x = 0
    y = 0
    for row in grid:
        for c in grid:
            if c == 2: return (x,y)
            else: y +=1
        y = 0
        x +=1
    return None

def relativeStep(c,n):
    difX = c[0] - n[0]
    print c[0]
    difY = c[1] - n[1]
    print "difX"
    print difX
    if difX > 0:
        return "left"
    elif difX < 0:
        return "right"
    elif difY > 0:
        return "up"
    else:
        return "down"


@bottle.post('/move')
def move():
    data = bottle.request.json
    print(json.dumps(data))

    world = empty_world(data["width"],data["height"])
    foods = data["food"]
    world = addFood(foods,world)



# TODO: add all other snakes
#    print "snakes"
#    snake_coords = []
#    snakes = data["snakes"]["data"]["body"]["data"]
#    for snake in snakes:
#        x = snake["x"]
#        y = snake["y"]
#        snake_coords.append((x,y))

#    for snake in snakes:
#            print snake[5]
        #data = snake["data"]

    #print snakes


    #coords = snake["data"][0]["body"]["data"]
    #coords = snake["data"]
#    print "COORDS:"
#    print coords
#    for c in coords:
#        x = c["x"]
#        y = c["y"]
#        snake_coords.append((x,y))

#    print snake_coords
#    world = addSnake(snake_coords,world)

    #world = addSnakes(world)

    me = data["you"]
    data_list = me["body"]["data"]
    me_pos = []
    for o in data_list:
        x = o["x"]
        y = o["y"]
        me_pos.append((x,y))

    goal = None
    world = addSnake(me_pos,world)

    for x in range(0,20):
        for y in range(0,20):
            if world[x][y] == 2:
                goal = (x,y)



    print me_pos
    start = me_pos[0]

    print "head is " + str(start)

    a_star = AStar()
    a_star.__init__()
    a_star.init_grid(start,goal,me_pos,data["width"],data["height"])
    path = a_star.solve()
    print "Path"
    print path
    nextpos = path[1]
    print "NextPos"
    print nextpos
    currentpos = me_pos[0]
    step = relativeStep(currentpos,nextpos)
    print step

    #directions = ['up', 'down', 'left', 'right']
    #direction = random.choice()

    return MoveResponse(step)


@bottle.post('/end')
def end():
    data = bottle.request.json

    # TODO: Any cleanup that needs to be done for this game based on the data
    print json.dumps(data)


@bottle.post('/ping')
def ping():
    return "Alive"


# Expose WSGI app (so gunicorn can find it)
application = bottle.default_app()

if __name__ == '__main__':
    bottle.run(
        application,
        host=os.getenv('IP', '0.0.0.0'),
        port=os.getenv('PORT', '8080'),
        debug=True)
