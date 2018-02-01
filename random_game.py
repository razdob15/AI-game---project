# Raz's Project 2017/2018

from random import randrange
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.image import Image
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.uix.layout import Layout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scatter import Scatter
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.behaviors import ButtonBehavior
from kivy.uix.button import Button
from kivy.animation import Animation
from kivy.graphics.texture import Texture
from kivy.utils import escape_markup
import time

from itertools import permutations





class ButtonCountry(ButtonBehavior, Image):
    def __init__(self, control, armies_number=0, **kwargs):
        ButtonBehavior.__init__(self)
        Image.__init__(self)

        self.source = 'red.png'
        # Set Background Color
        if True:
            if control == 0:
                self.source = 'green.png'
            elif control == 1:
                self.source = 'red.png'
            elif control == 2:
                self.source = 'blue.png'
            else:
                print "Error: The control is no 0 or 1 or 2 !"

        self.control = control

    # Temporary
    # This Function
    # hows the poses of the buttons....
    '''def on_touch_move(self, touch):

        print "{}, {}".format(int(touch.x), int(touch.y))
        self.pos = (touch.x, touch.y)'''
    ######################################################


class Country(Layout, Image):
    # Class variable
    SIGN = Label(text='^',
                 color=(1, 0, 0, 1),
                 markup=True,
                 size=(50, 50),
                 font_size=30)
    MODE = 'cc'
    """ MODE can be:
    'cc' - for Choose Country
    'csc' - for Choose Side Country (near the chose country)
    'aa' - for Add Armies
    (optional) 'ct' - for Computer Turn """

    NOW_SIDE_COUNTRIES = []
    CHOSE_COUNTRY = None
    TARGET_COUNTRY = None
    # Reset variable at any turn (every time computer finish its turn).
    OCCUPIED_COUNTRIES = []

    def __init__(self, control, side_countries, continent, pos, **kwargs):
        """
        :param control: int, can be only:
            0 for neutral
            1 for computer's control
            2 for user's control
        :param side_countries: list of Countries
        :param continent: int - can be only:
            1 for Africa
            2 for Asia
            3 for Europe
            4 for Australia
            5 for America
        :param pos: Tuple(x, y) - The button pos
        """
        Layout.__init__(self, **kwargs)
        Image.__init__(self, **kwargs)

        # Layout attributes
        self.size = (100, 100)
        self.size_hint = (0.5, 0.5)

        # Country attributes
        self.control = control
        if control == 0:
            self.armies_counter = 2  # randrange(0, 6)
        else:
            self.armies_counter = 5
        if self.control != 2:
            self.armies_counter *= -1
        self.side_countries = side_countries
        self.continent = continent

        # Button Attributes:
        self.button_pos = pos
        self.button_size = (15, 15)
        self.button_is_big = False

        # Text - Number of Armies
        self.armies_counter_label = Label(text=str(self.armies_counter), markup=True,
                                          size=(15, 15), pos=(self.button_pos[0], self.button_pos[1] + 15))
        self.armies_counter_label.color = (0, 10, 1, 1)
        #       color = (Red, Green, Blue, Alpha)

        self.add_widget(self.armies_counter_label)

        # Add btn to the map
        self.btn = ButtonCountry(control=self.control)
        self.btn.bind(on_press=self.country_click)
        self.btn.pos = self.button_pos
        self.btn.size = self.button_size
        self.add_widget(self.btn)

        # User's turn attributes
        self.armies_to_pass = None

    def refresh_armies_counter(self, armies):
        """
        Refreshes the country's armies number, logical and graphics.
        :param armies: the new number of armies
        :return: None
        """
        self.armies_counter = armies
        self.armies_counter_label.text = str(armies)

    def add_armies_to_country(self, armies_to_add):
        """

        :param armies_to_add: Natural Int!! How many armies to add? (get the abs and make it to the correct)
        :return: None
        """
        armies_to_add = abs(armies_to_add)
        if self.control == 2:
            self.refresh_armies_counter(armies=self.armies_counter + armies_to_add)
        else:
            self.refresh_armies_counter(armies=self.armies_counter - armies_to_add)

    def change_button_size_on_the_layout(self, to_big):
        """

        :param (bool) to_big: True - change to big
                        False - Chane to Small
        :return: None
        """

        # If no change needed
        if (to_big and self.button_is_big) or (not to_big and not self.button_is_big):
            return

        # New Button
        temp = ButtonCountry(control=self.control)
        temp.source = self.btn.source
        temp.bind(on_press=self.country_click)

        if self.button_is_big:
            # Decrease the size and change the pos
            temp.size = self.button_size
            temp.pos = self.button_pos
            self.button_is_big = False
        else:
            # Increase the pos and the size
            temp.pos = (self.btn.pos[0] - 10, self.btn.pos[1] - 10)
            temp.size = (28, 28)
            self.button_is_big = True

        # Remove the old button from the layout
        self.remove_widget(self.btn)
        self.btn = temp

        # Add the new button to the layout
        self.add_widget(self.btn, 0)

    def country_click(self, touch):
        """
        Handle all the countries clicks: user's, computer's or natural.
        If all the Countries are small and now, in the user turn he click on his country - this is the the
        CHOSE_COUNTRY which can pass armies from it to its side countries.
        If the country is a SIDE_COUNTRY, so the user can pass his armies from CHOSE_COUNTRY to the current country.

        :param touch: Country button...
        :return: None
        """

        print self.button_pos

        if Country.MODE == 'cc':  # User's turn - (cc = Choose Country)

            # if Country.CHOSE_COUNTRY is None:
            # Before a country has chosen

            if self.btn.control == 2 and self not in Country.OCCUPIED_COUNTRIES:
                # User's country which can attack this turn

                # Change the side countries source to be targets
                for country in self.side_countries:
                    if country.btn.control == 1:
                        country.btn.source = 'x_red.png'
                    elif country.btn.control == 0:
                        country.btn.source = 'x_green.png'
                    elif country.btn.control == 2:
                        country.btn.source = 'arrow_blue.png'

                self.change_button_size_on_the_layout(True)

                Country.CHOSE_COUNTRY = self

                Country.SIGN.pos = (self.button_pos[0] - 20, self.button_pos[1] - 40)
                self.add_widget(Country.SIGN)

                # Change class NOW_SIDE_COUNTRIES to this country's side countries
                Country.NOW_SIDE_COUNTRIES = self.side_countries
                Country.TARGET_COUNTRY = None
                Country.MODE = 'csc'

        elif Country.MODE == 'csc':  # A country was chosen
            if self is Country.CHOSE_COUNTRY:  # This country is the user's chosen country

                # Return all the side countries to the start
                self.change_button_size_on_the_layout(to_big=False)
                for country in self.side_countries:
                    country.change_button_size_on_the_layout(False)

                    # If the menu is visible, remove it
                    if country.armies_to_pass is not None:
                        country.remove_widget(country.armies_to_pass)

                    if country.btn.control == 1:
                        country.btn.source = 'red.png'
                    elif country.btn.control == 0:
                        country.btn.source = 'green.png'
                    elif country.btn.control == 2:
                        country.btn.source = 'blue.png'

                Country.NOW_SIDE_COUNTRIES = []
                Country.CHOSE_COUNTRY = None
                self.remove_widget(Country.SIGN)
                Country.MODE = 'cc'

            else:  # There is a chosen country but it's not this country
                if self in Country.NOW_SIDE_COUNTRIES:  # A side country
                    if self is Country.TARGET_COUNTRY:
                        self.change_button_size_on_the_layout(False)
                        Country.TARGET_COUNTRY = None
                        if Country.CHOSE_COUNTRY.armies_counter > 0:
                            self.remove_widget(self.armies_to_pass)

                    elif not Country.TARGET_COUNTRY:
                        self.change_button_size_on_the_layout(True)
                        Country.TARGET_COUNTRY = self
                        self.add_armies_numbers_gridlayout()

        elif Country.MODE == 'aa' and self.control == 2:
            self.refresh_armies_counter(self.armies_counter + 1)
            Game.refresh_addition_armies(Game.ADDITION_ARMIES - 1)

    def add_armies_numbers_gridlayout(self):
        """
        Add to the side country his options to pass armies to it
        """
        if self.armies_to_pass is not None:
            self.remove_widget(self.armies_to_pass)
        if Country.CHOSE_COUNTRY.armies_counter == 0:
            return

        self.armies_to_pass = GridLayout(cols=Country.CHOSE_COUNTRY.armies_counter + 1,
                                         size=(23 * Country.CHOSE_COUNTRY.armies_counter, 20),
                                         pos=(self.button_pos[0] + 20, self.button_pos[1]))

        for num in xrange(Country.CHOSE_COUNTRY.armies_counter + 1):
            num_button = Button(text=str(num))
            num_button.bind(on_press=self.choose_armies_number)
            self.armies_to_pass.add_widget(num_button)
        self.add_widget(self.armies_to_pass)

    def change_control(self, new_control):
        """

        :param new_control: The new control of self.
        :return: None
        """
        if self.control != new_control:
            if 0 <= new_control <= 2:
                self.control = new_control
                if new_control == 0:
                    self.btn.source = 'green.png'
                elif new_control == 1:
                    self.btn.source = 'red.png'
                elif new_control == 2:
                    self.btn.source = 'blue.png'
            else:
                print 'Input Error  in method: change_control'
        else:
            print 'change_control -> No Change Needed'

    def choose_armies_number(self, button):
        """

        :param button: The button in the gridLayout, symbol to the number of armies the user wants to pass
        :return: None
        """
        if Country.CHOSE_COUNTRY.armies_counter > 0:
            pass_armies = int(button.text)
            Country.CHOSE_COUNTRY.armies_counter -= pass_armies
            self.armies_counter += pass_armies
            if self.control != 2:
                Country.OCCUPIED_COUNTRIES.append(self)
            if self.armies_counter > 0:
                self.control = 2
                self.btn.source = "blue.png"

            Country.CHOSE_COUNTRY.armies_counter_label.text = str(Country.CHOSE_COUNTRY.armies_counter)
            self.armies_counter_label.text = str(self.armies_counter)
            self.add_armies_numbers_gridlayout()


def ext_country(country):
    """
    Helping function to 'ext_countries_in_bloc'
    :param country: Country in bloc.
    :return: If the country has a side country with a different control.
    """
    for side_country in country.side_countries:
        if side_country.control != country.control:
            return True
    return False


def ext_countries_in_bloc(bloc):
    """

    :param bloc: List of Countries.
    :return: All the ext-countries* in the bloc.
                * ext-countries => country in the bloc has a side country with a different control.
    """
    the_ext_counries = list()
    for country in bloc:
        if ext_country(country):
            the_ext_counries.append(country)
    return the_ext_counries


def sum_armies_in_bloc(bloc):
    """

    :param bloc: List of countries... BLOC .
    :return: The sum of the armies in the bloc.
    """
    sum_armies = 0
    for country in bloc:
        sum_armies += country.armies_counter
    return sum_armies


class Game(Layout, Image):
    ARMIES_LABEL = Label(text='0',
                         size=(100, 100),
                         pos=(1100, 770),
                         markup=True,
                         font_size=40,
                         color=(0, 10, 1, 1))
    ADDITION_ARMIES = 5

    def __init__(self):
        Layout.__init__(self)
        Image.__init__(self)
        self.source = 'world_map_draw_the_limit.png'

        self.finish_turn_btn = Button(text='Finish my turn',
                                      size=(180, 30),
                                      pos=(100, 10),
                                      markup=True,
                                      font_size=25)
        self.finish_turn_btn.bind(on_press=self.click_finish_turn)
        self.add_widget(self.finish_turn_btn)

        self.countries_dic = dict()
        self.countries_dic['egypt'] = Country(0, set([]), 1, (620, 495))
        self.countries_dic['usa_east'] = Country(0, set([]), 5, (245, 610))
        self.countries_dic['usa_west'] = Country(0, set([]), 5, (124, 623))
        self.countries_dic['canada'] = Country(0, set([]), 5, (228, 770))
        self.countries_dic['australia'] = Country(1, set([]), 1, (993, 168))
        self.countries_dic['russia_east'] = Country(0, set([]), 2, (689, 708))
        self.countries_dic['russia_west'] = Country(0, set([]), 2, (916, 777))
        self.countries_dic['france'] = Country(0, set([]), 3, (540, 640))
        self.countries_dic['spain'] = Country(0, set([]), 3, (514, 596))
        self.countries_dic['india'] = Country(0, set([]), 2, (799, 481))
        self.countries_dic['middle_east_israel'] = Country(2, set([]), 2, (655, 543))
        self.countries_dic['iran'] = Country(0, set([]), 2, (710, 550))
        self.countries_dic['europe_east'] = Country(0, set([]), 2, (614, 679))
        self.countries_dic['china'] = Country(0, set([]), 2, (868, 583))
        self.countries_dic['mongolia'] = Country(0, set([]), 2, (860, 640))
        self.countries_dic['kazakhstan'] = Country(0, set([]), 2, (750, 650))
        self.countries_dic['mexico'] = Country(1, set([]), 2, (151, 520))
        self.countries_dic['south_america_n'] = Country(0, set([]), 2, (242, 384))
        self.countries_dic['south_america_s'] = Country(0, set([]), 2, (304, 103))
        self.countries_dic['brazil'] = Country(0, set([]), 2, (321, 281))
        self.countries_dic['denmark'] = Country(0, set([]), 2, (613, 779))
        self.countries_dic['algeria'] = Country(0, set([]), 2, (536, 509))
        self.countries_dic['congo'] = Country(0, set([]), 2, (602, 330))
        self.countries_dic['madagascar'] = Country(0, set([]), 2, (690, 228))
        self.countries_dic['south_africa'] = Country(0, set([]), 2, (605, 213))
        self.countries_dic['greenland'] = Country(0, set([]), 2, (487, 846))
        self.countries_dic['chad'] = Country(0, set([]), 2, (585, 436))
        self.countries_dic['indonesia'] = Country(0, set([]), 2, (937, 342))

        self.countries_dic['usa_east'].side_countries.add(self.countries_dic['usa_west'])
        self.countries_dic['usa_west'].side_countries.add(self.countries_dic['usa_east'])
        self.countries_dic['canada'].side_countries.add(self.countries_dic['greenland'])
        self.countries_dic['greenland'].side_countries.add(self.countries_dic['canada'])
        self.countries_dic['mexico'].side_countries.add(self.countries_dic['usa_east'])
        self.countries_dic['usa_east'].side_countries.add(self.countries_dic['mexico'])
        self.countries_dic['mexico'].side_countries.add(self.countries_dic['usa_west'])
        self.countries_dic['usa_west'].side_countries.add(self.countries_dic['mexico'])
        self.countries_dic['canada'].side_countries.add(self.countries_dic['usa_east'])
        self.countries_dic['usa_east'].side_countries.add(self.countries_dic['canada'])
        self.countries_dic['canada'].side_countries.add(self.countries_dic['usa_west'])
        self.countries_dic['usa_west'].side_countries.add(self.countries_dic['canada'])
        self.countries_dic['egypt'].side_countries.add(self.countries_dic['middle_east_israel'])
        self.countries_dic['middle_east_israel'].side_countries.add(self.countries_dic['egypt'])
        self.countries_dic['india'].side_countries.add(self.countries_dic['china'])
        self.countries_dic['china'].side_countries.add(self.countries_dic['india'])
        self.countries_dic['greenland'].side_countries.add(self.countries_dic['denmark'])
        self.countries_dic['denmark'].side_countries.add(self.countries_dic['greenland'])
        self.countries_dic['russia_east'].side_countries.add(self.countries_dic['denmark'])
        self.countries_dic['denmark'].side_countries.add(self.countries_dic['russia_east'])
        self.countries_dic['russia_east'].side_countries.add(self.countries_dic['denmark'])
        self.countries_dic['denmark'].side_countries.add(self.countries_dic['russia_east'])
        self.countries_dic['russia_east'].side_countries.add(self.countries_dic['europe_east'])
        self.countries_dic['europe_east'].side_countries.add(self.countries_dic['russia_east'])
        self.countries_dic['denmark'].side_countries.add(self.countries_dic['europe_east'])
        self.countries_dic['europe_east'].side_countries.add(self.countries_dic['denmark'])
        self.countries_dic['russia_east'].side_countries.add(self.countries_dic['russia_west'])
        self.countries_dic['russia_west'].side_countries.add(self.countries_dic['russia_east'])
        self.countries_dic['algeria'].side_countries.add(self.countries_dic['egypt'])
        self.countries_dic['egypt'].side_countries.add(self.countries_dic['algeria'])
        self.countries_dic['chad'].side_countries.add(self.countries_dic['egypt'])
        self.countries_dic['egypt'].side_countries.add(self.countries_dic['chad'])
        self.countries_dic['algeria'].side_countries.add(self.countries_dic['chad'])
        self.countries_dic['chad'].side_countries.add(self.countries_dic['algeria'])
        self.countries_dic['congo'].side_countries.add(self.countries_dic['chad'])
        self.countries_dic['chad'].side_countries.add(self.countries_dic['congo'])
        self.countries_dic['madagascar'].side_countries.add(self.countries_dic['congo'])
        self.countries_dic['congo'].side_countries.add(self.countries_dic['madagascar'])
        self.countries_dic['south_africa'].side_countries.add(self.countries_dic['congo'])
        self.countries_dic['congo'].side_countries.add(self.countries_dic['south_africa'])
        self.countries_dic['madagascar'].side_countries.add(self.countries_dic['south_africa'])
        self.countries_dic['south_africa'].side_countries.add(self.countries_dic['madagascar'])
        self.countries_dic['madagascar'].side_countries.add(self.countries_dic['australia'])
        self.countries_dic['australia'].side_countries.add(self.countries_dic['madagascar'])
        self.countries_dic['indonesia'].side_countries.add(self.countries_dic['australia'])
        self.countries_dic['australia'].side_countries.add(self.countries_dic['indonesia'])
        self.countries_dic['indonesia'].side_countries.add(self.countries_dic['india'])
        self.countries_dic['india'].side_countries.add(self.countries_dic['indonesia'])
        self.countries_dic['middle_east_israel'].side_countries.add(self.countries_dic['kazakhstan'])
        self.countries_dic['kazakhstan'].side_countries.add(self.countries_dic['middle_east_israel'])
        self.countries_dic['mongolia'].side_countries.add(self.countries_dic['russia_west'])
        self.countries_dic['russia_west'].side_countries.add(self.countries_dic['mongolia'])
        self.countries_dic['mongolia'].side_countries.add(self.countries_dic['china'])
        self.countries_dic['china'].side_countries.add(self.countries_dic['mongolia'])
        self.countries_dic['kazakhstan'].side_countries.add(self.countries_dic['russia_east'])
        self.countries_dic['russia_east'].side_countries.add(self.countries_dic['kazakhstan'])
        self.countries_dic['mongolia'].side_countries.add(self.countries_dic['kazakhstan'])
        self.countries_dic['kazakhstan'].side_countries.add(self.countries_dic['mongolia'])
        self.countries_dic['russia_west'].side_countries.add(self.countries_dic['kazakhstan'])
        self.countries_dic['kazakhstan'].side_countries.add(self.countries_dic['russia_west'])
        self.countries_dic['china'].side_countries.add(self.countries_dic['kazakhstan'])
        self.countries_dic['kazakhstan'].side_countries.add(self.countries_dic['china'])
        self.countries_dic['iran'].side_countries.add(self.countries_dic['middle_east_israel'])
        self.countries_dic['middle_east_israel'].side_countries.add(self.countries_dic['iran'])
        self.countries_dic['china'].side_countries.add(self.countries_dic['iran'])
        self.countries_dic['iran'].side_countries.add(self.countries_dic['china'])
        self.countries_dic['india'].side_countries.add(self.countries_dic['iran'])
        self.countries_dic['iran'].side_countries.add(self.countries_dic['india'])
        self.countries_dic['kazakhstan'].side_countries.add(self.countries_dic['iran'])
        self.countries_dic['iran'].side_countries.add(self.countries_dic['kazakhstan'])
        self.countries_dic['france'].side_countries.add(self.countries_dic['europe_east'])
        self.countries_dic['europe_east'].side_countries.add(self.countries_dic['france'])
        self.countries_dic['france'].side_countries.add(self.countries_dic['spain'])
        self.countries_dic['spain'].side_countries.add(self.countries_dic['france'])
        self.countries_dic['algeria'].side_countries.add(self.countries_dic['spain'])
        self.countries_dic['spain'].side_countries.add(self.countries_dic['algeria'])
        self.countries_dic['mexico'].side_countries.add(self.countries_dic['south_america_n'])
        self.countries_dic['south_america_n'].side_countries.add(self.countries_dic['mexico'])
        self.countries_dic['brazil'].side_countries.add(self.countries_dic['south_america_n'])
        self.countries_dic['south_america_n'].side_countries.add(self.countries_dic['brazil'])
        self.countries_dic['brazil'].side_countries.add(self.countries_dic['south_america_s'])
        self.countries_dic['south_america_s'].side_countries.add(self.countries_dic['brazil'])
        self.countries_dic['south_africa'].side_countries.add(self.countries_dic['south_america_s'])
        self.countries_dic['south_america_s'].side_countries.add(self.countries_dic['south_africa'])
        self.countries_dic['brazil'].side_countries.add(self.countries_dic['congo'])
        self.countries_dic['congo'].side_countries.add(self.countries_dic['brazil'])

        self.add_widget(Game.ARMIES_LABEL)

        # Add all countries to the map
        for country in self.countries_dic.values():
            self.add_widget(country)

        # Countries and their poses
        """
        '''
        self.add_widget(Country(2, [], 1, (620, 495)))  # Egypt
        self.add_widget(Country(1, [], 5, (245, 610)))  # Usa East
        self.add_widget(Country(2, [], 5, (124, 623)))  # USA West
        self.add_widget(Country(0, [], 5, (228, 770)))  # Canada
        self.add_widget(Country(1, [], 1, (993, 168)))  # Australia
        self.add_widget(Country(1, [], 2, (689, 708)))  # Russia East
        self.add_widget(Country(2, [], 2, (916, 777)))  # Russia West
        self.add_widget(Country(0, [], 3, (540, 640)))  # France
        self.add_widget(Country(2, [], 3, (514, 596)))  # Spain
        self.add_widget(Country(0, [], 2, (799, 481)))  # India
        self.add_widget(Country(1, [], 2, (655, 543)))  # Middle East (Israel Area)
        self.add_widget(Country(2, [], 1, (600, 670)))  # Europe East
        self.add_widget(Country(0, [], 2, (868, 583)))  # China
        self.add_widget(Country(0, [], 5, (151, 520)))  # Mexico
        self.add_widget(Country(1, [], 5, (242, 384)))  # South America (N)
        self.add_widget(Country(1, [], 5, (304, 103)))  # South America (S)
        self.add_widget(Country(2, [], 5, (321, 281)))  # Brazil
        self.add_widget(Country(2, [], 3, (613, 779)))  # Denmark
        self.add_widget(Country(1, [], 1, (536, 509)))  # Algeria
        self.add_widget(Country(0, [], 1, (602, 330)))  # Congo
        self.add_widget(Country(0, [], 1, (690, 228)))  # Madagascar
        self.add_widget(Country(0, [], 1, (605, 213)))  # South Africa
        self.add_widget(Country(2, [], 5, (487, 846)))  # Greenland
        self.add_widget(Country(1, [], 1, (585, 436)))  # Chad
        self.add_widget(Country(2, [], 0, (937, 342)))  # Indonesia
        '''

        # 620, 495 - Egypt              V
        # 245, 610 - USA East           V
        # 124, 623 - USA West           V
        # 228, 770 - Canada             V
        # 993, 168 - Australia          V
        # 689, 708 - Russia East        V
        # 916, 777 - Russia West        V
        # 540, 640 - France             V
        # 514, 596 - Spain              V
        # 799, 481 - India              V
        # 655, 543 - Israel area (- Middle East)    V
        # 614, 679 - Europe East        V
        # 868, 583 - China              V
        # 151, 520 - Mexico             V
        # 242, 384 - South America (N)  V
        # 304, 103 - South America (S)  V
        # 321, 281 - Brazil             V
        # 613, 779 - Denmark            V
        # 536, 509 - Algeria            V
        # 602, 330 - Congo              V
        # 690, 228 - Madagascar         V
        # 605, 213 - South Africa       V
        # 487, 846 - Greenland          V
        # 585, 436 - Chad               V
        # 937, 342 - Indonesia          V
        """

    def click_finish_turn(self, touch):
        """
        The user clicks the FINISH button when he finish his turn.
        So, in this function, all the user-turn parameters are initialized.
        :param touch: click on the button...
        :return:
        """

        # Finish User turn:
        if Country.CHOSE_COUNTRY:
            Country.CHOSE_COUNTRY.country_click(0)
        Country.CHOSE_COUNTRY = None
        Country.NOW_SIDE_COUNTRIES = None
        Country.TARGET_COUNTRY = None

        print "user finishes his turn,\nnow computer turn"

        # Start Computer turn:
        Country.MODE = 'ct'  # Computer Turn
        self.computer_turn()

    @staticmethod
    def refresh_addition_armies(number):
        """
        This function refreshes the label which shows the number of armies that the user can share in every turn.
        :param number: number od armies to share between all user's countries
        :return:
        """
        if number == 0:
            Game.ADDITION_ARMIES = 5
            Country.MODE = 'cc'
            Game.ARMIES_LABEL.text = '0'
            return
        Game.ADDITION_ARMIES = number
        Game.ARMIES_LABEL.text = str(number)

    def pass_armies(self, source_country, armies_number, des_country):
        """
        This function passes [armies_number] armies from source_country to des_country

        :param source_country: Country object - from this country the armies is coming
        :param armies_number: int - number of the armies to pass
        :param des_country: Country object - to this country the armies is coming
        :return:
        """

        if armies_number > abs(source_country.armies_counter):
            armies_number = abs(source_country.armies_counter)
        else:  # Input Checking
            armies_number = abs(armies_number)

        if des_country.control == 0:  # Natural country
            if abs(des_country.armies_counter) - armies_number >= 0:
                des_country.refresh_armies_counter(des_country.armies_counter + armies_number)
            else:
                des_country.refresh_armies_counter(-(armies_number - abs(des_country.armies_counter)))
                des_country.change_control(1)

        else:
            des_country.refresh_armies_counter(des_country.armies_counter - armies_number)
            if des_country.control == 2 and des_country.armies_counter < 0:  # Change to computer's control
                des_country.change_control(1)

        source_country.refresh_armies_counter(source_country.armies_counter + armies_number)

        print "Country: {} passed {} armies to country {}".format(self.country_name(source_country).upper(),
                                                                  armies_number, self.country_name(des_country).upper())

    def country_name(self, country):
        """
    
        :param country: Country object in the game. 
        :return: string. Name of the country in the countries_dic.
        """
        for name, c in self.countries_dic.items():
            if country == c:
                return name

    def country_bloc(self, root_country, past_countries=None):
        """

        :param past_countries: The countries which is already in the bloc.
        :param root_country: Country objects, begins the bloc.
        :return: List object, contains all countries in the bloc*. (Included the root country).
                bloc* - list of countries with the same control.
        """

        if past_countries is None:
            past_countries = []
        if root_country.control == 0:
            return [root_country]
        if root_country not in past_countries:
            past_countries.append(root_country)
        the_bloc = past_countries
        for side_country in root_country.side_countries:
            if (side_country not in past_countries) and (side_country.control == root_country.control):
                the_bloc += self.country_bloc(root_country=side_country, past_countries=past_countries)

        return list(set(the_bloc))

    def all_blocs_in_game(self):
        """
        :return: List contains blocs*.
                bloc* - list of countries with the same control.
        """

        all_blocs = list()
        past_countries = list()
        for country in self.countries_dic.values():  # All countries
            if country not in past_countries:
                all_blocs.append(self.country_bloc(root_country=country))  #
                past_countries += self.country_bloc(root_country=country)
        return all_blocs

    def computer_blocs(self):
        """

        :return: List contains the computer's blocs.
        """
        comp_blocs = list()
        for bloc in self.all_blocs_in_game():
            if bloc[0].control == 1:
                comp_blocs.append(bloc)
        return comp_blocs

    def side_blocs(self, bloc):
        """

        :param bloc: List of countries... BLOC .
        :return: All the blocs near the giving bloc.
        """
        the_side_blocs = list()
        for ext_country in ext_countries_in_bloc(bloc=bloc):  # All the ext-countries in the bloc.
            for side_country in ext_country.side_countries:  # All the side countries to the country.
                if side_country.control != ext_country.control:  # The side country not in the bloc.
                    if self.country_bloc(root_country=side_country) not in the_side_blocs:  # if the bloc not exist yet.
                        the_side_blocs.append(self.country_bloc(root_country=side_country))
        return the_side_blocs

    def computer_turn(self):
        """
        Handle the computer turn - The AI
        :return:
        """
        Game.ARMIES_LABEL.text = "Computer Turn"

        print "Checkkkk", sum_armies_in_bloc(
            self.country_bloc(root_country=self.countries_dic['middle_east_israel']))

        self.ai_divide_armies_between_blocs()

        # TODO: Use the ai-functions here !

        # Computer finished his turn.
        print "Computer finishes his turn,\nnow user turn"
        Country.OCCUPIED_COUNTRIES = []
        Country.MODE = 'aa'
        Game.ARMIES_LABEL.text = '5'
        Game.ADDITION_ARMIES = 5

    # TODO : Build The AI!!



    def optins_to_divide(self, armies_to_divide = 5):
        if len(self.computer_blocs()) == 1:
            return [(armies_to_divide)]

        temp = list()
        for x in range(armies_to_divide + 1):
            temp.append(x)

        # Get all permutations of length 2
        # and length 2
        perm = permutations(temp, len(self.computer_blocs()))

        perm = filter(lambda x: sum(x) == 5, perm)
        ''' for i in list(perm):
            print "pppp", i'''


    # AI
    def next_moves_list(self):



        # TODO (1): Create this function !
        pass



    def ai_divide_armies_between_blocs(self, armies_to_divide=5):


        all_score = list()
        current_option = list()

        computer_blocs = self.computer_blocs()
        for option in self.optins_to_divide():
            score = 0
            # TODO - SCORE - Give more score to the ability to conquer more than one country in one tiurn !
            for i in len(option):
                for side_bloc in self.side_blocs(computer_blocs[i]):
                    if sum_armies_in_bloc(side_bloc) < sum_armies_in_bloc(computer_blocs[i]) + option[i]:
                        score += 10
                    elif sum_armies_in_bloc(side_bloc) > sum_armies_in_bloc(computer_blocs[i]) + option[i]:
                        score -= 10


        # TODO - Divide the armies between the correct blocs.



        pass






        for comp_bloc in self.computer_blocs():
            for side_bloc in self.side_blocs(bloc=comp_bloc):
                comp_sum_armis = abs(sum_armies_in_bloc(bloc=comp_bloc))
                side_sum_armis = abs(sum_armies_in_bloc(bloc=side_bloc))

                if comp_sum_armis > side_sum_armis:
                    pass
                else:
                    delta = abs(comp_sum_armis - side_sum_armis) + 1
                    if delta < armies_to_divide:
                        comp_bloc[0].add_armies_to_country(armies_to_add=delta)

    def ai_pass_armies(self):
        for bloc in self.computer_blocs():
            pass


class WarGameApp(App):
    def build(self):
        return Game()


WarGameApp().run()
