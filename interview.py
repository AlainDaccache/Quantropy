'''
Lists
'''


def reverse_array_list_swapping(lst):
    start, end = 0, len(lst)
    while start < end:
        lst[start], lst[end] = lst[end], lst[start]
        start += 1
        end -= 1
    return lst


def reverse_array_list_swapping_recursive(lst, start, end):
    if start >= end:
        return lst
    lst[start], lst[end] = lst[end], lst[start]
    return reverse_array_list_swapping_recursive(lst, start + 1, end - 1)


def reverse_array_list_recursive(lst):
    if len(lst) == 1:
        return lst
    else:
        return [lst[-1]] + reverse_array_list_recursive(lst[:-1])


'''
Linked Lists
'''


class Node:
    def __init__(self, data):
        self.data = data
        self.next = None


class LinkedList:
    def __init__(self):
        self.head = None

    def push(self, new_data):
        new_node = Node(new_data)
        new_node.next = self.head
        self.head = new_node

    def reverse(self):
        previous_node = None
        current_node = self.head
        while current_node is not None:
            next_node = current_node.next
            current_node.next = previous_node
            previous_node = current_node
            current_node = next_node
            self.head = current_node
        self.head = previous_node


linked_list = LinkedList()
linked_list.push(new_data=3)
linked_list.push(new_data=2)
linked_list.push(new_data=1)
linked_list.reverse()
print(linked_list)

'''
Graphs and Trees
'''

def breadth_first_search(graph, node):
    '''
    Breadth First Search

    1. Pick any node, visit the adjacent unvisited vertex, mark it as visited, display it, and insert it in a queue.
    2. If there are no remaining adjacent vertices left, remove the first vertex from the queue.
    3. Repeat step 1 and step 2 until the queue is empty or the desired node is found.

    Time Complexity: Since all of ​the nodes and vertices are visited, the time complexity for breadth_first_search
    on a graph is O(V + E); where V is the number of vertices and E is the number of edges.
    '''
    visited = []  # List to keep track of visited nodes.
    queue = []  # Initialize a queue
    visited.append(node)
    queue.append(node)

    while queue:
        s = queue.pop(0)
        print(s, end=" ")

        for neighbour in graph[s]:
            if neighbour not in visited:
                visited.append(neighbour)
                queue.append(neighbour)



# Driver Code
graph = {
    'A': ['B', 'C'],
    'B': ['D', 'E'],
    'C': ['F'],
    'D': [],
    'E': ['F'],
    'F': []
}
breadth_first_search(graph, 'A')


def depth_first_search(graph, node):
    '''
    Depth First Search

    1. Pick any node. If it is unvisited, mark it as visited and recur on all its adjacent nodes.
    2. Repeat until all the nodes are visited, or the node to be searched is found.

    Time Complexity: Since all of ​the nodes and vertices are visited, the time complexity for breadth_first_search
    on a graph is O(V + E); where V is the number of vertices and E is the number of edges.
    '''
    visited = set()  # Set to keep track of visited nodes.
    if node not in visited:
        print(node)
        visited.add(node)
        for neighbour in graph[node]:
            depth_first_search(graph, neighbour)


# Driver Code
depth_first_search(graph, 'A')
