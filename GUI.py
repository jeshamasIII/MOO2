import tkinter as tk
from GameClass import Game
from ColonyClass import Planet, Colony


class Header:
    def __init__(self, parent, names):
        self.labels = [tk.Label(master=parent, text=name, relief=tk.RAISED)
                       for name in names]


class SpinBox(tk.Spinbox):
    def __init__(self, parent, upper_limit):
        self.text_variable = tk.StringVar(value=upper_limit)
        tk.Spinbox.__init__(self, master=parent, from_=0, to=upper_limit,
                            textvariable=self.text_variable,
                            state='readonly')

        self.bind('<Enter> e', lambda event: self.invoke('buttonup'))
        self.bind('<Enter> d', lambda event: self.invoke('buttondown'))


class BuildQueue(tk.OptionMenu):
    def __init__(self, parent, colony):
        self.colony = colony
        self.text_variable = tk.StringVar(value="tradeGoods")
        tk.OptionMenu.__init__(
            self,
            parent,
            self.text_variable,
            *colony.avail_buildings,
        )
        self.configure(takefocus=True)

    def update_choices(self):
        self['menu'].delete(0, 'end')
        for building in self.colony.avail_buildings:
            self['menu'].add_command(
                label=building,
                command=tk._setit(self.text_variable, building)
            )

        if self.colony.build_queue is None:
            self.text_variable.set('tradeGoods')
            self['state'] = 'normal'


class ColonyRow:
    def __init__(self, parent, colony):
        self.name_label = tk.Label(master=parent, text=colony.name.capitalize(),
                                   relief=tk.RAISED)

        self.farmers_spinbox = SpinBox(parent,
                                       colony.num_farmers + colony.unassigned)

        self.workers_spinbox = SpinBox(parent,
                                       colony.num_workers + colony.unassigned)

        self.scientists_spinbox = SpinBox(parent,
                                          colony.num_scientists + colony.unassigned)

        self.unassigned_label = tk.Label(
            master=parent,
            text=colony.unassigned,
            relief=tk.RAISED
        )

        self.build_queue = BuildQueue(parent, colony)

        self.buy_button = tk.Button(master=parent, text='Buy')

        self.spinboxes = [self.farmers_spinbox, self.workers_spinbox,
                          self.scientists_spinbox
                          ]

        self.row = [self.name_label, *self.spinboxes, self.unassigned_label,
                    self.build_queue, self.buy_button
                    ]


# class for displaying information from a game or colony object
class InfoLabel(tk.Label):
    def __init__(self, parent, object):
        tk.Label.__init__(self, master=parent, text=self.text(object),
                          relief=tk.RAISED, anchor=tk.N)

    @staticmethod
    def text(object):
        pass

    def update_label(self, object):
        self.configure(text=self.text(object))


class ColonyInfo1(InfoLabel):
    @staticmethod
    def text(colony):
        cost = Colony.building_data[colony.build_queue].cost

        output = (f"Selected: {colony.name.capitalize()}\n"
                  f"Climate: {colony.climate.capitalize()}\n"
                  f"Size: {colony.size.capitalize()}\n"
                  f"Gravity: {colony.gravity.capitalize()}\n"
                  f"Mineral Richness: {colony.mineral_richness.capitalize()}\n"
                  f"Population: {colony.cur_pop}\n"
                  f"Max Pop: {colony.max_pop}\n"
                  f"{colony.raw_pop % 1000} + {colony.pop_increment}\n"
                  f"{colony.stored_prod}/{cost} + {colony.prod}")
        return output


class ColonyInfo2(InfoLabel):
    @staticmethod
    def text(colony):
        output = (f"Selected: {colony.name.capitalize()}\n"
                  f"Food: {colony.food}\n"
                  f"Imported Food: {colony.imported_food}\n"
                  f"Production: {colony.prod}\n"
                  f"Pollution: {colony.pollution_penalty}\n"
                  f"Research: {colony.rp}\n"
                  f"Net BC: {colony.bc}\n"
                  f"Morale: {colony.morale_multiplier}\n"
                  )
        return output


class ColonyInfo3(InfoLabel):
    @staticmethod
    def text(colony):
        buildings = []
        for building, is_built in colony.buildings.items():
            if (is_built and building
                    not in ['terraforming', 'gaiaTransformation']):
                buildings.append(building)

        output = '\n'.join(['Buildings:'] + buildings)
        return output


class GameInfo(InfoLabel):
    @staticmethod
    def text(game):
        return (
            f'Turn: {game.turn_count}\n'
            f"Reserve: {game.reserve} \n"
            f"Income: {game.bc} \n"
            f"Population: {game.population}\n"
            f"Freighters: ({game.avail_freighters}) {game.num_freighters}\n"
            f"Food: {game.food} \n"
            f"Research: {game.rp}"
        )


class ResearchFieldInfo(InfoLabel):
    @staticmethod
    def text(game):
        output = ''
        if game.res_queue is not None:
            buildings = game.res_queue.buildings
            if buildings:
                output += '\n'.join(['Buildings:'] + buildings) + '\n\n'
            else:
                output += 'Buildings: \n None \n\n'

            achievements = game.res_queue.achievements
            if achievements:
                output += '\n'.join(['Achievements:'] + achievements) + '\n\n'
            else:
                output += 'Achievements: \n None \n\n'

        else:
            output += ('Buildings: \n None \n\n'
                       'Achievements:\n None')

        return output


class ResearchInfo(tk.Frame):
    def __init__(self, parent, game):
        tk.Frame.__init__(self, master=parent, bd=1, relief=tk.RAISED)

        self.game = game
        self.researching = tk.Label(master=self, text=self.researching_text())

        self.researching.pack(side='top')

        self.text_variable = tk.StringVar()
        self.research_choice = tk.OptionMenu(
            self,
            self.text_variable,
            *game.tech_tree
        )

        self.research_choice.pack(side='top')

        self.progress = tk.Label(master=self, text=self.progress_text())

        self.progress.pack(side='top')

    def researching_text(self):
        if self.game.res_queue is not None:
            return f'Researching: {self.game.res_queue.field}{self.game.res_queue.level}'
        else:
            return 'Researching: None'

    def progress_text(self):
        if self.game.res_queue is not None:
            return f'Progress: {self.game.stored_rp}/{2 * self.game.res_queue.cost}'
        else:
            return f'Progress: {self.game.stored_rp}/None'

    def update_labels(self):
        self.researching.configure(text=self.researching_text())
        self.progress.configure(text=self.progress_text())

    def update_menu(self):
        menu = self.research_choice['menu']
        menu.delete(0, 'end')
        for field in self.game.avail_tech_fields:
            menu.add_command(
                label=field,
                command=tk._setit(self.text_variable, field)
            )
        if len(self.game.avail_tech_fields) > 0:
            self.text_variable.set(self.game.avail_tech_fields[0])
        else:
            self.text_variable.set('')


class GUI(tk.Tk):
    def __init__(self, game):
        tk.Tk.__init__(self)
        self.header = Header(self, ['Name', 'Farmers', 'Workers',
                                    'Scientists', 'Unassigned', 'Building', ''])

        self.game = game
        self.colony_selected = game.colonies[0]

        # create header
        for i, label in enumerate(self.header.labels):
            label.grid(row=0, column=i, sticky=tk.W + tk.E + tk.N + tk.S)

        # create a row for each colony
        self.colony_rows = [ColonyRow(self, c) for c in game.colonies]

        # put colony rows on grid
        for i, colony_row in enumerate(self.colony_rows, start=1):
            for j, widget in enumerate(colony_row.row):
                widget.grid(row=i, column=j,
                            sticky=tk.W + tk.E + tk.N + tk.S)

        self.last_row_index = len(game.colonies) + 1

        # info labels
        self.colony_info1 = ColonyInfo1(self, game.colonies[0])

        self.colony_info2 = ColonyInfo2(self, game.colonies[0])

        self.colony_info3 = ColonyInfo3(self, game.colonies[0])

        self.research_field_info = ResearchFieldInfo(self, game)

        self.research_info = ResearchInfo(self, game)

        self.game_info = GameInfo(self, game)

        # turn button
        self.turn_button = tk.Button(master=self, text='T\nU\nR\nN')

        self.last_row = [
            self.colony_info1, self.colony_info2, self.colony_info3,
            self.research_field_info, self.research_info, self.game_info,
            self.turn_button
        ]

        # place last row on grid
        for i, info_window in enumerate(self.last_row):
            info_window.grid(row=self.last_row_index, column=i,
                             sticky=tk.W + tk.E + tk.N + tk.S)

        # set bindings

        # Whenever the mouse enters a different colony row,
        # the colony info labels display information for that row's
        # colony.
        for num, colony_row in enumerate(self.colony_rows):
            for widget in colony_row.row:
                widget.bind(
                    '<Enter>',
                    lambda event, num=num: self.colony_row_callback(event, num)
                )

        # bind the t-key to the turn button
        self.bind('t', self.turn)

        # This causes the keyboard focus to follow the mouse
        self.bind_all(
            '<Enter>',
            lambda event: self.nametowidget(event.widget).focus()
        )

        # set traces/ commands

        # These traces cause the game objects build_que to change
        # when the gui's build_menu changes and invokes the
        # the game objects buy_production method when the one of
        # buy_buttons is pressed in a colony row.
        for i, row in enumerate(self.colony_rows, start=1):
            row.build_queue.text_variable.trace(
                "w",
                lambda x, y, z, num=i: self.set_build_menu(x, y, z, num)
            )

            row.buy_button.configure(
                command=lambda num=i: self.buy_production(num)
            )

        # Ties the turn_button to the turn function defined below
        self.turn_button.configure(command=self.turn)

        # trace for research info label,
        # causes the game's research_queue attribute to change as
        # the gui's research_choice optionmenu changes.
        self.research_info.text_variable.trace(
            'w',
            self.set_research_queue
        )

        # spinbox validation
        vcmd = self.register(self.spinbox_callback)
        for i, colony_row in enumerate(self.colony_rows, start=1):
            for j, spinbox in enumerate(colony_row.spinboxes):
                spinbox.configure(
                    validate='key',
                    validatecommand=(vcmd, '%P', '%s', i, j)
                )

        self.mainloop()

    def colony_row_callback(self, event, num):
        c = self.game.colonies[num]

        self.colony_selected = c
        self.colony_info1.update_label(c)
        self.colony_info2.update_label(c)
        self.colony_info3.update_label(c)

    def set_build_menu(self, x, y, z, num):
        var = self.colony_rows[num - 1].build_queue.text_variable

        if var.get() != '':
            c = self.game.colonies[num - 1]
            c.build_queue = var.get()
            self.game_info.update_label(self.game)

            if c == self.colony_selected:
                self.colony_info1.update_label(c)

    def set_research_queue(self, x, y, z):
        var = self.research_info.text_variable.get()
        if var == '':
            self.game.res_queue = None
        else:
            self.game.res_queue = Game.tech_tree[var][game.tech_tree_positions[var]]
        self.research_info.update_labels()
        self.research_field_info.update_label(game)

    def buy_production(self, num):
        c = self.game.colonies[num - 1]
        if c.build_queue in ['tradeGoods', 'housing']:
            return

        build_menu = self.colony_rows[num - 1].build_queue

        if (build_menu['state'] == 'normal' and
                self.game.production_cost(c, c.build_queue) <= self.game.reserve):
            self.game.buy_production(c)
            self.game_info.update_label(self.game)

            if c == self.colony_selected:
                self.colony_info1.update_label(c)

            build_menu.configure(state='disabled')

    def spinbox_callback(self, P, s, row_num, spin_num):
        row_num = int(row_num)
        spin_num = int(spin_num)
        cur_value = int(s)
        new_value = int(P)

        colony = self.game.colonies[row_num - 1]

        # update colony attributes
        if spin_num == 0:
            colony.num_farmers = new_value
            game.distribute_food()
        elif spin_num == 1:
            colony.num_workers = new_value
        else:
            colony.num_scientists = new_value

        # update info labels
        self.colony_info1.update_label(self.colony_selected)
        self.colony_info2.update_label(self.colony_selected)
        self.game_info.update_label(self.game)

        spinboxes = self.colony_rows[row_num - 1].spinboxes
        unassigned_label = self.colony_rows[row_num - 1].unassigned_label
        cur_spinbox = spinboxes[spin_num]

        # if value of spinbox decreases, increase value of unassigned and
        # increase range of other spinboxes
        if new_value < cur_value:
            for spinbox in spinboxes:
                if spinbox != cur_spinbox:
                    spinbox['to'] += 1
            unassigned_label['text'] += 1

        # if value of spinbox increases, decrease value fo unassigned and
        # decrease range of the other spinboxes
        if new_value > cur_value:
            for spinbox in spinboxes:
                if spinbox != cur_spinbox:
                    spinbox['to'] -= 1
            unassigned_label['text'] -= 1

        return True

    def turn(self, event=None):
        self.turn_button.focus()
        cond1 = any(colony.unassigned for colony in self.game.colonies)
        cond2 = (self.research_info.text_variable.get() == ''
                 and len(game.avail_tech_fields) > 0
                 )

        if cond1 or cond2:
            return

        self.game.turn()

        # update spinboxes, optionmenus in colony rows
        for colony, colony_row in zip(self.game.colonies, self.colony_rows):
            # temporarily deactivate spinbox validation
            for spinbox in colony_row.spinboxes:
                spinbox['validate'] = 'none'

            # if population of colony increased, update it's unassigned label,
            # and increase the range of its spinboxes
            if colony.cur_pop > colony.prev_pop:
                colony_row.unassigned_label['text'] = colony.unassigned
                for spinbox in colony_row.spinboxes:
                    spinbox['to'] += colony.unassigned

            # if the population of the colony decreased, decrease the spinbox
            # values until they sum to the colony's population
            attributes = ['num_farmers', 'num_workers', 'num_scientists']
            if colony.cur_pop < colony.prev_pop:
                for spinbox, attr in zip(colony_row.spinboxes, attributes):
                    spinbox['to'] = getattr(colony, attr)
                    spinbox.text_variable.set(getattr(colony, attr))

            # reactivate spinbox validation
            for spinbox in colony_row.spinboxes:
                spinbox['validate'] = 'key'

            if colony.build_queue is None:
                colony_row.build_queue.update_choices()

        if self.game.res_queue is None:
            self.research_info.update_menu()

            for colony_row in self.colony_rows:
                colony_row.build_queue.update_choices()

        # update info windows
        self.colony_info1.update_label(self.colony_selected)
        self.colony_info2.update_label(self.colony_selected)
        self.colony_info3.update_label(self.colony_selected)
        self.research_info.update_labels()
        self.game_info.update_label(self.game)

        self.game.distribute_food()


# Initialize game object

p1 = Planet('huge', 'abundant', 'normal', 'terran')
c1 = Colony(p1, 'colony1', 2, 2, 2,
            ['automatedFactory', 'hydroponicFarm', 'biospheres'])

p2 = Planet('huge', 'abundant', 'normal', 'terran')
c2 = Colony(p2, 'colony2', 2, 2, 2,
            ['automatedFactory', 'hydroponicFarm', 'biospheres'])

p3 = Planet('huge', 'abundant', 'normal', 'terran')
c3 = Colony(p3, 'colony3', 2, 2, 2,
            ['automatedFactory', 'hydroponicFarm', 'biospheres'])


# starting positions for each research field
starting_tech = [('const', 6), ('chem', 2), ('soc', 2), ('comp', 3),
                 ('bio', 2)]

game = Game(starting_tech, [c1, c2, c3])

# Initialize GUI
gui = GUI(game)
