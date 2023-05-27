# Transaction Manager

Transaction Manager is a web application developed using Django, HTML, Bootstrap, jQuery, Jinja, and SQLite. It is designed to help maintain and track transactions of a group of people on a duration basis. Each member of the group can add transactions for others but not for themselves.

## Features

- User registration and authentication
- User roles: admin and member
- Admin can manage groups and members
- Members can view transactions of the group
- Members can add transactions for others (excluding themselves)
- Transactions are categorized by duration (e.g., daily, weekly, monthly)
- Transaction details include date, description, amount, and payer
- Dashboard with an overview of transactions
- Search functionality for transactions
- Responsive design using Bootstrap

## Installation

To run the Transaction Manager application locally, follow these steps:

1. Clone the repository:

   ```shell
   $ git clone https://github.com/your-username/transaction-manager.git
   $ cd transaction-manager
   ```

2. Create a virtual environment:

   ```shell
   $ python3 -m venv env
   $ source env/bin/activate
   ```

3. Install the required dependencies:

   ```shell
   $ pip install -r requirements.txt
   ```

4. Set up the database:

   ```shell
   $ python manage.py migrate
   ```

5. Create a superuser (admin account):

   ```shell
   $ python manage.py createsuperuser
   ```

6. Start the development server:

   ```shell
   $ python manage.py runserver
   ```

7. Access the application by visiting `http://localhost:8000` in your web browser.

## Usage

1. Register a new user account or log in as the admin with the superuser account.
2. Create a group and add members to it.
3. As an admin, manage group details and member assignments.
4. As a member, view transactions of the group.
5. To add a transaction, navigate to the "Add Transaction" page and fill in the details (excluding yourself as the payer).
6. View and search transactions on the dashboard.

## Technology Stack

The Transaction Manager application is built using the following technologies:

- Django: A Python web framework for rapid development and clean design.
- HTML: The standard markup language for creating web pages.
- Bootstrap: A popular CSS framework for building responsive and mobile-first websites.
- jQuery: A fast, small, and feature-rich JavaScript library.
- Jinja: A templating engine for Python used to generate dynamic HTML pages.
- SQLite: A lightweight, file-based database management system.

## Contributing

Contributions are welcome! If you'd like to contribute to the Transaction Manager project, please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and commit them with descriptive messages.
4. Push your changes to your forked repository.
5. Submit a pull request explaining your changes.

Please ensure that your code adheres to the existing coding style and includes relevant tests.

## License

The Transaction Manager application is open-source software licensed under the [MIT License](LICENSE). Feel free to use, modify, and distribute it as per the terms of the license.

## Contact

If you have any questions, suggestions, or issues, please contact the project maintainer at [sandeepkumargalipelly@gmail.com](mailto:sandeepkumargalipelly@gmail.com).

--- 
# Version Docs
### Version 1.6
- added remove member in group view with confirm button
- added admin static files

### Version 1.7.0
- added few UI improvements
- added loading animation
#### 1.7.1
- made changes to the loading animation
- added few UI improvements
