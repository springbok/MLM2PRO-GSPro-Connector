from src.ui import Color, UI


class Menu:
    def __init__(self):
        self.menu_options = {
            'M': 'Display Menu',
            'R': 'Reset ROI',
            'C': 'Reset GSPRO connection',
            'Q': 'Exit',
        }

    def __display_menu(self):
        for key in self.menu_options.keys():
            print(key, '--', self.menu_options[key])

    def run(self):
        self.__display_menu()
        option = ''
        try:
            option = input('Enter your choice: ').upper()
        except:
            UI.display_message(Color.RED, "MENU ||", 'Wrong input. Please enter a valid option, press M top display menu')
        if option == 'Q':
            # shutdown_main()
            exit()
        elif option == 'M':
            self.__display_menu()
        elif option == 'R':
            i=1
            #try:
            #    obtain_rois(True)
            #except Exception as e:
            #    print_colored_prefix(Color.RED, "Image Processing ||", "An error occurred: {}".format(e))
        else:
            soptions = ', '.join(map(str, list(self.menu_options.keys())))
            UI.display_message(Color.RED, "MENU ||", "Invalid option. Please enter a valid option: " + soptions)
