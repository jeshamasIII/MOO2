# This gui has two purposes. First to make debugging the game logic easier.
# Second to allow a human to create benchmarks for the game-tree search
# by manually completing games.

import tkinter as tk
import tkinter.font as tkFont
from GameClass import Game
from BuildingDataDictionary import building_data


class Header:
    def __init__(self, parent, names, font):
        self.labels = []
        for name in names:
            self.labels.append(
                tk.Label(master=parent, text=name, relief=tk.RAISED, font=font)
            )


class ColonistSpinBox(tk.Spinbox):
    def __init__(self, parent, upper_limit, colonist_type, font):
        self.colonist_type = colonist_type
        self.value = tk.IntVar(value=upper_limit)
        self.previous_value = self.value.get()

        tk.Spinbox.__init__(self, master=parent, from_=0, to=upper_limit,
                            textvariable=self.value, state='readonly',
                            font=font)

        self.bind('e', lambda event: self.invoke('buttonup'))
        self.bind('d', lambda event: self.invoke('buttondown'))


class BuildQueue(tk.OptionMenu):
    def __init__(self, parent, colony, font):
        self.colony = colony
        self.text_variable = tk.StringVar(value="tradeGoods")

        tk.OptionMenu.__init__(
            self,
            parent,
            self.text_variable,
            *colony.available_buildings,
        )
        self.configure(takefocus=True, font=font)
        self['menu'].configure(font=font)

    def update_choices(self):
        self['menu'].delete(0, 'end')
        for building in self.colony.available_buildings:
            self['menu'].add_command(
                label=building,
                command=tk._setit(self.text_variable, building)
            )

        if self.colony.build_queue is None:
            self.text_variable.set('tradeGoods')
            # self.colony.build_queue = 'tradeGoods'
            self['state'] = 'normal'


class ColonyRow:
    def __init__(self, parent, colony, font):
        self.colony = colony

        self.name_label = tk.Label(
            master=parent,
            text=colony.name.capitalize(),
            relief=tk.RAISED,
            font=font
        )

        self.farmers_spinbox = ColonistSpinBox(
            parent=parent,
            upper_limit=colony.num_farmers + colony.unassigned,
            colonist_type='farmer',
            font=font
        )

        self.workers_spinbox = ColonistSpinBox(
            parent=parent,
            upper_limit=colony.num_workers + colony.unassigned,
            colonist_type='worker',
            font=font
        )

        self.scientists_spinbox = ColonistSpinBox(
            parent=parent,
            upper_limit=colony.num_scientists + colony.unassigned,
            colonist_type='scientist',
            font=font
        )

        self.unassigned_label = tk.Label(
            master=parent,
            text=colony.unassigned,
            relief=tk.RAISED,
            font=font
        )

        self.build_queue = BuildQueue(parent, colony, font=font)

        self.buy_button = tk.Button(master=parent, text='Buy', font=font)

        self.spinboxes = [self.farmers_spinbox, self.workers_spinbox,
                          self.scientists_spinbox
                          ]

        self.row_order = [self.name_label, *self.spinboxes,
                          self.unassigned_label, self.build_queue,
                          self.buy_button
                          ]

    def __iter__(self):
        return iter(self.row_order)


# class for displaying information for a game or colony object
class UpdatableInfoLabel(tk.Label):
    def __init__(self, parent, object, font):
        tk.Label.__init__(self, master=parent, text=self.text(object),
                          relief=tk.RAISED, anchor=tk.N, font=font)

    @staticmethod
    def text(object):
        pass

    def update_label(self, object):
        self.configure(text=self.text(object))


class ColonyInfo1(UpdatableInfoLabel):
    @staticmethod
    def text(colony):
        building = colony.build_queue
        if building == 'terraforming':
            building_cost = 250 * (1 + colony.terraform_count)
        else:
            building_cost = building_data[building].cost

        output = (
            f"{colony.name.capitalize()} \n\n"
            f"Climate: {colony.climate.capitalize()}\n"
            f"Size: {colony.size.capitalize()}\n"
            f"Gravity: {colony.gravity.capitalize()}\n"
            f"Mineral Richness: {colony.mineral_richness.capitalize()}\n"
            f"Population: {colony.current_population} M\n"
            f"Max Pop: {colony.max_population} M\n"
            f"Pop Growth: {colony.raw_population % 1000}k + {colony.population_increment}k\n"
            f"Stored Prod / Building Cost + Prod: {colony.stored_production}/{building_cost} + {colony.production}"
        )
        return output


class ColonyInfo2(tk.Frame):
    def __init__(self, parent):
        self.parent = parent
        tk.Frame.__init__(self, master=parent)

        self.widgets = [
            tk.Label(master=self),
            tk.Label(master=self),
            tk.Button(master=self, command=lambda: FoodVariables(parent),
                      height=2),
            tk.Label(master=self, relief=tk.RAISED),
            tk.Button(master=self, command=lambda: ProductionVariables(parent)),
            tk.Button(master=self, command=lambda: Pollution(parent)),
            tk.Button(master=self, command=lambda: RpVariables(parent)),
            tk.Button(master=self, command=lambda: BcVariables(parent)),
            tk.Button(master=self, command=lambda: Morale(parent))
        ]

        for widget in self.widgets:
            widget.configure(font=parent.custom_font, height=1,
                             anchor=tk.N)
            widget.pack(fill=tk.X)

        self.update_label()

    def update_label(self):
        colony = self.parent.colony_row_selected.colony
        strings = [
            f"{colony.name.capitalize()}",
            "",
            f"Food: {colony.food}\n",
            f"Imported Food: {colony.imported_food}\n",
            f"Production: {colony.production}\n",
            f"Pollution: {colony.production_variables['pollution_penalty']}\n",
            f"Research: {colony.rp}\n",
            f"Net BC: {colony.bc}\n",
            f"Morale: {colony.morale_multiplier}\n"
        ]

        for label, string in zip(self.widgets, strings):
            label.configure(text=string)


class ColonyInfo3(UpdatableInfoLabel):
    @staticmethod
    def text(colony):
        buildings = []
        for building, is_built in colony.buildings.items():
            if (is_built and building
                    not in ['terraforming', 'gaiaTransformation']):
                buildings.append(building)

        output = (f"{colony.name.capitalize()} \n\n"
                  + '\n'.join(['Buildings Completed:'] + buildings))
        return output


class GameInfo(UpdatableInfoLabel):
    @staticmethod
    def text(game):
        return (
            f'Turn: {game.turn_count}\n'
            f"Reserve: {game.reserve} \n"
            f"Income: {game.bc} \n"
            f"Population: {game.population}\n"
            f"Freighters: ({game.available_freighters}) {game.total_freighters}\n"
            f"Food: {game.food} \n"
            f"Research: {game.rp}"
        )


class ResearchFieldInfo(UpdatableInfoLabel):
    @staticmethod
    def text(game):
        output = ''

        output += 'Research Field Info \n\n'

        if game.research_queue is not None:

            output += (game.research_queue.field
                       + str(game.research_queue.level)
                       + '\n\n')

            buildings = game.research_queue.buildings
            if len(buildings) > 0:
                output += '\n'.join(['Buildings:'] + buildings) + '\n\n'
            else:
                output += 'Buildings: \n None \n\n'

            achievements = game.research_queue.achievements
            if len(achievements) > 0:
                output += '\n'.join(['Achievements:'] + achievements) + '\n\n'
            else:
                output += 'Achievements: \n None \n\n'

        else:
            output += ('Buildings: \n None \n\n'
                       'Achievements:\n None')

        return output


class ResearchChoicesInfo(tk.Frame):
    def __init__(self, parent, game, font):
        tk.Frame.__init__(self, master=parent, bd=1, relief=tk.RAISED)

        self.game = game
        self.researching = tk.Label(master=self, text=self.researching_text(),
                                    font=font)

        self.researching.pack()

        self.text_variable = tk.StringVar()
        self.research_choice = tk.OptionMenu(
            self,
            self.text_variable,
            *game.tech_tree
        )
        self.research_choice.configure(font=font)
        self.research_choice['menu'].configure(font=font)

        self.research_choice.pack()

        self.progress = tk.Label(master=self, text=self.progress_text(),
                                 font=font)

        self.progress.pack()

        self.achievements_completed = tk.Label(
            master=self,
            text=self.achievements_completed_text(),
            font=font
        )
        self.achievements_completed.pack()

    def researching_text(self):
        if self.game.research_queue is not None:
            return ('Researching: '
                    + self.game.research_queue.field
                    + str(self.game.research_queue.level))
        else:
            return 'Researching: None'

    def progress_text(self):
        if self.game.research_queue is not None:
            return ('Progress: '
                    + str(self.game.stored_rp) + '/'
                    + str(int(1.5 * self.game.research_queue.rp_cost)))
        else:
            return f'Progress: {self.game.stored_rp}/None'

    def achievements_completed_text(self):
        text = "\n\n Achievements Completed: \n\n"

        for achievement, is_researched in self.game.achievements.items():
            if is_researched:
                text += achievement + "\n"

        return text

    def update_labels(self):
        self.researching.configure(text=self.researching_text())
        self.progress.configure(text=self.progress_text())
        self.achievements_completed.configure(text=self.achievements_completed_text())

    def update_menu(self):
        menu = self.research_choice['menu']
        menu.delete(0, 'end')
        for field in self.game.available_tech_fields:
            menu.add_command(
                label=field,
                command=tk._setit(self.text_variable, field)
            )
        if len(self.game.available_tech_fields) > 0:
            self.text_variable.set(self.game.available_tech_fields[0])
        else:
            self.text_variable.set('')


class PopUpWindow:
    def __init__(self, parent):
        self.window = tk.Toplevel()
        self.game = parent.game
        self.colony = parent.colony_row_selected.colony
        self.label = tk.Label(
            master=self.window,
            text=self.update_text(),
            relief=tk.RAISED,
            justify='left',
            font=parent.custom_font
        )
        self.label.pack()
        self.window.mainloop()

    def update_text(self):
        pass


class BcVariables(PopUpWindow):
    def update_text(self):
        self.colony.bc
        variables = self.colony.bc_variables

        output = (
            f"{self.colony.name.capitalize()} \n\n"
            f"+{variables['taxes_collected']} \t Taxes Collected \n"
            f"+{variables['morale_bonus']} \t Morale Bonus \n"
            f"+{variables['spaceport_bonus']} \t Spaceport \n"
            f"+{variables['stock_exchange_bonus']} \t Stock Exchange \n"
            f"+{variables['currency_exchange_bonus']} \t Currency Exchange \n"
            f"+{variables['government_bonus']} \t Government Bonus \n"
            f"+{variables['tradegoods']} \t Tradegoods \n"
            f"-{variables['maintenance_cost']} \t Maintenance Cost \n"
            f"-{variables['climate_cost']} \t Climate Cost \n\n"
        )

        sign = '+' if self.colony.bc >= 0 else '-'
        output += sign + f"{self.colony.bc} \t Net BC \n"

        return output


class RpVariables(PopUpWindow):
    def update_text(self):
        self.colony.rp
        variables = self.colony.rp_variables

        output = (
            f"{self.colony.name.capitalize()} \n\n"
            f"+{variables['base_research']} \t Base RP \n"
            f"+{variables['astro_university']} \t Astro University \n"
            f"+{variables['heightened_intelligence']} \t Heightened Intelligence \n"
            f"+{variables['research_lab']} \t Research Lab \n"
            f"+{variables['supercomputer']} \t Super Computer \n"
            f"+{variables['galactic_cybernet']} \t Galactic Cybernet \n"
            f"+{variables['morale_bonus']} \t Morale Bonus \n"
            f"+{variables['government_bonus']} \t Government Bonus \n"
            f"-{variables['gravity_penalty']} \t Gravity Penalty \n"
            f"+{variables['research_lab_building']} \t Research Lab \n"
            f"+{variables['supercomputer_building']} \t Super Computer \n"
            f"+{variables['autolab_building']} \t Autolab \n"
            f"+{variables['galactic_cybernet_building']} \t Galactic Cybernet \n\n"
            f"+{self.colony.rp} \t Total RP \n"
        )
        return output


class FoodVariables(PopUpWindow):
    def update_text(self):
        self.colony.food
        variables = self.colony.food_variables

        output = (
            f"{self.colony.name.capitalize()} \n\n"
            f"+{variables['base_food_from_farmers']} \t Base Food From Farmers \n"
            f"+{variables['soil_enrichment']} \t Soil Enrichment \n"
            f"+{variables['biomorphic_fungi']} \t Biomorphic Fungi \n"
            f"+{variables['weather_controller']} \t Weather Controller \n"
            f"+{variables['astro_university']} \t Astro University \n"
            f"+{variables['moral_bonus']} \t Moral Bonus \n"
            f"-{variables['gravity_penalty']} \t Gravity Penalty \n"
            f"+{variables['hydroponic_farm']} \t Hydroponic Farm \n"
            f"+{variables['subterranean_farm']} \t Subterranean Farm \n"
            f"-{self.colony.current_population} \t Colony Population \n\n"
        )

        sign = '+' if self.colony.food >= 0 else ''
        output += sign + f"{self.colony.food} \t Net Food \n"

        return output


class ProductionVariables(PopUpWindow):
    def update_text(self):
        self.colony.production
        variables = self.colony.production_variables

        output = (
            f"{self.colony.name.capitalize()} \n\n"
            f"+{variables['base_worker_production']} \t Base Worker Production \n"
            f"+{variables['astro_university']} \t Astro University \n"
            f"+{variables['microlite_construction']} \t Microlite Construction \n"
            f"+{variables['automated_factory']} \t Automated Factory \n"
            f"+{variables['robominer_plant']} \t Robominer Plant \n"
            f"+{variables['deep_core_mine']} \t Deep Core Mine \n"
            f"-{variables['gravity_penalty']} \t Gravity Penalty \n"
            f"+{variables['morale_bonus']} \t Morale Bonus \n"
            f"+{variables['robotic_factory']} \t Robotic Factory \n"
            f"-{variables['pollution_penalty']} \t Pollution Penalty \n"
            f"+{variables['automated_factory_building']} \t Automated Factory Building \n"
            f"+{variables['robominer_plant_building']} \t Robominer Plant Building \n"
            f"+{variables['deep_core_mine_building']} \t Deep Core Mine Building \n"
            f"+{variables['recyclotron']} \t Recyclotron \n\n"
            f"+{self.colony.production} \t Total Production \n"
        )

        return output


class Pollution(PopUpWindow):
    def update_text(self):
        self.colony.production
        variables = self.colony.production_variables
        nano_disasemblers = self.game.achievements['nanoDisassemblers']

        if self.colony.buildings['coreWasteDump']:
            output = (
                f"{self.colony.name.capitalize()} \n\n"
                "0 \t Total Pollution"
            )
        else:
            output = (
                f"{self.colony.name.capitalize()} \n\n"
                f"{nano_disasemblers} \t Nano Disassemblers \n\n"

                f"{variables['polluting_production']} \t Polluting Production \n"
                f"{variables['pollution_reduction_multiplier']} \t Pollution Reduction Multiplier \n"
                f"{self.colony.planet_pollution_tolerance} \t Planet Pollution Tolerance \n\n"

                f"{variables['pollution_penalty']} \t Pollution Penalty \n"
            )

        return output


class Morale(PopUpWindow):
    def update_text(self):
        output = (
            f"+{.2 * self.colony.buildings['holoSimulator']} \t Holo Simulator \n"
            f"+{.3 * self.colony.buildings['pleasureDome']} \t Pleasure Dome \n"
            f"+{.2 * self.game.achievements['realityNetwork']} \t Virtual Reality Network \n\n"
            f"{self.colony.morale_multiplier} \t Morale Multiplier \n"
        )

        return output


class GUI(tk.Tk):
    def __init__(self, game):
        tk.Tk.__init__(self)

        self.title(string='MOO2 GUI')
        self.custom_font = tkFont.Font(family="consolas", size=9)

        self.game = game

        header_names = ['Name', 'Farmers', 'Workers', 'Scientists',
                        'Unassigned', 'Building', '']
        self.header = Header(self, header_names, font=self.custom_font)

        for column_number, label in enumerate(self.header.labels):
            label.grid(row=0, column=column_number,
                       sticky=tk.W + tk.E + tk.N + tk.S)

        self.colony_rows = [ColonyRow(self, colony, font=self.custom_font)
                            for colony in game.colonies]

        self.colony_row_selected = self.colony_rows[0]

        for row_number, colony_row in enumerate(self.colony_rows, start=1):
            for column_number, widget in enumerate(colony_row):
                widget.grid(row=row_number, column=column_number,
                            sticky=tk.W + tk.E + tk.N + tk.S)

        self.last_row_index = len(game.colonies) + 1

        # info labels
        self.colony_info1 = ColonyInfo1(
            self,
            game.colonies[0],
            font=self.custom_font
        )

        self.colony_info2 = ColonyInfo2(
            self,
        )

        self.colony_info3 = ColonyInfo3(
            self,
            game.colonies[0],
            font=self.custom_font
        )

        self.research_field_info = ResearchFieldInfo(
            self,
            game,
            font=self.custom_font
        )

        self.research_info = ResearchChoicesInfo(
            self,
            game,
            font=self.custom_font
        )

        self.game_info = GameInfo(
            self,
            game,
            font=self.custom_font
        )

        # turn button
        self.turn_button = tk.Button(master=self, text='T\nU\nR\nN',
                                     font=self.custom_font)

        self.last_row = [
            self.colony_info1, self.colony_info2, self.colony_info3,
            self.research_field_info, self.research_info, self.game_info,
            self.turn_button
        ]

        for column_number, info_window in enumerate(self.last_row):
            info_window.grid(row=self.last_row_index, column=column_number,
                             sticky=tk.W + tk.E + tk.N + tk.S)

        # set bindings

        # Whenever the mouse enters a different colony row,
        # the colony info labels display information for that row's
        # colony.
        for colony_row in self.colony_rows:
            for widget in colony_row:
                widget.bind(
                    '<Enter>',
                    lambda event, x=colony_row: self.select_colony_row(event, x)
                )
        # bind the t-key to the turn button
        self.bind('t', lambda event: self.turn())

        # This binding causes the keyboard focus to follow the mouse
        self.bind_all(
            '<Enter>',
            lambda event: self.nametowidget(event.widget).focus()
        )

        # ask for quiting application
        self.protocol("WM_DELETE_WINDOW", self.prevent_close)

        # set traces/ commands

        for colony, colony_row in zip(self.game.colonies, self.colony_rows):
            colony_row.build_queue.text_variable.trace(
                "w",
                lambda w, x, y, z=colony: self.set_build_queue(w, x, y, z)
            )

            colony_row.buy_button.configure(command=self.buy_production)

        # Ties the turn_button to the turn method
        self.turn_button.configure(command=self.turn)

        # trace for research info label,
        # causes the game's research_queue attribute to change as
        # the gui's research_choice optionmenu changes.
        self.research_info.text_variable.trace(
            'w',
            self.set_research_queue
        )

        # spinbox command
        for colony_row in self.colony_rows:
            for spinbox in colony_row.spinboxes:
                spinbox.configure(
                    command=lambda x=spinbox: self.update_spinbox(x)
                )

        self.mainloop()

    def select_colony_row(self, event, colony_row):
        if event.state != 1:
            self.colony_row_selected = colony_row

            self.colony_info1.update_label(colony_row.colony)
            self.colony_info2.update_label()
            self.colony_info3.update_label(colony_row.colony)

    def set_build_queue(self, w, x, y, colony):
        text_variable = self.colony_row_selected.build_queue.text_variable
        colony.build_queue = text_variable.get()

        if colony == self.colony_row_selected.colony:
            self.colony_info1.update_label(colony)
            self.game_info.update_label(self.game)

    def set_research_queue(self, x, y, z):
        field_name = self.research_info.text_variable.get()
        if field_name == '':
            self.game.research_queue = None
        else:
            position = self.game.tech_tree_positions[field_name]
            self.game.research_queue = Game.tech_tree[field_name][position]

        self.research_info.update_labels()
        self.research_field_info.update_label(self.game)

    def buy_production(self):
        colony = self.colony_row_selected.colony
        if colony.build_queue in ['tradeGoods', 'housing']:
            return

        build_menu = self.colony_row_selected.build_queue

        if (build_menu['state'] == 'normal' and
                self.game.production_cost(colony, colony.build_queue)
                <= self.game.reserve):
            self.game.buy_production(colony)
            self.game_info.update_label(self.game)
            self.colony_info1.update_label(colony)
            build_menu.configure(state='disabled')

    def update_spinbox(self, selected_spinbox):
        colony = self.colony_row_selected.colony

        # update colony attributes
        if selected_spinbox.colonist_type == 'farmer':
            colony.num_farmers = selected_spinbox.value.get()
            self.game.distribute_food()
        elif selected_spinbox.colonist_type == 'worker':
            colony.num_workers = selected_spinbox.value.get()
        elif selected_spinbox.colonist_type == 'scientist':
            colony.num_scientists = selected_spinbox.value.get()

        # update info labels
        self.colony_info1.update_label(colony)
        self.colony_info2.update_label()
        self.game_info.update_label(self.game)

        # Update the ranges of the other spinboxes and update the unassigned
        # label.
        spinboxes = self.colony_row_selected.spinboxes
        unassigned_label = self.colony_row_selected.unassigned_label

        if selected_spinbox.value.get() < selected_spinbox.previous_value:
            for spinbox in spinboxes:
                if spinbox != selected_spinbox:
                    spinbox['to'] += 1
            unassigned_label['text'] += 1

        if selected_spinbox.value.get() > selected_spinbox.previous_value:
            for spinbox in spinboxes:
                if spinbox != selected_spinbox:
                    spinbox['to'] -= 1
            unassigned_label['text'] -= 1

        selected_spinbox.previous_value = selected_spinbox.value.get()

    def prevent_close(self):
        window = tk.Toplevel()
        label = tk.Label(master=window, font=self.custom_font,
                         text="Are you sure you want to quit?")
        label.pack()

        yes_button = tk.Button(master=window, font=self.custom_font,
                               text="Yes", command=self.destroy)
        yes_button.pack()

        no_button = tk.Button(master=window, font=self.custom_font,
                              text="No", command=window.destroy)
        no_button.pack()

        window.bind('y', lambda event: self.destroy())
        window.bind('n', lambda event: window.destroy())

        window.mainloop()

    def turn(self):
        self.turn_button.focus()

        cond1 = any(colony.unassigned for colony in self.game.colonies)
        cond2 = (self.research_info.text_variable.get() == ''
                 and len(self.game.available_tech_fields) > 0)
        if cond1 or cond2:
            return

        self.game.turn()

        # update spinboxes and optionmenus in colony rows
        for colony, colony_row in zip(self.game.colonies, self.colony_rows):

            # if population of colony increased, update it's unassigned label,
            # and increase the range of its spinboxes
            if colony.current_population > colony.previous_population:
                colony_row.unassigned_label['text'] = colony.unassigned
                for spinbox in colony_row.spinboxes:
                    spinbox['to'] += colony.unassigned

            # if the population of the colony decreased,
            if colony.current_population < colony.previous_population:
                for spinbox in colony_row.spinboxes:
                    if spinbox.colonist_type == 'farmer':
                        number_of_colonists = colony.num_farmers

                    elif spinbox.colonist_type == 'worker':
                        number_of_colonists = colony.num_workers

                    elif spinbox.colonist_type == 'scientist':
                        number_of_colonists = colony.num_scientists

                    spinbox['to'] = number_of_colonists
                    spinbox.value.set(number_of_colonists)

            if colony.build_queue is None:
                colony_row.build_queue.update_choices()

        if self.game.research_queue is None:
            self.research_info.update_menu()

            for colony_row in self.colony_rows:
                colony_row.build_queue.update_choices()

        # update info windows
        colony_selected = self.colony_row_selected.colony
        self.colony_info1.update_label(colony_selected)
        self.colony_info2.update_label()
        self.colony_info3.update_label(colony_selected)
        self.research_info.update_labels()
        self.game_info.update_label(self.game)

        self.game.distribute_food()
