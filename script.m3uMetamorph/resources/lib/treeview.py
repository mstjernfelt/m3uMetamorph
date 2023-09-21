import xbmcgui

class TreeNode:
    def __init__(self, label, children=None):
        self.label = label
        self.children = children if children else []

class TreeView:
    def __init__(self, root_node):
        self.root_node = root_node

    def display_tree(self):
        dialog = xbmcgui.Dialog()

        #import web_pdb; web_pdb.set_trace()

        selected_items = []

        node = self.root_node
        while True:
            options = [child.label for child in node.children] + ["Go Back"]
            selected_index = dialog.select(node.label, options)

            if selected_index < len(node.children):
                selected_child = node.children[selected_index]
                selected_items.append(selected_child.label)
                node = selected_child
            elif selected_index == len(node.children):
                # Go back to the parent node
                if node == self.root_node:
                    break
                else:
                    node = self.root_node
            else:
                break

        dialog.ok("Selected Items", ", ".join(selected_items))
