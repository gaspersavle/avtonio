#!/usr/bin/python3
# -*- coding: utf-8 -*-
from graph_gen import tagMap, tagDets

class PathPlanning(object):
    def __init__(self):
        pass

    def calculate_h(self, nodeId, goalId):
        '''Calculate the heuristic cost from nodeId to goalId'''
        if nodeId in tagDets and goalId in tagDets:
            # tagDets : ID: (x, y)
            x1, y1 = tagDets[nodeId][0], tagDets[nodeId][1]
            x2, y2 = tagDets[goalId][0], tagDets[goalId][1]
            # euclidean distance
            return ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        return 0.0

    def backtracking(self, current_node):
        path = []
        while current_node is not None:
            path.append(current_node['id'])
            print(f"Path: {path}")
            parent_id = current_node['parent']
            if parent_id == None:
                break
                
            # Find parent in closed list - clearer implementation
            current_node is None
            for node in self.closed_list:
                if node['id'] == parent_id:
                    current_node = node
                    break
        path.reverse()
        return path



    def findPath(self, startId, goalId):
        '''Find the shortest path
        
        Inputs:
            startId - Id of the start tag.
            goalId  - Id of the goal tag.
                
        Outputs:
            path - A list of ordered tags that lead from the start tag to the goal tag
                 (including start and goal tag) or an empty list if path is not found.
        '''
        self.open_list = []
        self.closed_list = []

        active_node = {
                'id': startId,
                'parent': None,
                'g' : 0,
                'cost' : None
                }

        # Heuristic from start to end
        initial_h = self.calculate_h(startId, goalId)
        # Object = (nodeId, prevNodeId, gCost, fCost)
        initial_node = {
                        'id' : startId,
                        'parent' :None,
                        'g' : 0,
                        'cost' : initial_h
                        }
        
        self.open_list.append(initial_node)

        while self.open_list:
            #izberemo vozlisce, ki ima najmanjso razdaljo do konca
            active_node = min(self.open_list, key=lambda x: x['cost'])
            self.open_list.remove(active_node)
            if active_node['id'] == goalId:
                #Ce je trenutno vozlisce ciljno, ga dodamo na closed_list, ki bo prispeval k poti do cilja
                self.closed_list.append(active_node)
                current_node_marker = active_node
                
                # Backtrack from goal to start
                path = self.backtracking(current_node_marker)
                print(f"Path from {startId} to {goalId} : {path}")
                return path
            
            self.closed_list.append(active_node)
            
            # Process neighbours
            neighbours = tagMap.get(active_node['id'], ())
            
            for i in range(0, len(neighbours), 2):
                if i + 1 >= len(neighbours):
                    break
                    
                neighbour_id = neighbours[i]
                neighbour_cost = neighbours[i + 1]
                
                # Skip if already in closed list
                if any(node['id'] == neighbour_id for node in self.closed_list):
                    continue
                
                g_cost = active_node['g'] + neighbour_cost
                h_cost = self.calculate_h(neighbour_id, goalId)
                cost = g_cost + h_cost
                
                neighbour_node = {
                                  'id' : neighbour_id,
                                  'parent' : active_node['id'], 
                                  'g' : g_cost,
                                  'cost': cost
                                  }
                
                # Check if neighbor is already in open list
                existing_node = next((node for node in self.open_list if node['id'] == neighbour_id), None)
                
                if existing_node == None:
                    # Add new node to open list
                    self.open_list.append(neighbour_node)
                elif g_cost < existing_node['g']:
                    # Found better path, update the node
                    self.open_list.remove(existing_node)
                    self.open_list.append(neighbour_node)
        
        print(f"No path found from {startId} to {goalId}")
        return []

    def generateActions(self, path):
        '''Generate a list of actions for given path
        
        Inputs:
          path - A list of ordered tags that lead from the start tag to the goal tag
                 (including start and goal tag) or an empty list if path is not found.

        Outputs:
          actions - A list of actions the AGV need to execute in order to reach the goal tag
                    from the start tag or an empty list if no action is required/possible.
        '''
        actions = []

        for i in range(len(path)):
          node = path[i]

          if i + 1 >= len(path):
            break
          node_next = path[i + 1]

          neighbours = tagMap.get(node, ())

          # Find the next node in neighbours
          if neighbours[0] == node_next:
            dist = neighbours[1]
            action = 'left'
          elif neighbours[2] == node_next:
            dist = neighbours[3]
            action = 'right'
          else:
            dist = neighbours[5]
            action = 'forward'
          
          # print("Node: ", node, "-> Next Node: ", node_next, " | Action: ", action, " | Distance: ", dist)

          action_tuple = (action, node_next, dist)
          actions.append(action_tuple)


        print("-- actions --")
        print(actions)

        #TODO Convert path to actions here ...
        # kateri cri sledimo, katera je ciljna tock, razdalja do nje po črti 
        #action = ('left', 20, 0.202)
        #actions.append(action)

        return actions



if __name__ == '__main__':
  pp = PathPlanning()
  path = pp.findPath(2, 12)
  print(path)
  actions = pp.generateActions(path)
  print(actions)
