# PyRota
A GUI rota scheduler for Python 3

## Prerequisites
This program requires Python 3, as well as the module tkcalendar.
To install tkcalendar: `pip install tkcalendar` on the command line of your chosen OS.

## User guide
### Start menu
When the program is started, an options menu appears. Here, you can choose to create a new rota or open an existing rota. When a rota is created, a database (.db) file is created in the same directory as the program, and given the name entered by the user. This is also the name which must be used in order to open an existing rota.

### Employee menu
Once a rota has been created/opened, or when the `Employees` button is pressed, you are greeted with the employee menu. There are two elements to this window, the 'add employee' section, and the 'view/edit' section:
#### Add employee
`EmployeeID`: Unique employee identifier, can contain any characters

`First Name`: Employee's first name

`Last name`: Employee's last name

`Job role`: Employee's job title. NOTE: Employees must be given a job role before they can be created. Their job role CANNOT be 'None'. To create a job role, please see 'Company menu' below.

`Holiday remaining (days)`: The number of days holiday the employee has accrued. Must be a whole number.

`Min.hours/week`: The minimum number of hours to rota in the employee for.

`Employee availability`: Opens a pop-up window, where you are able to select the days of the week that each employee is available.
#### View/edit
The view/edit section is used to edit or delete existing employees in the rota. Existing employees are displayed in the listbox when present, and once an employee is selected you have the option to edit the employee's attributes or remove them.

### Company menu
Accessed by pressing the `Company` button.
#### Staff required each day
This section allows you to create up to three unique shift patterns for the total number of staff required for each day of the week. This is optional, and allows you to match the number of staff with the average weekly demand trends for your business. If you are not open 7 days a week, simply set closing days to have 0 employees.
#### Job roles
This section allows you to add new job roles. The `Min. working staff` option allows you to set a minimum number of employees with that job role to work every day. If this is not necessary, simply set this option to 0. Job roles can also be edited/deleted in the same fashion as employees using the listbox and buttons provided.

### Holiday menu
Accessed by pressing the `Holidays` button.
#### Holiday calendar
In the holiday menu, there is an interactive calendar, giving a simple visual interface to view upcoming employee holidays. Dates on the calendar can be selected and edited, and up to 5 employees can be on hoiday on any given date. When an employee books off a block of days, the `Add holiday` button can be used to set a start/end date for the employee's holiday and add it to the calendar.
