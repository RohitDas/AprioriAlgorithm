class Node(object):
    def __init__(self,
                 k,
                 prime_k, 
                 leaf_load,
                 is_internal,
                 is_leaf,
                 is_root,
                 level):
        self.k = k
        self.prime_k = prime_k
        self.leaf_load = leaf_load
        self.is_root = is_root
        self.is_internal = is_internal
        self.is_leaf = is_leaf
        self.level = level
        self.values = set([])
        self.children = {}
        self.initialize()

    def initialize(self):
        """
            Function to Initialize an internal node or a root with its leaves.
                                Node(prime_k=3)
                                 |
            _____________________ __________________________
           |                     |                          |
           LeafNode             LeafNode                   LeafNode

        """
        if not self.is_leaf:
            for i in range(self.prime_k):
                self.children.update({
                    i: Node(self.k,self.prime_k, self.leaf_load,
                            False, True, 
                            False, self.level+1)
                })

    def add_element(self,
                    val):
        if self.is_leaf:
            self.values.add(val)
            if self.is_overloaded() and self.level < self.k:
                return self.divide_leaf_node()
            else:
                return None
        else:
            assert self.is_root or self.is_internal, "A leaf can never be neither of leaf, root or the internal node"
            try:
                child_index = val[self.level] % self.prime_k
            except:
                print(val, self.level)
                child_index = val[self.level] % self.prime_k
            result = self.children.get(child_index).add_element(val)
            if result:
                self.children[child_index] = result
            return None

    def add_elements(self, 
                    vals):
        """
            Function and takes a list of values and adds it to the Hash tree
        """
        for val in vals:
            self.add_element(val)

    def is_overloaded(self):
        """
            Function checks whether a leaf node is overloaded.
            Overloading shall happen when len(values) > leaf_node
        """
        assert self.is_leaf, "Only the leaves can use this function"
        return len(self.values) > self.leaf_load

    def divide_leaf_node(self):
        """
            When the load gets a lot, this function divides the leaf node and
            returns a new node.
        """
        new_node = Node(self.k,self.prime_k, 
                        self.leaf_load,
                        True,
                        False,
                        False,
                        self.level)
        new_node.add_elements(self.values)
        return new_node


    def visualize(self):
        if self.is_leaf:
            print("------------------------------------It is leaf node and it contains-------------------------------------------")
            print(self.values)
            print("--------------------------------------------------------------------------------------------------------------")

        else:
            for child_index in self.children:
                print("Child_" + str(child_index))
                self.children[child_index].visualize()



if __name__ == "__main__":
    prime_k = 5
    leaf_load = 5
    is_internal = False
    is_leaf = False
    is_root = True
    level = 0
    node = Node(3, prime_k, leaf_load, is_internal, is_leaf, is_root, level)
    elements = [(1,2,3), (1,2,4), (4,5,7), (1,2,5), (4,5,8), (1,5,9), (1,3,6),(2,3,4), (5,6,7), (3,4,5), (3,5,6), (3,5,7), (6,8,9), (3,6,8), (3,6,7)]
    node.add_elements(elements)
    node.visualize()

