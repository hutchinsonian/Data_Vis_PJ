import random
from data import *
import heapq

# 一致代价搜索 Uniform Cost Search
class UCS:
    def __init__(self, graph, priority_depth_limit=4, stepshow=False, vis_node=None, vis_edge=None):
        self.graph = graph
        self.priority_depth_limit = priority_depth_limit
        self.stepshow = stepshow # 与算法有关，是否访问边时将节点加入
        if stepshow:
            if vis_node is not None:
                self.vis_node = vis_node
            if vis_edge is not None:
                self.vis_edge = vis_edge

    def get_neighbors(self, node: Node):
        raise NotImplementedError()

    def add_node(self, node: Node):
        raise NotImplementedError()

    def add_edge(self, e, curnode):
        raise NotImplementedError()

    def vis_node(self, node: Node):
        pass
    
    def vis_edge(self, e, curnode):
        pass

    # 在优先级队列中寻找键
    def findkey(self, pq, key):
        for i in range(len(pq)):
            if pq[i][1] == key:
                return i
        return -1

    # 运行 UCS
    def run(self, q):

        explored = set()   # 是否被扩展
        visited = set()    # 是否被访问

        while len(q) > 0:
            top = heapq.heappop(q)
            top_priority = top[0]
            top_id = top[1]
            top_node = Node(self.graph, top_id)

            neighbors = self.get_neighbors(top_node)

            if top_id not in visited:
                visited.add(top_id)
                if self.add_node(top_node):
                    return  # 满足条件终止搜索
            
            explored.add(top_id)

            # 限制深度
            max_priority = top_priority + 1
            if max_priority > self.priority_depth_limit:
                continue

            for e in neighbors:
                neighbor = e["target"] if e["source"] == top_id else e["source"]
                priority = link_priority[e["relation"]]
                qidx = self.findkey(q, neighbor)

                flag = False
                if neighbor not in explored and qidx == -1:
                    priority = max(priority, max_priority)
                    heapq.heappush(q, [priority, neighbor])
                    flag = True
                elif qidx > -1 and priority < q[qidx][0]:
                    q[qidx][0] = priority
                    heapq.heapify(q)
                    flag = True
                
                if flag:
                    if self.stepshow and neighbor not in visited:  # 被访问
                        neighbor_node = Node(self.graph, neighbor)
                        self.get_neighbors(neighbor_node)  # 需要判别是否是核心节点
                        visited.add(neighbor)
                        if self.add_node(neighbor_node):
                            return
                    if self.add_edge(e, top_id):
                        return


class searchUCS(UCS):
    def __init__(self, graph, limitation, vis_node=None, vis_edge=None):
        self.limitation = limitation
        self.node_limit = net_limit[limitation]["node"]
        self.edge_limit = net_limit[limitation]["edge"]
        self.subgraph = Subgraph(["id", "label", "style"], ["id", "source", "target", "label"])
        self.corenodes = []
        self.statdata = {"nodes": {}, "edges": {}, "industries": {}}

        self.default_style = {}
        self.core_style = {"fill": "blue"}

        super().__init__(graph, 4, True, vis_node, vis_edge)

    def get_neighbors(self, node: Node):
        if node.label == "IP" or node.label == "Cert":
            neighbors = node.queryNeighbors()
        else:
            neighbors = node.queryChildren()

        before = len(neighbors)
        node.iscore = coreasset(node.node_id, neighbors, self.limitation)
        # 这将移除关联的邻居节点
        neighbors = filter(node.node_id, neighbors, self.limitation)
        after = len(neighbors)
        print("%d" % before if before == after else "%d(%d)" % (before, after), end=" ")

        return toRecords(neighbors)

    def add_node(self, node: Node):

        # 移除正在访问的节点
        removenode(node.node_id)

        # cut off
        if self.node_limit == 0:
            return True
        self.node_limit -= 1

        if node.label not in self.statdata["nodes"].keys():
            self.statdata["nodes"][node.label] = 1
        else:
            self.statdata["nodes"][node.label] += 1

        industries = queryIndustry(node.node_id)
        for industry in industries:
            if industry not in self.statdata["industries"].keys():
                self.statdata["industries"][industry] = 1
            else:
                self.statdata["industries"][industry] += 1

        if node.iscore:
            self.corenodes.append(node.node_id)
            self.subgraph.addNode(
                {
                    "id": node.node_id,
                    "label": node.label + "_" + str(len(self.corenodes)),
                    "style": self.core_style,
                }
            )
        else:
            self.subgraph.addNode(
                {"id": node.node_id, "label": node.label, "style": self.default_style}
            )
        self.vis_node(node)

        return False

    def add_edge(self, e, curnode):

        if e["relation"] not in self.statdata["edges"].keys():
            self.statdata["edges"][e["relation"]] = 1
        else:
            self.statdata["edges"][e["relation"]] += 1

        self.subgraph.addEdge(
            {
                "id": str(e["id"]),
                "source": e["source"],
                "target": e["target"],
                "label": e["relation"],
            }
        )
        
        self.edge_limit -= 1
        self.vis_edge(e, curnode)
        if self.edge_limit == 0:
            return True
        return False

    def search_run(self, node_id):
        q = [[1, node_id]]
        super().run(q)
        if len(self.corenodes) == 0:
            print("No corenodes! Add the init node!")
            self.corenodes.append(node_id)


class pathUCS(UCS):
    def __init__(self, graph):
        super().__init__(graph, 3, False)

    def get_neighbors(self, node: Node):
        return toRecords(node.queryNeighbors())

    def add_node(self, node: Node):
        if node.node_id in self.targets:
            self.targets.remove(node.node_id)
            tpath = []
            tptr = node.node_id

            while tptr != self.source:
                tedge = self.edge_to[tptr]
                tpath.append(tedge["id"])
                tptr = tedge["prev"]
            tpath.reverse()

            for edgeid in tpath:
                self.visitedEdges.add(edgeid)
            self.targetPaths[node.node_id] = tpath
            print("%s: %s" % (node.node_id, str(tpath)))

        return len(self.targets) == 0

    def add_edge(self, e, curnode):
        neighbor = e["target"] if e["source"] == curnode else e["source"]
        self.edge_to[neighbor] = {"id": e["id"], "prev": curnode}

    def path_run(self, node_id, subset):
        self.source = node_id
        self.targets = set(subset)
        self.targets.remove(node_id)

        # Store the prev node
        self.edge_to = {}
        # Target Path
        self.targetPaths = {}
        # Visited Path
        self.visitedEdges = set()

        q = [[0, node_id]]
        super().run(q)

class subUCS(UCS):
    def __init__(self, graph, ifneighbor=False):
        self.subgraph = Subgraph(["id","style","score"],["id","source","target"])
        self.ifneighbor = ifneighbor

        self.default_style = {}
        self.core_style = {"fill": "blue"}
        super().__init__(graph, 10, False) # Almost infinity.

    def get_neighbors(self, node: Node):
        return toRecords(node.queryNeighbors())

    def add_visited_node(self, node_id, iscore):
        if node_id not in self.visitedNode:
            self.visitedNode.add(node_id)
            self.subgraph.addNode({
                "id": node_id,
                "style": self.core_style if iscore else self.default_style,
                "score": queryScore(node_id)
            })
    
    def add_visited_edge(self, edge_id, source, target):
        if edge_id not in self.visitedEdge:
            self.visitedEdge.add(edge_id)
            self.subgraph.addEdge({
                "id": str(edge_id),
                "source": source,
                "target": target,
            })

    def add_neighbors(self, node_id):
        neighbors = self.get_neighbors(Node(self.graph,node_id))
        for e in neighbors:
            self.add_visited_edge(e["id"], e["source"], e["target"])
            neighbor = e["target"] if e["source"] == node_id else e["source"]
            self.add_visited_node(neighbor, False)

    def add_node(self, node: Node):
        if node.node_id in self.targets:
            self.targets.remove(node.node_id)
            tptr = node.node_id
            self.add_visited_node(tptr, True)

            while tptr != self.source:
                tedge = self.edge_to[tptr]
                if self.ifneighbor:
                    self.add_neighbors(tptr)
                else:
                    self.add_visited_edge(tedge["id"], tedge["prev"], tptr)
                    if tptr != self.source:
                        self.add_visited_node(tedge["prev"], False)
                tptr = tedge["prev"]

        return len(self.targets) == 0

    def add_edge(self, e, curnode):
        neighbor = e["target"] if e["source"] == curnode else e["source"]
        self.edge_to[neighbor] = {"id": e["id"], "prev": curnode}

    def sub_run(self, subset):
        self.source = subset[0]
        self.targets = set(subset)
        self.targets.remove(self.source)

        # Store the prev node
        self.edge_to = {}

        self.visitedNode = set()
        # Add source node into subgraph
        self.add_visited_node(self.source, True)
        self.visitedEdge = set()

        q = [[0, self.source]]
        super().run(q)