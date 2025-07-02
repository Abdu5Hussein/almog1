# Almog1 Project API Documentation

This document provides an overview of the RESTful APIs available in the Almog1 project and how to access their detailed documentation.

## Accessing API Documentation

The Almog1 project utilizes `drf-spectacular` to generate interactive API documentation. You can access the detailed API documentation through the following interfaces:

*   **Swagger UI:** For an interactive and user-friendly exploration of all API endpoints, their parameters, and responses.
    *   **URL:** `/api/schema/swagger-ui/`

*   **ReDoc:** For a more concise and readable documentation format, ideal for quick reference.
    *   **URL:** `/api/schema/redoc/`

To access these, ensure the Django development server is running (as described in the main `README.md` file) and navigate to the respective URLs in your web browser (e.g., `http://127.0.0.1:8000/api/schema/swagger-ui/`).

## API Functionalities Overview

The Almog1 API provides a comprehensive set of endpoints to manage various aspects of the system. Key functional areas include:

*   **Authentication & Authorization:**
    *   User login, logout, token generation, and refresh.
    *   Management of user permissions and activation status.

*   **User & Employee Management:**
    *   Creating, retrieving, updating, and deleting user and employee profiles.
    *   Managing employee attendance, salaries, and balance adjustments.

*   **Product & Inventory Management:**
    *   CRUD operations for products, categories, subcategories, models, engines, and OEM numbers.
    *   Tracking product movement, lost/damaged items, and managing storage locations.
    *   Uploading and retrieving product images.

*   **Client & Supplier Management:**
    *   Managing client and supplier information.
    *   Generating account statements and reports for clients and suppliers.

*   **Invoice Management (Buy & Sell):**
    *   Creation, retrieval, update, and deletion of purchase (buy) and sales (sell) invoices.
    *   Management of invoice items, costs, and return permissions.
    *   Invoice reporting and Excel export functionalities.

*   **Order & Delivery Management:**
    *   Assigning orders to employees/drivers.
    *   Tracking order status, confirming delivery, and managing delivery history.
    *   Monitoring order assignments and employee availability.

*   **Support & Feedback System:**
    *   Sending and receiving feedback messages.
    *   Managing support conversations and marking messages as read.

*   **Notifications:**
    *   Firebase Cloud Messaging (FCM) integration for sending and registering push notifications.

*   **Analytics & Reporting:**
    *   Endpoints for sales analysis, purchase analysis, item analytics (by category, price, source), and invoice status summaries.

*   **System Configuration:**
    *   Endpoints for managing companies, countries, and other system-wide settings.

This API is designed to be the primary interface for interacting with the Almog1 system programmatically, supporting both web and mobile applications.