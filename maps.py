import os
import numpy as np
import time


class Maps(object):
    def __init__(self, dist_matrix, mag_matrix):
        self.Setup(dist_matrix)
        self.mag_matrix = mag_matrix
        return

    def dijkstra(self, A, startpoint):
        S = []
        U = [i for i in range(A.shape[1])]
        dm = A.copy()
        dm[dm == -1] = 9999
        path = [startpoint for i in range(dm.shape[1])]
        while(True):
            if len(U) == 0:
                break
            else:
                index_min = U[np.argmin(dm[startpoint, U])]
                min_dist = dm[startpoint, index_min]
                S.append(index_min)
                U.remove(index_min)
                for index in U:
                    temp_dist = dm[index_min, index] + min_dist
                    if temp_dist < dm[startpoint, index]:
                        dm[startpoint, index] = temp_dist
                        path[index] = index_min
        distance = dm[startpoint]
        return distance, path

    def Setup(self, dist_matrix):
        self.dist_matrix = dist_matrix
        self.best_dist = np.zeros_like(dist_matrix)
        self.best_path = np.zeros_like(dist_matrix)
        for i in range(dist_matrix.shape[0]):
            self.best_dist[i], self.best_path[i] = self.dijkstra(
                dist_matrix, i)
        return

    def Get_Best(self, startpoint, endpoint):
        best_dist = self.best_dist[startpoint, endpoint]
        best_path = [endpoint]
        point = endpoint
        previous = self.best_path[startpoint, point]
        while(previous != startpoint):
            best_path.append(previous)
            point = previous
            previous = self.best_path[startpoint, point]
        best_path.append(previous)
        best_path.reverse()
        return best_dist, best_path

    def Update(self):
        pass


if __name__ == "__main__":
    dist_matrix = [[0, 6, -1, -1, -1, 5, 8],
                   [6, 0, 10, -1, -1, -1, -1],
                   [-1, 10, 0, 4, -1, -1, 3],
                   [-1, -1, 4, 0, 7, -1, -1],
                   [-1, -1, 5, 7, 0, 2, 4],
                   [5, -1, -1, -1, 2, 0, -1],
                   [8, -1, 3, -1, 4, -1, 0]]
    dist_matrix = np.array(dist_matrix)
    Map = Maps(dist_matrix, dist_matrix)
    print('Distance Matrix:\n', Map.dist_matrix)
    print('Best Distance:\n', Map.best_dist)
    print('Best Path:\n', Map.best_path)
    i = 3
    j = 0
    print('From %i to %i,distance:%i' % (i, j, Map.Get_Best(i, j)[0]))
    print('Path: ', Map.Get_Best(i, j)[1])
