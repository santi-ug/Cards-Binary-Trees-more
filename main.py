import pygame
import json
import sys
import pygame_gui
from abstract import *
from button import Button
from objects import *
from graph import *
from general import SolSet
from pygame.locals import *
import random
from tree import BinaryTree, NAryTree
from combobox import *


class DoubleClick:
    def __init__(self):
        self.double_click = pygame.time.Clock()
        self.time = 0  # Necessary to temporary store time passed after checking second down click
        self.first_click = True  # Is this the first click in the double click
        self.wasDC = False  # Was the alst call to isDC() a double click

    # Implementing double click was a lot harder than initially thought
    # A double click starts on a mouse down and ends on the second mouse up
    # If there is too much time between the first and second mouse down, the second mouse down will be treated as a first
    def isDC(self, event):
        if event.type == MOUSEBUTTONDOWN and event.button == 1:
            click_time = self.double_click.tick()  # Check how long since last click
            if (
                not self.first_click
            ):  # If it's the first click, exit function with False
                # If it's the second downclick, make sure that a double click is still a possibility
                # If not, make this down click the first click
                # Since tick() was called, store time passed in self.time, to be added to the upclick later
                if click_time > SolSet.double_speed:
                    self.first_click = True
                else:
                    self.time = click_time

        if event.type == MOUSEBUTTONUP and event.button == 1:
            if not self.first_click:  # If it's the second click
                click_time = (
                    self.double_click.tick()
                )  # Get time since last click (the second down click)
                self.first_click = True  # The next click will again be first
                if (
                    click_time + self.time < SolSet.double_speed
                ):  # Add the click_time and self.time and check if fast enough
                    self.wasDC = True
                    return True
            else:
                # If it was first first upclick, now the second_click is expected
                self.first_click = False
        # If we get to here, no double click was detected
        self.wasDC = False
        return False


class Game:
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()

        # basic
        random.seed()
        self.screen = self.setDisplay()  # Display dimensions
        pygame.display.set_caption("Taller | Estructura de Datos")
        self.double_click = DoubleClick()  # Double click checker
        self.text_main_btns = [
            "Pilas",
            "Árboles",
            "Grafos",
            "Pick up",
            "Exit",
            "You Win!",
            "Add",
        ]
        self.main_btns = []
        self.initButtons()

        # cards
        self.move_pile = Repository("Repository")  # For moving piles
        self.cards = self.loadCards()  # All the cards
        self.piles = self.populatePiles()  # All the piles
        self.won = False
        self.cards_active = False

        # tree
        self.tree = TreeController(
            self.main_btns[6], self.main_btns[0], self.main_btns[1], self.main_btns[2], self.screen
        )

        # graph
        self.graph = GraphController(self.screen)

        # main
        self.menu_active = True

    # Inputs to main_btns (buttons) a button with it's respective text from text_main_btns
    def initButtons(self):
        for i in range(len(self.text_main_btns)):
            if i == 6:  # ADD
                btn = Button(self.text_main_btns[i], (5, 110))
                btn.setDimensions(80, 40)
            elif i == 5:  # WINNER
                btn = Button(self.text_main_btns[i], (280, 350))
                btn.setDimensions(200, 50)
            else:  # PILA, ARBOL, GRAFOS, PICK UP, EXIT
                btn = Button(self.text_main_btns[i], (650 / 2, (i + 3) * 60))
                btn.setDimensions(160, 50)
                if i != 4:  # EXIT
                    btn.visible = True

            self.main_btns.append(btn)

    # The display dimensions are calculated given the wanted margins and card dimensions
    def setDisplay(self):
        return pygame.display.set_mode((800, 600))

    # Load the cards (the common card back and the card images)
    def loadCards(self):
        Card.loadBack(SolSet.image_back)
        cards = [Card(x, (0, 0)) for x in SolSet.image_names]
        random.shuffle(cards)
        return cards

    # Place the piles (are reset the SuitPile win number down to 0)
    def populatePiles(self):
        piles = []
        suit_piles = []
        SuitPile.total_cards = 0

        marker = 0  # Keeps track of the last card added
        x = SolSet.margin_space  # The x_position of the pile
        y = SolSet.margin_space + SolSet.image_resolution[1] + SolSet.row_space

        for i in range(1, 8):  # Need seven main piles
            pile_name = "Main" + str(i)
            if i == 1:
                cards = self.cards[
                    0:1
                ]  # Each pile position also tells me how many cards it needs
                piles.append(
                    MainPile(
                        pile_name,
                        (x, y),
                        SolSet.image_bottom,
                        SolSet.tile_small_space,
                        SolSet.tile_large_space,
                        cards,
                    )
                )
            else:
                cards = self.cards[
                    marker: 2 + marker
                ]  # Each pile position also tells me how many cards it needs
                piles.append(
                    MainPile(
                        pile_name,
                        (x, y),
                        SolSet.image_bottom,
                        SolSet.tile_small_space,
                        SolSet.tile_large_space,
                        cards,
                    )
                )

            # The suit piles are exactly above main piles (starting on the four one)
            if i == 7:
                suit_piles.append(
                    SuitPile(
                        "Suit" +
                        str(1), (x, SolSet.margin_space), SolSet.image_bottom
                    )
                )

            # tick along x and marker
            x += piles[-1].rect.w + SolSet.start_space
            if i == 1:
                marker = 1 + marker
            else:
                marker = 2 + marker

        empty = []
        piles.append(
            StartPile(
                "Start",
                (SolSet.margin_space, SolSet.margin_space),
                SolSet.start_space,
                SolSet.image_back,
                empty,
            )
        )

        # The last four piles always must be the suit piles
        piles.extend(suit_piles)
        return piles

    # simply gets the pile that was clicked (none if no pile was clicked)
    def clickedPile(self, event):
        for pile in self.piles:
            if pile.hasPosition(event.pos):
                return pile

    # When a double click occurs, try to put that card in the suit piles
    def onDoubleClick(self, event):
        clicked_pile = self.clickedPile(event)  # Get the clicked pile

        if clicked_pile:
            # onDoubleClick always returns only one card
            card_taken = clicked_pile.onDoubleClick(event)
            if card_taken:  # If a card is returned (double click was valid)
                no_home = True  # This card right now has no home in the Suit piles
                for pile in self.piles[-1:]:  # Go through the four suit piles
                    # The False ensures that the card_taken does not have to contact the Suit piles
                    if pile.validAddCards(card_taken, False):
                        pile.addCards(card_taken)
                        no_home = False
                        break
                # If no suit pile has been found, return the card that was double clicked
                if no_home:
                    card_taken[0].pile.addCards(card_taken)

    # Draw is simple, just draw all the piles
    def draw(self):
        if not self.menu_active:

            if self.cards_active:
                for pile in self.piles:
                    pile.draw(self.screen)
                self.move_pile.draw(self.screen)
                if self.won:
                    self.main_btns[5].visible = True
                    self.winScreen()
                self.main_btns[4].visible = True
                self.main_btns[4].draw(self.screen)

            if self.tree.tree_active:
                # tree menu
                if self.tree.type_tree == -1:
                    self.tree.binary_tree_btn.visible = True
                    self.tree.binary_tree_btn.draw(self.screen)
                    self.tree.nary_tree_btn.visible = True
                    self.tree.nary_tree_btn.draw(self.screen)

                # binary tree
                elif self.tree.type_tree == 0:
                    self.tree.binary_tree_btn.visible = False
                    self.tree.nary_tree_btn.visible = False

                    self.tree.drawTreeMenu()
                    self.tree.drawBinaryTree()
                    self.main_btns[4].visible = True
                    self.main_btns[4].draw(self.screen)
                    self.main_btns[6].visible = True
                    self.main_btns[6].draw(self.screen)
                    self.tree.manager.draw_ui(self.screen)

                # nary tree
                elif self.tree.type_tree == 1:
                    self.tree.binary_tree_btn.visible = False
                    self.tree.nary_tree_btn.visible = False

                    self.tree.drawTreeMenu()
                    self.tree.drawTree()
                    self.main_btns[4].visible = True
                    self.main_btns[4].draw(self.screen)
                    self.main_btns[6].visible = True
                    self.main_btns[6].draw(self.screen)
                    self.tree.manager.draw_ui(self.screen)

            if self.graph.graph_active:
                self.graph.map_colombia.visible = True
                self.graph.graph_exit_button.visible = True
                self.graph.graph_reset_button.visible = True
                self.graph.draw(self.screen)

        else:
            self.main_btns[0].draw(self.screen)
            self.main_btns[1].draw(self.screen)
            self.main_btns[2].draw(self.screen)

    def start(self):
        self.gameLoop()

    # When all the cards are in the suit pile
    def winCondition(self):
        return SuitPile.total_cards == len(self.cards)

    def winScreen(self):
        self.main_btns[5].draw(self.screen)

    def reset(self):
        self.cards = self.loadCards()
        self.piles = self.populatePiles()
        self.main_btns[5].visible = False
        self.won = False

    def cardGame(self, event):
        self.main_btns[0].visible = False
        self.main_btns[1].visible = False
        self.main_btns[2].visible = False
        # Check and store if a double click occured
        if (
            event.type == MOUSEBUTTONUP
            or event.type == MOUSEBUTTONDOWN
            and event.button == 1
        ):
            self.double_click.isDC(event)

            # Pressing r resets the program
        if event.type == KEYUP and event.key == K_r:
            self.reset()

            # If the game has been won, reset it with r
        if self.winCondition():
            self.won = True
            if event.type == KEYUP and event.key == K_r:
                self.reset()
                # exit to main menu

                # Now for the main meat of the program
        else:
            if event.type == MOUSEBUTTONUP and event.button == 1:
                # Is the user currently dragging cards (and now wants to let them go)
                # I store it as the I need to check this variable again later and the cards might have been released
                move_pile_full = self.move_pile.hasCards()

                if move_pile_full:  # If yes
                    # This finds the left most pile where the dropped cards are accepted
                    selected_pile = None
                    for pile in self.piles:
                        if pile.validAddCards(self.move_pile.cards):
                            selected_pile = pile
                            break

                            # If a valid pile is found, drop the cards there, otherwise return the cards
                    if selected_pile:
                        self.move_pile.addToPile(selected_pile)
                    else:
                        self.move_pile.returnCards()

                    # The double click must come after the move_pile is resolved, so that no cards are even in the move_pile
                if self.double_click.wasDC:
                    self.onDoubleClick(event)

                    # If the move_pile was empty and no double click, just run a simple onClick on the pile
                if not move_pile_full and not self.double_click.wasDC:
                    clicked_pile = self.clickedPile(event)
                    if clicked_pile:
                        clicked_pile.onClick(event)

                    # If mouse is held down, move those cards to the self.move_pile
            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                clicked_pile = self.clickedPile(event)
                if clicked_pile:
                    cards_taken = clicked_pile.onClick(event)
                    if cards_taken:
                        self.move_pile.addCards(cards_taken)

                    # if the mouse is moved, move the mouse_pile (if it has cards)
            if event.type == MOUSEMOTION:
                if self.move_pile.hasCards():
                    self.move_pile.movePosition(event.rel)

    def mainMenu(self, event):
        self.main_btns[0].visible = True
        self.main_btns[1].visible = True
        self.main_btns[2].visible = True

    # The basic idea of the game loop is thus :
    # If a pile is clicked, onClick() is run
    # If onClick() returns cards, this means that these cards can be moved around (while mouse is held down)
    # The moving of cards is performed by self.move_pile
    # With a double click, the down, up, and and click are read as single clicks (and still run as such)
    # The lst up click will result in onDoubleClick being called
    def gameLoop(self):
        while True:
            REFRESH_RATE = self.clock.tick(144) / 1000

            event_list = pygame.event.get()
            for event in event_list:
                # Check if the program is quit
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()

                # check clicks
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    # CARDS
                    # click pila
                    if self.main_btns[0].hasPosition(event.pos):
                        self.menu_active = False
                        self.tree.tree_active = False
                        self.graph.graph_active = False
                        self.cards_active = True
                    # click pick up
                    if self.main_btns[3].hasPosition(event.pos):
                        # pick up cards
                        pass
                    # click exit
                    if self.main_btns[4].hasPosition(event.pos):
                        self.tree.tree_active = False
                        self.cards_active = False
                        self.graph.graph_active = False
                        self.menu_active = True

                        # TREES
                    # click arbol
                    if self.main_btns[1].hasPosition(event.pos):
                        self.menu_active = False
                        self.cards_active = False
                        self.graph.graph_active = False
                        self.tree.tree_active = True

                    # click exit
                    if self.main_btns[4].hasPosition(event.pos):
                        self.tree.type_tree = -1
                        self.tree.order_types.main = self.tree.main_text
                        self.cards_active = False
                        self.tree.tree_active = False
                        self.graph.graph_active = False
                        self.menu_active = True

                        # GRAPHS
                    # click grafo
                    if self.main_btns[2].hasPosition(event.pos):
                        self.cards_active = False
                        self.tree.tree_active = False
                        self.menu_active = False
                        self.graph.graph_active = True

                    # click exit
                    if self.graph.graph_exit_button.hasPosition(event.pos):
                        self.cards_active = False
                        self.tree.tree_active = False
                        self.graph.graph_active = False
                        self.graph.graph_reset_button.visible = False
                        self.menu_active = True

                    # click reset
                    if self.graph.graph_reset_button.hasPosition(event.pos):
                        self.graph.origin.main = self.graph.main_origin_text
                        self.graph.destination.main = self.graph.main_destination_text

                # show whats active
                if self.cards_active:
                    self.cardGame(event)
                elif self.tree.tree_active:
                    self.tree.treeInputCheck(event, event_list)
                elif self.graph.graph_active:
                    self.graph.runGraphs(event_list)
                else:
                    self.mainMenu(event)

                self.tree.manager.process_events(event)

            self.tree.manager.update(REFRESH_RATE)
            self.screen.fill((120, 120, 120))
            self.draw()
            pygame.display.flip()


#########
# TREE CODE


class TreeController(object):
    def __init__(self, addbutton, pilabutton, arbolbutton, grafobutton, screen):
        self.screen = screen
        self.tree_active = False
        # 0 = binary
        # 1 = n-ary
        # -1 = not picked
        self.type_tree = -1
        self.binary_tree_btn = Button("Binary Tree", (650 / 2, 180))
        self.binary_tree_btn.setDimensions(160, 50)
        self.nary_tree_btn = Button("N-Ary Tree", (650 / 2, 240))
        self.nary_tree_btn.setDimensions(160, 50)

        self.base_font = pygame.font.Font(None, 20)
        self.tree_font = pygame.font.Font(None, 24)

        self.tree = NAryTree()
        self.binary_tree = BinaryTree()

        self.manager = pygame_gui.UIManager((800, 600))

        self.nodes = ""
        self.father = ""
        self.value = ""

        self.text_input_fields = ["Amt Nodes", "Father Node", "Value"]
        #                             a              b           c
        self.text_fields = []
        self.initTextFields()
        self.ADD_B = addbutton
        self.PILA_B = pilabutton
        self.ARBOL_B = arbolbutton
        self.GRAFO_B = grafobutton

        # comboboxes & settings
        COLOR_INACTIVE = (205, 92, 92)
        COLOR_ACTIVE = (255, 150, 150)
        COLOR_LIST_INACTIVE = (140, 140, 140)
        COLOR_LIST_ACTIVE = (255, 150, 150)
        self.main_text = "Select Order Type"
        self.order_types = DropDown(
            [COLOR_INACTIVE, COLOR_ACTIVE],
            [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
            624,
            22,
            165,
            30,
            self.main_text
        )
        self.initComboBoxes()

        # for comboboxes
        self.binary_tree_inorder = []
        self.binary_tree_preorder = []
        self.binary_tree_postorder = []
        self.binary_tree_levelorder = []
        self.tree_levelorder = []
        self.order_given = []

    def initComboBoxes(self):
        self.order_types.options.append("INORDEN")
        self.order_types.options.append("POSTORDEN")
        self.order_types.options.append("PREORDER")
        self.order_types.options.append("AMPLITUD")

    # FIX
    def showOrder(self):
        # self.tree_font
        if self.type_tree == 0:  # binary
            if self.order_types.main == self.order_types.options[0]:
                self.binary_tree_inorder = self.binary_tree.inorder()
                self.drawTheShownOrder(0)
            elif self.order_types.main == self.order_types.options[1]:
                self.binary_tree_preorder = self.binary_tree.preorder()
                self.drawTheShownOrder(1)
            elif self.order_types.main == self.order_types.options[2]:
                self.binary_tree_postorder = self.binary_tree.postorder()
                self.drawTheShownOrder(2)
            elif self.order_types.main == self.order_types.options[3]:
                self.binary_tree_levelorder = self.binary_tree.level_order_traversal()
                self.drawTheShownOrder(3)
        elif self.type_tree == 1:  # n-ary
            if self.order_types.main == self.order_types.options[3]:
                self.tree_levelorder = self.tree.level_order_traversal()
                self.drawTheShownOrder(4)

    def drawTheShownOrder(self, n):
        self.orderDefiner(n)

        if self.order_types.main != self.main_text:
            txt = self.tree_font.render(
                self.order_types.main + ' = ' + str(self.order_given), True, (255, 255, 255))
            pg.draw.rect(self.screen, (20, 20, 20), (self.screen.get_width()//2 - txt.get_width()//2 - 15, self.screen.get_height()-100,
                                                     txt.get_width() + 30, 32), 0)
            self.screen.blit(txt, (self.screen.get_width(
            )//2 - txt.get_width()//2, self.screen.get_height()-100 + txt.get_height()//2))

    def orderDefiner(self, n):
        if n == 0:
            self.order_given = self.binary_tree_inorder
        elif n == 1:
            self.order_given = self.binary_tree_preorder
        elif n == 2:
            self.order_given = self.binary_tree_postorder
        elif n == 3:
            self.order_given = self.binary_tree_levelorder
        elif n == 4:
            self.order_given = self.tree_levelorder

    def initTextFields(self):
        amt_nodes_txt_field = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((5, 20), (80, 25)),
            manager=self.manager,
            object_id="#a",
        )
        father_node_txt_field = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((5, 50), (80, 25)),
            manager=self.manager,
            object_id="#b",
        )
        value_txt_field = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect((5, 80), (80, 25)),
            manager=self.manager,
            object_id="#c",
        )
        self.text_fields.append(amt_nodes_txt_field)
        self.text_fields.append(father_node_txt_field)
        self.text_fields.append(value_txt_field)

    def addTreeNode(self):
        father, value, nodes = None, None, None
        data = [nodes, value, father]
        for i in range(len(self.text_fields)):
            if self.type_tree == 0 and i == 2:
                pass
            else:  # n-ary
                try:
                    if i == 0:
                        data[i] = int(self.nodes)
                    elif i == 1:
                        data[i] = int(self.value)
                    elif i == 2:
                        data[i] = int(self.father)
                except:
                    print("Text inserted is not a number")
                    return

        if self.type_tree == 0:  # binary
            if self.binary_tree.len < data[0]:
                self.binary_tree.insert_node(self.binary_tree.root, data[1])
            else:
                print("Maximum amount of nodes allowed already reached")
        elif self.type_tree == 1:  # n-ary
            if self.tree.len < data[0] - 1:
                self.tree.insert_child(self.tree.root, data[2], data[1])
            else:
                print("Maximum amount of nodes allowed already reached")

    def drawTree(self):
        if self.tree.root != None:
            xDelta, yDelta = 100, 60
            xCoordinate = self.screen.get_width() // 2

            def dfs(node, level, xCoordenate):
                x, y = xCoordenate, 60 * (level + 1)
                for i in range(len(node.child)):
                    if i % 2 == 0 and i > 0:
                        pygame.draw.line(self.screen, (255, 255, 255), (x, y), ((
                            x - xDelta * (i - 1)), y + (yDelta)), 3,)
                        dfs(node.child[i], level + 1, x - (xDelta * (i - 1)))
                    else:
                        pygame.draw.line(self.screen, (255, 255, 255), (x, y), ((
                            x + xDelta * i), y + (yDelta)), 3,)
                        dfs(node.child[i], level + 1, x + (xDelta * i))
                pygame.draw.circle(self.screen, (0, 0, 0), (x, y), 25)
                node_value = self.tree_font.render(
                    str(node.data), True, (255, 255, 255))
                self.screen.blit(node_value, (x - 5, y - 10))
            dfs(self.tree.root, 0, xCoordinate)

    def drawBinaryTree(self):
        if self.binary_tree.root != None:
            xDelta, yDelta = 150, 60  # Definición de deltas
            # PRimera coordenada de dibujado (mitad de la pantalla)
            xCoordenate = self.screen.get_width()//2

            def dfs(node: self.binary_tree.Node, level, xCoordenate, xDelta, r):
                # Se selecciona el nivel de Y dependiendo del nivel
                x, y = xCoordenate, yDelta*(level+1)

                if node.left:  # Dibujado de lineas4
                    pygame.draw.line(self.screen, (255, 255, 255),
                                     (x, y), (x - xDelta, y + yDelta), 3)
                if node.right:
                    pygame.draw.line(self.screen, (255, 255, 255),
                                     (x, y), (x + xDelta, y + yDelta), 3)

                if node.left != None:  # Llamados recursivos
                    dfs(node.left, level+1, xCoordenate -
                        xDelta, xDelta-(xDelta*0.45), r-1)
                if node.right != None:
                    dfs(node.right, level+1, xCoordenate +
                        xDelta, xDelta-(xDelta*0.45), r-1)

                # Dibujado de circulos (Nodos)
                if node.left == None and node.right == None and node != self.binary_tree.root:
                    pygame.draw.circle(self.screen, (0, 0, 0), (x, y), r)
                else:
                    pygame.draw.circle(self.screen, (0, 0, 0), (x, y), r)

                # Se dibuja el valor del nodo en el circulo
                node_value = self.base_font.render(
                    str(node.data), True, (255, 255, 255))
                self.screen.blit(
                    node_value, (x - node_value.get_width()//2, y-node_value.get_height()//2))
            dfs(self.binary_tree.root, 0, xCoordenate, xDelta, 25)

    def drawTreeMenu(self):
        if self.type_tree == 0:  # binary menu
            self.text_fields[1].disable()
            self.text_fields[1].set_position((900, 900))
            self.text_fields[2].set_position((5, 50))
            self.ADD_B.setPosition((5, 80))
            for i in range(len(self.text_input_fields)):
                if i == 1:
                    pass
                else:
                    pygame.draw.rect(self.screen, (120, 120, 120),
                                     self.text_fields[i], 2)
                    text = self.base_font.render(
                        self.text_input_fields[i], True, (255, 255, 255)
                    )
                    if i == 2:
                        self.screen.blit(text, ((90, (i) * 28), (40, 40)))
                    else:
                        self.screen.blit(text, ((90, (i + 1) * 25), (40, 40)))
            self.drawTheShownOrder(0)
        elif self.type_tree == 1:  # n-ary menu
            self.text_fields[1].enable()
            self.text_fields[1].set_position((5, 50))
            self.text_fields[2].set_position((5, 80))
            self.ADD_B.setPosition((5, 110))
            for i in range(len(self.text_input_fields)):
                pygame.draw.rect(self.screen, (120, 120, 120),
                                 self.text_fields[i], 2)
                text = self.base_font.render(
                    self.text_input_fields[i], True, (255, 255, 255)
                )
                if i == 1:
                    self.screen.blit(text, ((90, (i + 1) * 28), (40, 40)))
                elif i == 2:
                    self.screen.blit(text, ((90, (i + 1) * 29), (40, 40)))
                else:
                    self.screen.blit(text, ((90, (i + 1) * 25), (40, 40)))
            self.drawTheShownOrder(1)
        # combobox
        self.order_types.draw(self.screen)
        if self.tree.root != None or self.binary_tree.root != None:
            self.showOrder()

    def treeInputCheck(self, event, event_list):

        self.PILA_B.visible = False
        self.ARBOL_B.visible = False
        self.GRAFO_B.visible = False

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.binary_tree_btn.hasPosition(event.pos):
                self.binary_tree.__init__()
                self.binary_tree_inorder = []
                self.binary_tree_preorder = []
                self.binary_tree_postorder = []
                self.binary_tree_levelorder = []
                self.tree_levelorder = []
                self.order_given = []
                self.text_fields[0].set_text("")
                self.nodes = 0
                self.text_fields[2].set_text("")
                self.value = 0
                self.type_tree = 0
            elif self.nary_tree_btn.hasPosition(event.pos):
                self.tree.__init__()
                self.binary_tree_inorder = []
                self.binary_tree_preorder = []
                self.binary_tree_postorder = []
                self.binary_tree_levelorder = []
                self.tree_levelorder = []
                self.order_given = []
                self.text_fields[0].set_text("")
                self.nodes = 0
                self.text_fields[1].set_text("")
                self.father = 0
                self.text_fields[2].set_text("")
                self.value = 0
                self.type_tree = 1

        if (
            event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED
            and event.ui_object_id == "#a"
        ):
            self.nodes = event.text
        if (
            event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED
            and event.ui_object_id == "#b"
        ):
            self.father = event.text
        if (
            event.type == pygame_gui.UI_TEXT_ENTRY_FINISHED
            and event.ui_object_id == "#c"
        ):
            self.value = event.text

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.ADD_B.hasPosition(event.pos):
                self.addTreeNode()

        selected_order = self.order_types.update(event_list)
        if selected_order >= 0:
            self.order_types.main = self.order_types.options[selected_order]

        if self.tree.root != None or self.binary_tree.root != None:
            self.showOrder()


#########
# GRAPH CODE


class GraphController(object):
    class Map(abstract.AbstractObject):
        # url is gonna be the url for the image location (self.name)
        def __init__(self, url, pos):
            abstract.AbstractObject.__init__(self, url, pos)
            self.image = self.loadMap()
            self.visible = False

        def setDimensions(self, w, h):
            self.drawing_image = pygame.transform.scale(self.image, (w, h))

        def loadMap(self):  # self.name = "mapcolombia.png" = url
            self.image = pygame.image.load(self.name)
            return self.image.convert_alpha()

        def draw(self, screen):
            if self.visible:
                screen.blit(self.drawing_image, self.rect)

    def __init__(self, screen):
        # basic
        self.map_colombia = self.Map("mapcolombia.png", (188, 22))
        # original                     (529, 695)
        self.map_colombia.setDimensions(423, 556)
        self.graph_active = False
        # exit button
        self.graph_exit_button = Button("Exit", (202, 470))
        self.graph_exit_button.setDimensions(160, 30)
        self.graph_reset_button = Button("Reset", (202, 510))
        self.graph_reset_button.setDimensions(160, 30)

        # graphs
        self.city_content = Graph()

        # comboboxes & settings
        COLOR_INACTIVE = (205, 92, 92)
        COLOR_ACTIVE = (255, 150, 150)
        COLOR_LIST_INACTIVE = (140, 140, 140)
        COLOR_LIST_ACTIVE = (255, 150, 150)
        self.main_origin_text = "Select Origin"
        self.origin = DropDown(
            [COLOR_INACTIVE, COLOR_ACTIVE],
            [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
            12,
            22,
            165,
            30,
            self.main_origin_text
        )
        self.main_destination_text = "Select Destination"
        self.destination = DropDown(
            [COLOR_INACTIVE, COLOR_ACTIVE],
            [COLOR_LIST_INACTIVE, COLOR_LIST_ACTIVE],
            624,
            22,
            165,
            30,
            self.main_destination_text
        )
        self.keys = {}
        self.coordinates = []
        self.config()

    def config(self):
        self.read_json()
        self.set_coordinates()
        i = 0
        for v in self.city_content.vertices:
            self.city_content.vertices[v].coordenadas = self.coordinates[i]
            i += 1
        for valor in self.keys.keys():
            self.origin.options.append(valor)
            self.destination.options.append(valor)

    def set_coordinates(self):
        self.coordinates.append((212, 66))  # San Andres
        self.coordinates.append((315, 293))  # Armeria
        self.coordinates.append((343, 101))  # Barranquilla
        self.coordinates.append((398, 214))  # Bucaramanga
        self.coordinates.append((367, 288))  # Bogotá
        self.coordinates.append((287, 327))  # Cali
        self.coordinates.append((328, 112))  # Cartagena
        self.coordinates.append((418, 189))  # Cúcuta
        self.coordinates.append((497, 564))  # Leticia
        self.coordinates.append((321, 239))  # Medellin
        self.coordinates.append((312, 162))  # Monteria
        self.coordinates.append((326, 344))  # Neiva
        self.coordinates.append((308, 274))  # Pereira
        self.coordinates.append((263, 397))  # Pasto
        self.coordinates.append((426, 75))  # Riohacha
        self.coordinates.append((367, 90))  # Santa Marta
        self.coordinates.append((395, 114))  # Valledupar
        self.coordinates.append((381, 310))  # Villavicencio

    def read_json(self):
        with open('ciudades.json') as data:
            citys = json.load(data)
            for city in citys:
                self.city_content.agregar_vertice(city.get('id'))
                self.keys[city.get('name')] = city.get('id')
            for city in citys:
                for destination in city.get('destinations'):
                    p = random.randint(1, 12)
                    self.city_content.generar_arista(
                        city.get('id'), destination, p)

    def draw(self, screen):
        self.map_colombia.draw(screen)
        self.origin.draw(screen)
        self.destination.draw(screen)
        if self.origin.main != self.main_origin_text and self.destination.main != self.main_destination_text:
            self.drawConnections(screen)
        self.drawGraph(screen)
        if self.graph_active:
            self.graph_reset_button.draw(screen)
            self.graph_exit_button.draw(screen)

    def drawGraph(self, screen):
        tempo_font = pg.font.Font(None, 18)
        for i in range(len(self.coordinates)):
            txt = tempo_font.render(self.origin.options[i], True, (0, 0, 0))
            pg.draw.circle(screen, (255, 255, 255),
                           self.coordinates[i], 5, 0)
            pg.draw.circle(screen, (0, 0, 0), self.coordinates[i], 5, 2)
            screen.blit(
                txt, (self.coordinates[i][0] - txt.get_width()//2, self.coordinates[i][1] - 20))

    def drawConnections(self, screen):
        for v in self.city_content.vertices:
            for destino in self.city_content.vertices[v].vecinos:
                pg.draw.line(screen, (0, 0, 0), self.city_content.vertices[v].coordenadas,
                             self.city_content.vertices[destino[0]].coordenadas, 1)

    def runGraphs(self, event_list):
        selected_origin = self.origin.update(event_list)
        if selected_origin >= 0:
            self.origin.main = self.origin.options[selected_origin]

        selected_destination = self.destination.update(event_list)
        if selected_destination >= 0:
            self.destination.main = self.destination.options[selected_destination]

#######
# MAIN RUN


if __name__ == "__main__":
    g = Game()
    g.start()
