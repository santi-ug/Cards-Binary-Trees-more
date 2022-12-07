from collections import defaultdict


class NAryTree(object):
    class Node(object):

        """Clase inicializzadora del nodo"""

        def __init__(self, data) -> None:
            self.data = data
            self.child = []

    """ Clase inicializadora del arbol n-ario"""

    def __init__(self):
        self.root = None
        self.len = 0
        self.traversal = []
        self.visible = False

    """ Método de incersion de un nodo """

    def insert_child(self, root, parent, data):
        new_child = self.Node(data)  # Crea el nodo que se va a insertar
        if not self.root:
            self.root = new_child
        else:
            if root.data == parent and len(root.child) < 3:
                if (
                    not self.non_equals(data) and data != parent
                ):  # Valida si el nodo ya existe dentro del padre
                    root.child.append(new_child)
                    self.len += 1
                else:
                    print("Nodo repetido")
            else:
                l = len(
                    root.child
                )  # Toma la cantidad de hijos para el llamado recursivo
                for i in range(l):
                    # Llamado recursivo
                    self.insert_child(root.child[i], parent, data)

    """ Método que valida la existencia previa de un nodo buscado """

    def non_equals(self, data):
        temp = self.level_order_traversal()
        for level in temp:
            if data in level:
                return True
        return False

    def inorder(self):
        inorder = []

        def traversal(node):
            if node != None:
                traversal(node.left)
                inorder.append(node.data)
                traversal(node.right)

        traversal(self.root)
        self.traversal = inorder

    def preorder(self):
        preorder = []

        def traversal(node):
            if node != None:
                preorder.append(node.data)
                traversal(node.left)
                traversal(node.right)

        traversal(self.root)
        self.traversal = preorder

    def postorder(self):
        postorder = []

        def traversal(node):
            if node != None:
                traversal(node.left)
                traversal(node.right)
                postorder.append(node.data)

        traversal(self.root)
        self.traversal = postorder

    """ Recorre un arbol N-Ario de forma recursiva en base a su profundidad """

    def level_order_traversal(self):
        route = defaultdict(list)  # Crea el manejador de datos

        def dfs(node, level):  # Funcion encargada de añadir los valores al manejador
            route[level].append(node.data)
            for child in node.child:
                dfs(child, level + 1)  # LLamado recursivo p[or cada hijo

        dfs(self.root, 0)  # Primer llamado
        self.traversal = [ans for k, ans in sorted(route.items())]
        return [ans for k, ans in sorted(route.items())]


class BinaryTree(object):
    class Node:
        def __init__(self, data):
            self.data = data
            self.left = None
            self.right = None

    def __init__(self) -> None:
        self.root = None
        self.len = 0
        self.traversal = []
        self.visible = False

    """ Realiza la insercion de un nodo dentro de un arbol binario """

    def insert_node(self, root: Node, data):
        if self.root == None:
            self.root = self.Node(data)
            self.len += 1
            return
        if data < root.data:
            if root.left is None:
                if not self.non_equals(data):
                    root.left = self.Node(data)
                    self.len += 1
            else:
                self.insert_node(root.left, data)
        else:
            if root.right is None:
                if not self.non_equals(data):
                    root.right = self.Node(data)
                    self.len += 1
            else:
                self.insert_node(root.right, data)

    """ Método que valida la existencia previa de un nodo buscado """

    def non_equals(self, data):
        temp = self.level_order_traversal()
        for level in temp:
            if data in level:
                return True
        return False

    """ Realiza el recorrido inorder de un arbol binario """

    def inorder(self):
        inorder = []

        def traversal(node):
            if node != None:
                traversal(node.left)
                inorder.append(node.data)
                traversal(node.right)

        traversal(self.root)
        return inorder

    """ Realiza el recorrido preorder de un arbol binario """

    def preorder(self):
        preorder = []

        def traversal(node):
            if node != None:
                preorder.append(node.data)
                traversal(node.left)
                traversal(node.right)

        traversal(self.root)
        return preorder

    """ Realiza el recorrido postorder de un arbol binario"""

    def postorder(self):
        postorder = []

        def traversal(node):
            if node != None:
                traversal(node.left)
                traversal(node.right)
                postorder.append(node.data)

        traversal(self.root)
        return postorder

    """ Recorrido por amplitud de un arbol binario"""

    def level_order_traversal(self):
        route = defaultdict(list)  # Crea el manejador de datos

        def dfs(node, level):  # Funcion encargada de añadir los valores al manejador
            route[level].append(node.data)
            if node.left != None:
                dfs(node.left, level + 1)
            if node.right != None:
                dfs(node.right, level + 1)

        dfs(self.root, 0)  # Primer llamado
        self.traversal = [ans for k, ans in sorted(route.items())]
        return [ans for k, ans in sorted(route.items())]
