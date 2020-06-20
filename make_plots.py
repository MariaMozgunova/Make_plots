import os

import matplotlib.pyplot as plt

from progressBar import printProgressBar


class MakePlots():
    def __init__(self, path, save_path, end_date, start_date=''):
        self.path = path
        self.save_path = save_path
        self.start_date = start_date
        self.end_date = end_date
        self.time = []
        self.data = [
            ['P_O2|atm', []],
            ['P_He|atm', []],
            ['Flow O2|l/min', []],
            ['Flow He|l/min', []],
            ['FiO2 Env|%', []],
            ['FiO2 sens2|%', []],
            ['P mask|cm H2O', []],
            ['Tmask|gradC', []], 
            ['Tnagr|gradC', []], 
            ['V|ml', []],
            ['f|1/min', []], 
            ['Tzad|gradC', []],
            ['FiO2 zad|%', []] 
        ]
        self.param = range(13)

    def choose_from_data(self, param):
        """Determins on which parameters to make plots."""
        if param:
            choice = {
                '1': [0, 2, 4, 5, 12],
                '2': [1, 3],
                '3': [7, 8, 11],
                '4': [6, 9, 10]
            }[param]
            self.param = choice

    def add_info(self, info):
        """Adds new information from each string."""
        self.time.append(int(info[0]))
        for i in self.param:
            if (i in [7, 8]) and (info[i + 1] == '135'):
                self.data[i][1].append(0)
                continue

            if i in [0, 1]:
                info[i+1] = int(info[i+1]) * 10

            self.data[i][1].append(int(info[i + 1]))

    def clean_data(self, new_path):
        """Makes plots on the specific time."""
        for i in self.param:
            fig, axis = plt.subplots( nrows=1, ncols=1 )
            axis.plot(self.time, self.data[i][1])
            new_names = self.data[i][0].split('|')
            plt.ylabel(new_names[1])
            plt.xlabel("seconds")
            fig.savefig(os.path.join(new_path, (new_names[0] + '.png')))
            plt.close(fig)
            self.data[i][1] = []
        self.time = []

    def not_valid(self, date):
        """Checks, whether the date of the file is appropriate, if given."""
        if self.start_date <= date <= self.end_date:
            return False
        return True

    def progress(self, i, l, filename):
        """Prints the progress of processing the files."""
        printProgressBar(
            i,
            l,
            prefix = f"Working on the file: {filename}. Progress:",
            suffix = 'Complete',
            length = 50
        )  

    def open_all(self):

        """
        Opens all the files in the given path.
        Sends every line with information to self.add_info.
        """

        l = len(os.listdir(self.path)) 
        i = 0
        for filename in os.listdir(self.path):
            date = filename.split(".")[0]
            if self.start_date and self.not_valid(date):
                i += 1
                continue

            self.progress(i, l, filename)  
            date = "_".join([date[6:], date[4:6], date[0:4]])
            with open(os.path.join(self.path, filename), 'r') as file:
                need_clean = False
                os.makedirs(os.path.join(self.save_path, date))
                
                for line in file:
                    if "# time;" in line:
                        continue
                    
                    if "# POW" in line:

                        if need_clean:
                            self.clean_data(
                                os.path.join(self.save_path, date, time)
                            )

                        need_clean = False
                        time = "`".join(line[21:-1].split(':'))
                        os.makedirs(os.path.join(self.save_path, date, time))                        
                        continue
                    need_clean = True
                    line = line.split(';')

                    if len(line) != 16:
                        continue
                    
                    self.add_info(line[:14])

                if need_clean:
                    self.clean_data(os.path.join(self.save_path, date, time))
                    
                file.close()
                i += 1 
                
        self.progress(i, l, filename)


if __name__ == "__main__":
    path_to_logs = input("Enter the absolute path to logs: ")
    path_plots = input("Enter the absolute path to existing " +
                        "dir where to save plots: ")
    print()
    start_date = input("*Optional. You can enter start date " + 
                "(required format - year month day, without separators): ")
    if start_date:
        end_date = input("*Required. Please enter end date " +  
                "(required format - year month day, without separators): ")
    else:
        end_date = ''
    
    print()
    print("*Optional. Enter the number of parameter: ")
    print("1. All information about O2;")
    print("2. All information about He;")
    print("3. Everything related to the temperature;")
    print("4. Pressure in mask, input volume, frequency of input.")
    param = input()
    not_valid = True
    
    while param and not_valid:
        try:
            int(param)
            not_valid = False
        except:
            param = input("You need to enter a number between 1 and 4: ")

    print()

    new_plots = MakePlots(path_to_logs, path_plots, end_date, start_date)
    new_plots.choose_from_data(param)
    new_plots.open_all()