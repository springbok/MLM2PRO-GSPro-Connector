from src.non_blocking_input import NonBlockingInput
from src.ui import Color, UI

class Menu:
    def __init__(self):
        self.menu_options = {
            'M': 'Display Menu',
            'R': 'Reset ROI',
            'C': 'Reset GSPRO connection',
            'Q': 'Exit',
        }

    def display(self):
        for key in self.menu_options.keys():
            print(key, '--', self.menu_options[key])

    def run(self):
        soptions = ', '.join(map(str, list(self.menu_options.keys())))
        option = ''
        try:
            print(f'Enter one of these choices ({soptions}):')
            non_blocking_input = NonBlockingInput(exit_condition='Q')
            done_processing = False
            input_str = ""
            while not done_processing:
                if non_blocking_input.input_queued():
                    input_str = non_blocking_input.input_get()
                    if input_str.strip() == non_blocking_input.exit_condition:
                        done_processing = True
                    else:
                        print("{}".format(input_str))
            option = input(f'Enter one of these choices ({soptions}): ').upper()
        except:
            UI.display_message(Color.RED, "", 'Wrong input. Please enter a valid option, press M top display menu')
        if option == 'Q':
            # shutdown_main()
            exit()
        elif option == 'M':
            self.display()
        elif option == 'R':
            i=1
            #try:
            #    obtain_rois(True)
            #except Exception as e:
            #    print_colored_prefix(Color.RED, "Image Processing ||", "An error occurred: {}".format(e))
        else:
            UI.display_message(Color.RED, "", "Invalid option. Please enter a valid option: " + soptions)
