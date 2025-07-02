# Almog1 Project Documentation

This document provides an overview of the Almog1 project, a Django-based web application with a robust REST API.

## Project Overview

This project was created by Ali Alfaytouri for Marine Company.

The Almog1 project is a comprehensive system likely designed for e-commerce, inventory management, or a similar business domain. It leverages the Django framework to provide a web interface and a powerful RESTful API for various functionalities. The application is built with a focus on modularity, utilizing several Django applications to manage different aspects of the business.

## Technologies Used

*   **Backend Framework:** Django 4.2.4
*   **Web Server Gateway Interface:** WSGI (for synchronous requests), ASGI (for asynchronous requests with Django Channels)
*   **Database:** MSSQL
*   **API Framework:** Django REST Framework
*   **API Documentation:** drf-spectacular (Swagger UI, ReDoc)
*   **Authentication:** Django REST Framework Simple JWT, Custom Cookie-based Authentication
*   **Asynchronous Tasks:** Celery (with Redis as broker), Django-Q
*   **Real-time Communication:** Django Channels (with Redis as channel layer)
*   **CORS Management:** django-cors-headers
*   **Debugging:** Django Debug Toolbar
*   **Other Libraries:** numpy, pandas, openpyxl, Pillow, python-dateutil, reportlab, etc. (as listed in `requirements.txt`)

## Project Structure and Purpose

The project is organized into several Django applications, each responsible for a specific set of functionalities:

*   **`Almog1` (Core Project):** Contains the main project settings, URL configurations, WSGI/ASGI configurations, and global middleware.
*   **`almogOil`:** This appears to be a core application, handling various business logic, including authentication, custom middleware, notifications, and potentially core data models.
*   **`wholesale_app`:** Likely handles wholesale-specific functionalities, such as pre-orders, product filtering for wholesale clients, and related API endpoints.
*   **`app_sell_invoice`:** Manages functionalities related to sales invoices, including creation, management, reporting, and item handling.
*   **`products`:** Manages product-related data, including product details, categories, models, engines, OEM numbers, and inventory.

The project's directory structure also includes:

*   **`.git/`:** Git version control repository.
*   **`.pytest_cache/`:** Cache directory for pytest.
*   **`logs/`:** Directory for application logs (e.g., `requests.log`).
*   **`media/`:** Stores user-uploaded media files (employee contracts, images, logos, product images).
*   **`node_modules/`:** Contains Node.js dependencies (if any frontend build process is involved).
*   **`static/`:** Contains static files (CSS, JavaScript, images) served by Django.
*   **`staticfiles/`:** Collected static files for deployment.
*   **`templates/`:** HTML templates for rendering web pages.
*   **`venv/`:** Python virtual environment.

## Key Features

The Almog1 application provides a wide range of features, including:

*   **User Authentication & Authorization:** Secure login, JWT-based authentication, custom cookie authentication, and granular permission management for users and groups.
*   **Product Management:** Comprehensive system for managing product details, including categories, subcategories, models, engines, OEM numbers, and associated images.
*   **Inventory Control:** Features for tracking product balance, movement, and managing lost/damaged items.
*   **Client & Supplier Management:** Tools for managing client and supplier information, including account statements and reports.
*   **Invoice Management (Buy & Sell):** Full lifecycle management of purchase and sales invoices, including item details, cost calculations, and return permissions.
*   **Employee Management:** Functionalities for managing employee details, attendance, salaries, and balance adjustments.
*   **Order Assignment & Delivery:** System for assigning orders to employees, tracking delivery status, and managing delivery history.
*   **Real-time Notifications:** Integration with Firebase Cloud Messaging (FCM) for push notifications and Django Channels for real-time updates.
*   **Reporting & Analytics:** Various reports and analytical tools for sales, purchases, item performance, and client data.
*   **API Documentation:** Automatically generated API documentation using `drf-spectacular` for easy integration and understanding of available endpoints.
*   **Custom Middleware:** Custom middleware for refreshing authentication tokens and logging requests.

## API Endpoints

The project exposes a comprehensive set of RESTful API endpoints. Detailed documentation for these endpoints can be accessed via:

*   **Swagger UI:** `/api/schema/swagger-ui/`
*   **ReDoc:** `/api/schema/redoc/`

These interfaces provide interactive documentation, allowing developers to explore available endpoints, their parameters, and expected responses.

## Setup Instructions

To set up and run the Almog1 project locally, follow these steps:

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd almog1
    ```

2.  **Create a virtual environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install dependencies:**
    Install all required Python packages using pip:
    ```bash
    pip install -r requirements.txt
    ```

4.  **Database Configuration:**
    The project uses MSSQL. Ensure your MSSQL server is running and accessible. Update the `DATABASES` setting in `Almog1/settings.py` with your database credentials.

    ```python
    DATABASES = {
        'default': {
            'ENGINE': 'mssql',
            'NAME': 'your_database_name',
            'USER': 'your_username',
            'PASSWORD': 'your_password',
            'HOST': 'your_database_host', # e.g., 'localhost' or IP address
            'PORT': '1433', # Default MSSQL port
            'OPTIONS': {
                'driver': 'ODBC Driver 17 for SQL Server', # Ensure this driver is installed
                'Trusted_Connection':'yes', # Use 'no' if not using Windows Authentication
            },
            'TEST': {
                'NAME': 'almog1_testing_db',
            },
        },
    }
    ```
    **Note:** You might need to install the ODBC Driver for SQL Server on your system.

5.  **Run Database Migrations:**
    Apply the database migrations to create the necessary tables:
    ```bash
    python manage.py migrate
    ```

6.  **Create a Superuser (for Admin access):**
    To access the Django admin panel, create a superuser account:
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to set up your username, email, and password.

7.  **Run the Development Server:**
    Start the Django development server:
    ```bash
    python manage.py runserver
    ```
    The application will typically be accessible at `http://127.0.0.1:8000/`.

8.  **Celery & Redis Setup (for Asynchronous Tasks and Real-time Communication):**
    The project utilizes Celery for background tasks and Django Channels for real-time communication, both relying on Redis.

    *   **Install Redis:** Ensure you have a Redis server installed and running.
    *   **Start Celery Worker:**
        Open a new terminal and run the Celery worker:
        ```bash
        celery -A Almog1 worker -l info
        ```
    *   **Start Celery Beat (for scheduled tasks):**
        Open another terminal and run Celery beat:
        ```bash
        celery -A Almog1 beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler
        ```
    *   **Run Django Channels Server:**
        For WebSocket communication, run the Daphne server:
        ```bash
        daphne -b 0.0.0.0 -p 8001 Almog1.asgi:application
        ```
        (Adjust the port if 8001 is already in use.)

## Contributing

[Add information on how to contribute to the project, if applicable.]

## License

[Add license information, e.g., MIT, Apache 2.0, etc.]
