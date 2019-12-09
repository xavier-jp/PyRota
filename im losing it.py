from tkinter import *
from tkinter import messagebox
import tkinter.ttk as ttk
import sqlite3 as sql
from sqlite3 import Error
from os import remove
from tkcalendar import Calendar
from tkcalendar import DateEntry as TkcDateEntry
from datetime import datetime, timedelta
from ast import literal_eval
################################################################################
class DateEntry(TkcDateEntry):
    def _setup_style(self, event=None):
        # override problematic method to implement fix
        self.style.layout('DateEntry', self.style.layout('TCombobox'))
        self.update_idletasks()
        conf = self.style.configure('TCombobox')
        if conf:
            self.style.configure('DateEntry', **conf)
        # The issue comes from the line below:
        maps = self.style.map('TCombobox')
        if maps:
            try:
                self.style.map('DateEntry', **maps)
            except TclError:
                # temporary fix to issue #61: manually insert correct map
                maps = {'focusfill': [('readonly', 'focus', 'SystemHighlight')],
                        'foreground': [('disabled', 'SystemGrayText'),
                                       ('readonly', 'focus', 'SystemHighlightText')],
                        'selectforeground': [('!focus', 'SystemWindowText')],
                        'selectbackground': [('!focus', 'SystemWindow')]}
                self.style.map('DateEntry', **maps)
        try:
            self.after_cancel(self._determine_downarrow_name_after_id)
        except ValueError:
            # nothing to cancel
            pass
        self._determine_downarrow_name_after_id = self.after(10, self._determine_downarrow_name)
################################################################################
class Window:
    def __init__(self, root):
        self.root = root
        self.window = Frame(self.root)
        self.window.pack()

        self.label, self.button, self.entry = [], [], []
        self.titleFont = ('Impact Bold', 32)
        self.subFont = ('Impact Bold', 17)
        self.font = ('Impact Bold', 13, 'bold')
        self.smallFont = ('Impact Bold', 11, 'bold')

    def close(self):
        self.window.destroy()

    def connect(self, dbName): #Initialises a connection to the .db file specified by the user. If there is an internal SQL error, False is returned and an error message is displayed.
        if dbName[-3:] != '.db':
            dbName += '.db'
        self.dbName = dbName

        try:
            connection = sql.connect(dbName)
            return connection
        except Error:
            return False

    def query(self, sqlCode): #Used for SQL SELECT statements. Returns the results of the query.
        cursor = self.connection.cursor()
        cursor.execute(sqlCode)
        return cursor.fetchall()

    def execute(self, sqlCode): #Used for SQL CREATE/INSERT statements. Commits the changes to the database.
        cursor = self.connection.cursor()
        cursor.execute(sqlCode)
        self.connection.commit()

    def startMenu(self):
        self.close()
        self.app = StartMenu(self.root)

    def mainMenu(self, connection, dbName):
        self.close()
        self.app = MainMenu(self.root, connection, dbName)

    def generateEmployeeEntries(self): #Creates widgets required for creating/editing employees, used by Window and Popup subclasses.
        labels = ['Employee ID:', 'First name:', 'Last name:', 'Job role:', 'Holiday remaining (days):', 'Min. hours/week:', 'Employee availability:']

        for label in range(1, len(labels)+1):
                self.label.append(Label(self.window, text=labels[label-1], font=self.font))
                self.label[-1].grid(row=label+3, column=1)

                if label != len(labels):
                    if label != 4:
                        self.entry.append(Entry(self.window))
                        self.entry[-1].config(font=self.font)
                        self.entry[-1].grid(row=label+3, column=3)
                else:
                    self.button.append(Button(self.window, text='Set...', font=self.font, command=self.editAvailability))
                    self.button[-1].grid(row=label+3, column=3, sticky=W)
                if label == 4:
                    jobRoles = ['None']

                    roleQuery = self.query('SELECT JobRole FROM JobRoles')
                    if roleQuery != []:
                        for jobRole in roleQuery:
                            jobRoles.append(jobRole[0])

                    self.roleVar = StringVar(self.window)
                    self.roleVar.set('None')
                    self.popupMenu = OptionMenu(self.window, self.roleVar, *jobRoles)
                    self.popupMenu.grid(row=label+3, column=3)

    def editAvailability(self): #Opens the EditAvailability() popup window. If the user has not filled out all employee entries, an error message will display.
        check = True
        for entry in self.entry:
            if entry.get() == '':
                check = False

        if check:
            self.abCheck = True
            EditAvailability(self.connection, self.entry[0].get())
        else:
            messagebox.showerror('Error', 'Please ensure all fields are filled out before attempting to set employee availability!')
################################################################################
class Popup(Window):
    def __init__(self):
        self.window = Tk()
        self.window.resizable(False, False)
        self.window.title('PyRota')

        self.label, self.button, self.entry = [], [], []
        self.titleFont = ('Impact Bold', 32)
        self.subFont = ('Impact Bold', 17)
        self.font = ('Impact Bold', 13, 'bold')
        self.smallFont = ('Impact Bold', 11, 'bold')
################################################################################
class StartMenu(Window):
    def __init__(self, root):
        super(StartMenu, self).__init__(root)
        self.label.append(Label(self.window, text='PyRota', font=self.titleFont))
        self.label.append(Label(self.window, text='Please choose one of the following options:\n', font=self.subFont))

        self.button.append(Button(self.window, text='Start new rota schedule', font=self.font, command=self.createRota))
        self.button.append(Button(self.window, text='Open existing rota schedule', font=self.font, command=self.openRota))
        self.button.append(Button(self.window, text='Quit', font=self.font, command=root.destroy))

        for label in self.label:
            label.pack()
        for button in self.button:
            button.config(height='3')
            button.pack(fill=X)

    def createRota(self):
        self.close()
        self.app = CreateRota(self.root)

    def openRota(self):
        self.close()
        self.app = OpenRota(self.root)
################################################################################
class CreateRota(Window):
    def __init__(self, root):
        super(CreateRota, self).__init__(root)
        self.label.append(Label(self.window, text='Enter a name for your new rota database:\n', font=self.subFont))
        self.label[0].pack()

        self.entry.append(Entry(self.window))
        self.entry[0].config(font=self.font)
        self.entry[0].pack()

        self.button.append(Button(self.window, text='OK', font=self.font, command=self.create))
        self.button.append(Button(self.window, text='Cancel', font=self.font, command=self.startMenu))

        for button in self.button:
            button.config(height='3')
            button.pack(fill=X)

    def create(self): #Checks for the existence of the file specified by the user. If it does not exist, it is created, and the tables are created within the file.
        if self.entry[0].get() == '':
            messagebox.showerror('Error', 'Please enter a name for your new database!')
        else:
            self.connection = self.connect(self.entry[0].get())
            tables = self.query("SELECT name FROM sqlite_master WHERE type='table';")
            if str(tables) != '[]':
                messagebox.showerror('Error', 'Database already exists!')
            else:
                if not self.connection:
                    self.entry[0].delete(0, END)
                    messagebox.showerror('Error', 'Unable to create the database file!')
                else:
                    tables = \
                            [""" CREATE TABLE IF NOT EXISTS Employees (
                                EmployeeID text PRIMARY KEY NOT NULL,
                                FirstName text NOT NULL,
                                LastName text NOT NULL,
                                JobRole text NOT NULL,
                                HolidayLeft integer NOT NULL,
                                MinHours integer
                            ); """,
                            """ CREATE TABLE IF NOT EXISTS Availability (
                                EmployeeID text PRIMARY KEY NOT NULL,
                                Days integer NOT NULL,
                                FOREIGN KEY (EmployeeID) REFERENCES Employees (EmployeeID)
                            ); """,
                            """ CREATE TABLE IF NOT EXISTS StaffRequired (
                                ShiftPattern PRIMARY KEY NOT NULL,
                                Monday integer,
                                Tuesday integer,
                                Wednesday integer,
                                Thursday integer,
                                Friday integer,
                                Saturday integer,
                                Sunday integer
                            ); """,
                            """ CREATE TABLE IF NOT EXISTS JobRoles (
                                JobRole text PRIMARY KEY NOT NULL,
                                MinStaff integer NOT NULL
                            ); """,
                            """ CREATE TABLE IF NOT EXISTS Holidays (
                                Date text PRIMARY KEY NOT NULL,
                                Employee1 text DEFAULT 'None',
                                Employee2 text DEFAULT 'None',
                                Employee3 text DEFAULT 'None',
                                Employee4 text DEFAULT 'None',
                                Employee5 text DEFAULT 'None',
                                FOREIGN KEY (Employee1) REFERENCES Employees (EmployeeID)
                                FOREIGN KEY (Employee2) REFERENCES Employees (EmployeeID)
                                FOREIGN KEY (Employee3) REFERENCES Employees (EmployeeID)
                                FOREIGN KEY (Employee4) REFERENCES Employees (EmployeeID)
                                FOREIGN KEY (Employee5) REFERENCES Employees (EmployeeID)
                            ); """]
                    for table in tables:
                        self.execute(table)
                    self.mainMenu(self.connection, self.dbName)
################################################################################
class OpenRota(Window):
    def __init__(self, root):
        super(OpenRota, self).__init__(root)
        self.label.append(Label(self.window, text='Enter the name of your rota database:\n', font=self.subFont))
        self.label[0].pack()

        self.entry.append(Entry(self.window))
        self.entry[0].config(font=self.font)
        self.entry[0].pack()

        self.button.append(Button(self.window, text='OK', font=self.font, command=self.findDB))
        self.button.append(Button(self.window, text='Cancel', font=self.font, command=self.startMenu))

        for button in self.button:
            button.config(height='3')
            button.pack(fill=X)

    def findDB(self): #Finds the database file specified by the user using self.connect(), and launches the main menu.
        self.connection = self.connect(self.entry[0].get())
        if not self.connection:
            self.entry[0].delete(0, END)
            messagebox.showerror('Error', 'Unable to establish a connection to the database file!')
        elif self.connection == 'pineapple':
            messagebox.showerror('File not found', 'The file name you entered could not be found. Make sure you entered the correct name, and that the database file is in the same folder as the PyRota application.')
        else:
            self.mainMenu(self.connection, self.dbName)

    def connect(self, dbName): #Checks whether the file specified by the user already exists. If not, an error message is displayed when the value 'pineapple' is returned to self.findDB().
        self.connection = super(OpenRota, self).connect(dbName)
        tables = self.query("SELECT name FROM sqlite_master WHERE type='table';")
        if str(tables) == '[]':
            self.connection.close()
            remove(self.dbName)
            return 'pineapple'
        else:
            return self.connection
################################################################################
class MainMenu(Window):
    def __init__(self, root, connection, dbName):
        super(MainMenu, self).__init__(root)
        self.connection = connection
        self.dbName = dbName

        if self.dbName[-3:] == '.db':
            self.dbName = self.dbName[:-3]

        self.label.append(Label(self.window, text=self.dbName, font=self.titleFont))
        self.label[0].grid(row=0, column=2)

        self.button.append(Button(self.window, text='Employees', font=self.font, command=self.employees))
        self.button.append(Button(self.window, text='Company', font=self.font, command=self.company))
        self.button.append(Button(self.window, text='Holidays', font=self.font, command=self.holidays))

        for button in range(3):
            self.button[button].grid(row=button+1, column=0, sticky=W)

        self.button.append(Button(self.window, text='Create rota', font=self.font, command=self.createRota))
        self.button[3].grid(row=1, column=4, sticky=E)

        self.button.append(Button(self.window, text='Quit', font=self.smallFont, command=self.quit))
        self.button[4].grid(row=0, column=0, sticky=NW)

    def quit(self):
        self.connection.close()
        root.destroy()

    def clearFields(self): #Removes all widgets from the window, except the main widgets defined in self.__init__().
        while len(self.label) > 1:
            self.label[-1].grid_remove()
            del self.label[-1]
        while len(self.button) > 5:
            self.button[-1].grid_remove()
            del self.button[-1]
        while len(self.entry) > 0:
            self.entry[-1].grid_remove()
            del self.entry[-1]

        try:
            self.list.destroy()
        except:
            pass
        try:
            self.scrollbar.destroy()
        except:
            pass
        try:
            self.popupMenu.destroy()
        except:
            pass
        try:
            self.calendar.destroy()
        except:
            pass

    def updateList(self, table): #Updates listbox to display entries from table {table}.
        self.list.delete(0, END)
        query = self.query(f'SELECT * from {table}')
        for item in query:
            self.list.insert(END, item)

    def generateListbox(self, Lrow, Lwidth, table):
        self.list = Listbox(self.window, height=6, width=Lwidth, font = self.font)
        self.list.grid(row=Lrow, column = 1, sticky=W)
        self.scrollbar = Scrollbar(self.window)
        self.scrollbar.grid(row=Lrow, column=2, sticky=W)
        self.list.configure(yscrollcommand=self.scrollbar.set)
        self.scrollbar.configure(command=self.list.yview)
        self.updateList(table)

        if Lwidth == 45:
            self.button.append(Button(self.window, text='Edit', font=self.font, command=self.editEmployee))
            self.button[-1].grid(row=Lrow, column=3, sticky=W)
            self.button.append(Button(self.window, text='Delete', font=self.font, command=self.delEmployee))
            self.button[-1].grid(row=Lrow, column=3, sticky=E)
        else:
            self.button.append(Button(self.window, text='Edit', font=self.font, command=self.editJobRole))
            self.button[-1].grid(row=Lrow, column=2)
            self.button.append(Button(self.window, text='Delete', font=self.font, command=self.delJobRole))
            self.button[-1].grid(row=Lrow, column=2, sticky=E)



    def employees(self): #Builds employee editor widgets.
        self.clearFields()
        self.abCheck = False

        self.label.append(Label(self.window, text='Add employee', font=self.subFont))
        self.label[-1].grid(row=3, column=2)
        self.generateEmployeeEntries()
        self.button.append(Button(self.window, text='Add', font=self.font, command=self.addEmployee))
        self.button[-1].grid(row=10, column=3, sticky=E)

        self.label.append(Label(self.window, text='View/edit', font=self.subFont))
        self.label[-1].grid(row=11, column=2)

        self.generateListbox(12, 45, 'Employees')

    def addEmployee(self): #Inserts new employee with details entered by user into Employees table, as long as all fields have been filled and the EmployeeID is not already in use.
        check = True
        for i in range(0, 5):
            if self.entry[i].get() == '' or not self.abCheck or self.roleVar.get() == 'None':
                messagebox.showerror('Error', 'Please ensure all fields are filled out before adding a new employee!')
                check = False
                break

        if check:
            try:
                self.execute(f"""INSERT INTO Employees(EmployeeID, FirstName, LastName, JobRole, HolidayLeft, MinHours)
                                VALUES('{self.entry[0].get()}', '{self.entry[1].get()}', '{self.entry[2].get()}', '{self.roleVar.get()}', {int(self.entry[3].get())}, {int(self.entry[4].get())})""")
                self.updateList('Employees')
                for entry in self.entry:
                    entry.delete(0, END)
            except sql.IntegrityError:
                messagebox.showerror('Error', f"Employee with ID '{self.entry[0].get()}' already exists!")
            except:
                messagebox.showerror('Error', 'Please ensure holiday remaining and min. hours are whole numbers!')

    def editEmployee(self):
        try:
            employee = self.list.get(self.list.curselection())
            EditEmployee(self.connection, employee)
        except TclError:
            pass

    def delEmployee(self):
        try:
            tables = ['Employees', 'Availability']
            for table in tables:
                self.execute(f"""DELETE FROM {table} WHERE EmployeeID = '{self.list.get(self.list.curselection())[0]}'""")
            self.updateList('Employees')
        except TclError:
            pass



    def company(self):
        self.clearFields()

        self.label.append(Label(self.window, text='Staff required each day', font=self.subFont))
        self.label[-1].grid(row=3, column=2)

        self.label.append(Label(self.window, text='Select shift pattern:', font=self.font))
        self.label[-1].grid(row=4, column=1)

        for button in range(3):
            stickies, commands = [W, None, E], [self.selectShiftPattern1, self.selectShiftPattern2, self.selectShiftPattern3]
            self.button.append(Button(self.window, text=str(button+1), font=self.font, command=commands[button]))
            self.button[-1].grid(row=4, column=2, sticky=stickies[button])

        self.label.append(Label(self.window, text='\n\n\n\n\n'))
        self.label[-1].grid(row=4, column=0, sticky=S)

        days = ['Monday:', 'Tuesday:', 'Wednesday:', 'Thursday:', 'Friday:', 'Saturday:', 'Sunday:']
        for day in range(len(days)):
            self.label.append(Label(self.window, text=days[day], font=self.font))
            self.label[-1].grid(row=day+5, column=1)

            self.entry.append(Entry(self.window))
            self.entry[-1].config(font=self.font)
            self.entry[-1].grid(row=day+5, column=2)

        self.selectShiftPattern1()

        self.button.append(Button(self.window, text='Save', font=self.font, command=self.saveStaffRequired))
        self.button[-1].grid(row=12, column=2, sticky=E)

        self.label.append(Label(self.window, text='\nJob roles', font=self.subFont))
        self.label[-1].grid(row=13, column=2)

        entryLabels = ['New job role name:', 'Min. working staff:']
        for label in range(len(entryLabels)):
            self.label.append(Label(self.window, text=entryLabels[label], font=self.font))
            self.label[-1].grid(row=label+14, column=1)

            self.entry.append(Entry(self.window))
            self.entry[-1].config(font=self.font)
            self.entry[-1].grid(row=label+14, column=2)

        self.button.append(Button(self.window, text='Add', font=self.font, command=self.addJobRole))
        self.button[-1].grid(row=16, column=2, sticky=E)

        self.generateListbox(17, 20, 'JobRoles')

    def saveStaffRequired(self):
        check = True
        for entry in range(0, 7):
            try:
                if self.entry[entry].get() == '':
                    messagebox.showerror('Error', 'Please ensure you have entered the staff required for each day!')
                    check = False
                    break
                else:
                    valueErrorer = str(int(self.entry[entry].get()))
            except ValueError:
                check = False
                messagebox.showerror('Error', 'Please ensure you have entered whole numbers in each field!')
                break

        if check:
            presenceCheck = self.query(f"""SELECT Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
                                        FROM StaffRequired WHERE ShiftPattern = {self.shiftPattern}""")
            if presenceCheck != []:
                self.execute(f'DELETE FROM StaffRequired WHERE ShiftPattern = {self.shiftPattern}')
            self.execute(f"""INSERT INTO StaffRequired(ShiftPattern, Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday)
                            VALUES({self.shiftPattern}, {self.entry[0].get()}, {self.entry[1].get()}, {self.entry[2].get()}, {self.entry[3].get()}, {self.entry[4].get()}, {self.entry[5].get()}, {self.entry[6].get()})""")

    def displayShiftPattern(self):
        staffRequired = self.query(f"""SELECT Monday, Tuesday, Wednesday, Thursday, Friday, Saturday, Sunday
                                    FROM StaffRequired WHERE ShiftPattern = {self.shiftPattern}""")
        for entry in range(0, 7):
            self.entry[entry].delete(0, END)
            if staffRequired != []:
                self.entry[entry].insert(0, staffRequired[0][entry])

    def selectShiftPattern1(self):
        self.shiftPattern = 1
        self.displayShiftPattern()

    def selectShiftPattern2(self):
        self.shiftPattern = 2
        self.displayShiftPattern()

    def selectShiftPattern3(self):
        self.shiftPattern = 3
        self.displayShiftPattern()

    def addJobRole(self):
        check = True
        try:
            if self.entry[7].get() == '':
                messagebox.showerror('Error', 'Please enter a name for your new job role!')
                check = False
            if self.entry[8].get() == str(int(self.entry[8].get())):
                pass
            if self.entry[8].get() == '0':
                raise ValueError
        except:
            messagebox.showerror('Error', 'Please enter a whole number greater than or equal to 1 for the minimum staff working!')
            check = False

        if check:
            try:
                presenceCheck = self.query(f'SELECT * FROM JobRoles WHERE JobRole = {self.entry[7].get()}')
                if presenceCheck != []:
                    self.execute(f'DELETE FROM JobRoles WHERE JobRole = {self.entry[7].get()}')
            except:
                pass
            try:
                self.execute(f"""INSERT INTO JobRoles(JobRole, Minstaff)
                                VALUES('{self.entry[7].get()}', {self.entry[8].get()})""")
                self.updateList('JobRoles')
            except sql.IntegrityError:
                messagebox.showerror('Error', f"""Job role '{self.entry[7].get()}' already exists!""")
        for entry in range(-1, -3, -1):
            self.entry[entry].delete(0, END)

    def editJobRole(self):
        try:
            EditJobRole(self.connection, self.list.get(self.list.curselection()))
        except TclError:
            pass

    def delJobRole(self):
        try:
            self.execute(f"""DELETE FROM JobRoles WHERE JobRole = '{self.list.get(self.list.curselection())[0]}'""")
            employeesWithRole = self.query(f"""SELECT EmployeeID FROM Employees WHERE JobRole = '{self.list.get(self.list.curselection())[0]}'""")
            if employeesWithRole != []:
                for employeeID in employeesWithRole[0]:
                    self.execute(f"""UPDATE Employees
                                    SET JobRole = 'None'
                                    WHERE EmployeeID = '{employeeID}'""")
            self.updateList('JobRoles')
        except TclError:
            pass


    def holidays(self):
        self.clearFields()

        self.label.append(Label(self.window, text='Holiday calendar\n', font=self.subFont))
        self.label[-1].grid(row=4, column=2)

        self.calendar = Calendar(self.window, font=self.font)
        date = self.calendar.datetime.today() + self.calendar.timedelta(days=2)
        self.calendar.grid(row=5, column=2)
        self.updateCalendar()

        self.button.append(Button(self.window, text='Add holiday', font=self.font, command=self.addHoliday))
        self.button[-1].grid(row=6, column=2, sticky=W)
        self.button.append(Button(self.window, text='Edit selected day', font=self.font, command=self.editHoliday))
        self.button[-1].grid(row=6, column=2, sticky=E)

    def addHoliday(self):
        try:
            AddHoliday(self.connection)
        except TclError:
            pass

    def editHoliday(self):
        try:
            EditHoliday(self.connection, self.calendar, self.calendar.selection_get())
        except TclError:
            pass

    def updateCalendar(self):
        self.calendar.calevent_remove('all')
        calendarInfo = self.query('SELECT * FROM Holidays')
        for tup in range(len(calendarInfo)):
            calendarInfo[tup] = list(calendarInfo[tup])

        for holidayDate in calendarInfo:
            date = datetime.strptime(holidayDate[0], '%d/%m/%Y').date()
            emptyEmployees = 0

            for i in range(1, 6):
                if holidayDate[i] != 'None':
                    employeeName = self.query(f"SELECT FirstName, LastName FROM Employees WHERE EmployeeID = '{holidayDate[i]}'")[0]
                    self.calendar.calevent_create(date, f'{employeeName[0]} {employeeName[1]} (EmployeeID: {holidayDate[i]}) - Holiday', 'holiday')
        self.calendar.tag_config('holiday', background='red', foreground='yellow')



    def createRota(self):
        self.clearFields()
################################################################################
class EditAvailability(Popup):
    def __init__(self, connection, employeeID):
        super(EditAvailability, self).__init__()
        self.connection = connection
        self.employeeID = employeeID

        days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        self.check = []

        for day in range(len(days)):
            self.check.append(IntVar())
            self.button.append(ttk.Checkbutton(self.window, text=days[day], variable=self.check[day]))
            self.button[day].pack()
            self.button[day].state(['!alternate'])

        availableDays = self.query(f"""SELECT Days FROM Availability WHERE EmployeeID = '{self.employeeID}'""")
        if availableDays != []:
            checkFiller = str(format(availableDays[0][0], '07b'))[::-1]
            for button in range(len(self.button)):
                if int(checkFiller[button]):
                    self.button[button].state(['selected'])

        self.button.append(Button(self.window, text='OK', font=self.smallFont, command=self.ok))
        self.button[-1].pack()

    def ok(self): #Appends available day values to Availability table in the database. Each day of the week is represented in binary to easily read the values back from the table (line 334).
        dayVals = {'Monday':1, 'Tuesday':2, 'Wednesday':4, 'Thursday':8, 'Friday':16, 'Saturday':32, 'Sunday':64}
        valDays = {0:'Monday', 1:'Tuesday', 2:'Wednesday', 3:'Thursday', 4:'Friday', 5:'Saturday', 6:'Sunday'}
        days = 0

        for button in range(len(self.button)-1):
            if self.button[button].instate(['selected']):
                days += dayVals[valDays[button]]
        if not days:
            messagebox.showerror('Error', 'Please select at least 1 day!', master=self.window)
        else:
            presenceCheck = self.query(f"""SELECT * FROM Availability WHERE EmployeeID = '{self.employeeID}'""")

            if presenceCheck != []:
                self.execute(f"""DELETE FROM Availability WHERE EmployeeID = '{self.employeeID}'""")
            self.execute(f"""INSERT INTO Availability(EmployeeID, Days)
                            VALUES('{self.employeeID}', {days})""")
            self.close()
################################################################################
class EditEmployee(Popup):
    def __init__(self, connection, employee):
        super(EditEmployee, self).__init__()
        self.connection = connection
        self.employee = employee

        self.label.append(Label(self.window, text='Edit employee\n', font=self.subFont))
        self.label[-1].grid(row=0, column=1)
        self.generateEmployeeEntries()

        for entry in range(len(self.entry)):
            if entry < 3:
                self.entry[entry].insert(0, self.employee[entry])
            else:
                self.entry[entry].insert(0, self.employee[entry+1])
        self.roleVar.set(self.employee[3])

        self.button.append(Button(self.window, text='OK', font=self.font, command=self.append))
        self.button[-1].grid(row=11, column=3, sticky=W)
        self.button.append(Button(self.window, text='Cancel', font=self.font, command=self.close))
        self.button[-1].grid(row=11, column=3, sticky=E)

    def append(self):
        oldEmployeeInfo = self.query(f"""SELECT * FROM Employees WHERE EmployeeID = '{self.employee[0]}'""")
        self.execute(f"""DELETE FROM Employees WHERE EmployeeID = '{self.employee[0]}'""")

        check = True
        for i in range(0, 5):
            if self.entry[i].get() == '' or self.roleVar.get() == 'None':
                messagebox.showerror('Error', 'Please ensure all fields are filled out before appending an employee!', master=self.window)
                check = False
                break

        if check:
            try:
                self.execute(f"""INSERT INTO Employees(EmployeeID, FirstName, LastName, JobRole, HolidayLeft, MinHours)
                                VALUES('{self.entry[0].get()}', '{self.entry[1].get()}', '{self.entry[2].get()}', '{self.roleVar.get()}', {self.entry[3].get()}, {self.entry[4].get()})""")
                topApp = app
                while True:
                    try:
                        topApp = topApp.app
                    except:
                        break
                topApp.updateList('Employees')
                self.close()

            except sql.OperationalError:
               messagebox.showerror('Error', 'Please ensure holiday remaining and min. hours are whole numbers!', master=self.window)
               self.execute(f"""INSERT INTO Employees(EmployeeID, FirstName, LastName, JobRole, HolidayLeft, MinHours)
                                VALUES('{oldEmployeeInfo[0][0]}', '{oldEmployeeInfo[0][1]}', '{oldEmployeeInfo[0][2]}', '{oldEmployeeInfo[0][3]}', {oldEmployeeInfo[0][4]}, {oldEmployeeInfo[0][5]})""")
################################################################################
class EditJobRole(Popup):
    def __init__(self, connection, jobRole):
        super(EditJobRole, self).__init__()
        self.connection = connection
        self.jobRole = jobRole

        self.label.append(Label(self.window, text='Edit job role', font=self.subFont))
        self.label[-1].grid(row=0, column=2)

        entryLabels = ['Job role name:', 'Min. working staff:']
        for label in range(len(entryLabels)):
            self.label.append(Label(self.window, text=entryLabels[label], font=self.font))
            self.label[-1].grid(row=label+1, column=1)

            self.entry.append(Entry(self.window))
            self.entry[-1].config(font=self.font)
            self.entry[-1].grid(row=label+1, column=3)

        for entry in range(len(self.entry)):
            self.entry[entry].insert(0, self.jobRole[entry])

        self.button.append(Button(self.window, text='OK', font=self.font, command=self.append))
        self.button[-1].grid(row=3, column=3, sticky=W)
        self.button.append(Button(self.window, text='Cancel', font=self.font, command=self.close))
        self.button[-1].grid(row=3, column=3, sticky=E)

    def append(self):
        oldJobRoleInfo = self.query(f"""SELECT * FROM JobRoles WHERE JobRole = '{self.jobRole[0]}'""")
        employeesWithRole = self.query(f"""SELECT EmployeeID FROM Employees WHERE JobRole = '{self.jobRole[0]}'""")
        self.execute(f"""DELETE FROM JobRoles WHERE JobRole = '{self.jobRole[0]}'""")

        try:
            if self.entry[0].get() == '':
                raise ValueError
            self.execute(f"""INSERT INTO JobRoles(JobRole, MinStaff)
                            VALUES('{self.entry[0].get()}', {self.entry[1].get()})""")
            for employeeID in employeesWithRole:
                self.execute(f"""UPDATE Employees
                                SET JobRole = '{self.entry[0].get()}'
                                WHERE EmployeeID = '{employeeID[0]}'""")
            topApp = app
            while True:
                try:
                    topApp = topApp.app
                except:
                   break
            topApp.updateList('JobRoles')
            self.close()

        except sql.OperationalError:
            messagebox.showerror('Error', 'Please enter a whole number for the minimum working staff!', master=self.window)
            self.execute(f"""INSERT INTO JobRoles(JobRole, MinStaff)
                            VALUES('{oldJobRoleInfo[0][0]}', {oldJobRoleInfo[0][1]})""")
        except ValueError:
            messagebox.showerror('Error', 'Please enter a name for the job role!', master=self.window)
            self.execute(f"""INSERT INTO JobRoles(JobRole, MinStaff)
                            VALUES('{oldJobRoleInfo[0][0]}', {oldJobRoleInfo[0][1]})""")
################################################################################
class AddHoliday(Popup):
    def __init__(self, connection):
        super(AddHoliday, self).__init__()
        self.connection = connection
        self.calendar = []
        self.dates = []

        self.label.append(Label(self.window, text='Add holiday\n', font=self.subFont))
        self.label[-1].grid(row=0, column=1)

        labels = ['Select start date:', 'Select end date:']
        for i in range(2):
            self.label.append(Label(self.window, text=labels[i], font=self.font))
            self.label[-1].grid(row=i+1, column=0)

            self.calendar.append(DateEntry(self.window, font=self.font, locale='en_GB', width=15))
            self.calendar[-1].set_date(app.app.app.calendar.selection_get())
            self.calendar[-1].grid(row=i+1, column=3)

        self.label.append(Label(self.window, text='Select employee:', font=self.font))
        self.label[-1].grid(row=3, column=0)

        employeeNames = ['None']
        employeeQuery = self.query('SELECT FirstName, LastName FROM Employees')
        if employeeQuery != []:
            for employeeName in employeeQuery:
                employeeNames.append(employeeName)

        self.employeeVar = StringVar(self.window)
        self.employeeVar.set('None')
        self.popupMenu = OptionMenu(self.window, self.employeeVar, *employeeNames)
        self.popupMenu.grid(row=3, column=3)

        self.button.append(Button(self.window, text='Add', font=self.font, command=self.addHoliday))
        self.button[-1].grid(row=4, column=3, sticky=W)
        self.button.append(Button(self.window, text='Cancel', font=self.font, command=self.close))
        self.button[-1].grid(row=4, column=3, sticky=E)

    def addHoliday(self):
        if self.calendar[1].get_date().year < self.calendar[0].get_date().year:
            raise ValueError
        elif (self.calendar[1].get_date().year == self.calendar[0].get_date().year) and (self.calendar[1].get_date().month < self.calendar[0].get_date().month):
            raise ValueError
        elif (self.calendar[1].get_date().year == self.calendar[0].get_date().year) and (self.calendar[1].get_date().month == self.calendar[0].get_date().month) and (self.calendar[1].get_date().day < self.calendar[0].get_date().day):
            raise ValueError

        delta = self.calendar[1].get_date() - self.calendar[0].get_date()
        for i in range(delta.days + 1):
            self.dates.append(self.calendar[0].get_date() + timedelta(days=i))

        if self.employeeVar.get() == 'None':
            messagebox.showerror('Error', 'Please select an employee!', master=self.window)

        else:
            employeeID = list(self.query(f"""SELECT EmployeeID FROM Employees WHERE FirstName = '{list(literal_eval(self.employeeVar.get()))[0]}' AND LastName = '{list(literal_eval(self.employeeVar.get()))[1]}'""")[0])[0]
            for date in self.dates:
                try:
                    check = list(self.query(f"SELECT * FROM Holidays WHERE Date = '{date.strftime('%d/%m/%Y')}'"))
                    if check != []:
                        check = list(check[0])
                        for employee in range(len(check)):
                            if check[employee] == employeeID:
                                raise ValueError
                            elif check[employee] == 'None':
                                check[employee] = employeeID
                                break
                        self.execute(f"DELETE FROM Holidays WHERE Date = '{date.strftime('%d/%m/%Y')}'")
                        self.execute(f"""INSERT INTO Holidays(Date, Employee1, Employee2, Employee3, Employee4, Employee5)
                                        VALUES('{check[0]}', '{check[1]}', '{check[2]}', '{check[3]}', '{check[4]}', '{check[5]}')""")
                    else:
                        self.execute(f"""INSERT INTO Holidays(Date, Employee1)
                                        VALUES('{date.strftime('%d/%m/%Y')}', '{employeeID}')""")
                except ValueError:
                    continue

            topApp = app
            while True:
                try:
                    topApp = topApp.app
                except:
                   break
            topApp.updateCalendar()
            self.close()
################################################################################
class EditHoliday(Popup):
    def __init__(self, connection, calendar, date):
        super(EditHoliday, self).__init__()
        self.connection = connection
        self.calendar = calendar
        self.date = date.strftime('%d/%m/%Y')

        self.label.append(Label(self.window, text=self.date, font=self.subFont))
        self.label[-1].grid(row=0, column=1)
        self.label.append(Label(self.window, text='Employees on holiday:', font=self.font))
        self.label[-1].grid(row=1, column=1)

        employees = list(self.query('SELECT FirstName, LastName FROM Employees'))
        for employee in range(len(employees)):
            employees[employee] = f'{list(employees[employee])[0]} {list(employees[employee])[1]}'
        employees.insert(0, 'None')

        self.employeeVar = []
        try:
            employeesOnHoliday = list(self.query(f"""SELECT Employee1, Employee2, Employee3, Employee4, Employee5 FROM Holidays WHERE Date = '{self.date}'""")[0])
            for employee in range(len(employeesOnHoliday)):
                try:
                    employeeName = list(self.query(f"""SELECT FirstName, LastName FROM Employees WHERE EmployeeID = '{employeesOnHoliday[employee]}'""")[0])
                    employeesOnHoliday[employee] = f'{employeeName[0]} {employeeName[1]}'
                except:
                    pass
                self.employeeVar.append(StringVar(self.window))
                self.employeeVar[-1].set(employeesOnHoliday[employee])

        except IndexError:
            for employee in range(5):
                self.employeeVar.append(StringVar(self.window))
                self.employeeVar[-1].set('None')

        self.popupMenu = []
        for employeeVar in self.employeeVar:
            self.popupMenu.append(OptionMenu(self.window, employeeVar, *employees))

        self.popupMenu[0].grid(row=2, column=0)
        self.popupMenu[1].grid(row=2, column=2)
        self.popupMenu[2].grid(row=3, column=0)
        self.popupMenu[3].grid(row=3, column=1)
        self.popupMenu[4].grid(row=3, column=2)

        self.button.append(Button(self.window, text='OK', font=self.font, command=self.ok))
        self.button[-1].grid(row=4, column=1, sticky=W)
        self.button.append(Button(self.window, text='Cancel', font=self.font, command=self.close))
        self.button[-1].grid(row=4, column=1, sticky=E)

    def ok(self):
        instances = {}
        for employeeVar in self.employeeVar:
            if employeeVar.get() not in instances and employeeVar.get() != 'None':
                instances[employeeVar.get()] = 1
            elif employeeVar.get() in instances:
                instances[employeeVar.get()] += 1

        check = True
        for instance in instances:
            if instances[instance] > 1:
                check = False

        if not check:
            messagebox.showerror('Error', 'You have selected the same employee twice!', master=self.window)
        else:
            self.execute(f"""DELETE FROM Holidays WHERE Date = '{self.date}'""")

            employeeIDs = []
            for employee in range(len(self.employeeVar)):
                if self.employeeVar[employee].get() != 'None':
                    employeeName = self.employeeVar[employee].get().split()
                    employeeIDs.append(list(self.query(f"""SELECT EmployeeID FROM Employees WHERE FirstName = '{employeeName[0]}' AND LastName = '{employeeName[1]}'""")[0])[0])
                else:
                    employeeIDs.append('None')
            self.execute(f"""INSERT INTO Holidays(Date, Employee1, Employee2, Employee3, Employee4, Employee5)
                            VALUES('{self.date}', '{employeeIDs[0]}', '{employeeIDs[1]}', '{employeeIDs[2]}', '{employeeIDs[3]}', '{employeeIDs[4]}')""")

            topApp = app
            while True:
                try:
                    topApp = topApp.app
                except:
                   break
            topApp.updateCalendar()
            self.close()
################################################################################
def onClosing(): #Creates warning to prevent user from accidentally exiting the program without saving.
    if messagebox.askokcancel('Warning!', 'Are you sure you want to exit? Changes you have made may be lost!'):
        root.destroy()

if __name__ == '__main__':
    root = Tk()
    root.resizable(False, False)
    root.title('PyRota')
    app = StartMenu(root)
    root.protocol("WM_DELETE_WINDOW", onClosing)
    root.mainloop()