# Django REST API with JWT Authentication and RBAC

This project implements a small Django REST API with user authentication using JWT, role-based access control (RBAC), and secured resource endpoints. It was developed as an interview test following the provided requirements.

## Features Implemented

*   User registration and login using Django REST Framework and `djangorestframework-simplejwt`.
*   JWT (JSON Web Token) generation and refresh using `/api/token/` and `/api/token/refresh/`.
*   Custom User model extending Django's built-in `AbstractUser` to include a `role` field (Admin, Manager, User).
*   Role-based access control enforced using custom Django REST Framework permission classes.
*   A `/api/resources/` endpoint with permissions ensuring:
    *   Admin users can Create, Read, Update, and Delete resources.
    *   Manager users can Read and Update resources.
    *   Regular users can only Read resources.
*   A `/api/me/` endpoint to retrieve information about the currently authenticated user.
*   API documentation automatically generated using `drf-yasg`, available in Swagger UI and ReDoc formats.
*   A simple home page at the root URL (`/`) providing links to key project areas.
*   Automated API tests using `APITestCase` to verify authentication and permission logic.

## Setup Instructions

1.  **Clone the repository.**

2.  **Navigate to the project directory.**

3.  **Create a Python virtual environment:**
    ```bash
    python -m venv venv
    ```

4.  **Activate the virtual environment:**
    *   On Windows:
        ```bash
        .\venv\Scripts\activate
        ```
    *   On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```

5.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

6.  **Run database migrations:**
    ```bash
    python manage.py migrate
    ```

7.  **Create a superuser (for accessing the Django Admin site):**
    ```bash
    python manage.py createsuperuser
    ```
    Follow the prompts to create the admin user.

8.  **Run the Django development server:**
    ```bash
    python manage.py runserver
    ```
    The API will be accessible at `http://127.0.0.1:8000/`.

## Project Access Points

Once the server is running, you can access:

*   **Home Page:** `http://127.0.0.1:8000/` (Provides links to below)
*   **Django Admin Site:** `http://127.0.0.1:8000/admin/` (Login with superuser)
*   **Swagger UI Documentation:** `http://127.0.0.1:8000/swagger/`
*   **ReDoc Documentation:** `http://127.0.0.1:8000/redoc/`

## API Endpoints Overview

All API endpoints are under the `/api/` path:

*   `POST /api/register/` - Register a new user.
*   `POST /api/token/` - Obtain JWT `access` and `refresh` tokens.
*   `POST /api/token/refresh/` - Obtain a new `access` token using a valid `refresh` token.
*   `GET /api/me/` - Get information about the authenticated user (requires `Bearer` token).
*   `/api/resources/` - Endpoint for managing resources (requires `Bearer` token, permissions vary by role).

## Testing the API and Permissions

I used Postman to test the API endpoints and verify the role-based permissions with cURL/Invoke-WebRequest.

**Pre-configured Test Users:**

To easily test different permission levels, the following users were created via the API and had their roles assigned via the Django Admin site:

*   **Eben:** Admin user (`username`: `Eben`, `password`: `Hangwani@23`, `email`: `eben@gmail.com`)
*   **Raj:** Manager user (`username`: `Raj`, `password`: `Hangwani@23`, `email`: `ratjaji@gmail.com`)
*   **Thomas:** Regular user (`username`: `Thomas`, `password`: `Hangwani@23`, `email`: `thomas@gmail.com`)

**Testing Steps:**

1.  **Obtain a Token:** Use the `POST /api/token/` endpoint with the username and password of the desired test user (Eben, Raj, or Thomas) to get their `access` token.
2.  **Authorize Requests:** Include the obtained `access` token in the `Authorization` header of subsequent requests in the format `Bearer <access_token>`.
3.  **Test Endpoints:** Make requests to the `/api/me/` and `/api/resources/` endpoints using the authorized token to observe behavior based on the user's role.

    *   **Admin (Eben):** Should be able to GET `/api/me/`, and perform GET, POST, PUT, PATCH, DELETE on `/api/resources/`.
    *   **Manager (Raj):** Should be able to GET `/api/me/`, GET, PUT, PATCH on `/api/resources/`. POST and DELETE should return `403 Forbidden`.
    *   **User (Thomas):** Should be able to GET `/api/me/`, and only GET on `/api/resources/`. POST, PUT, PATCH, and DELETE should return `403 Forbidden`.
    *   **Unauthenticated:** Accessing `/api/me/` or `/api/resources/` without a token should return `401 Unauthorized` (except for POST to `/api/register/` and POST to `/api/token/`, which are publicly accessible).

**Postman Examples:**

A Postman collection containing sample API requests for authentication, user info, and resource management is provided in the project root (`Django REST API Interview.postman_collection.json`). You can import this file into Postman to quickly access and run the pre-configured requests.

**cURL Examples (equivalent to PowerShell's Invoke-WebRequest):**

*   **Obtain Token (using 'Eben'):**
    ```bash
    curl -X POST http://127.0.0.1:8000/api/token/ \
      -H "Content-Type: application/json" \
      -d '{"username": "Eben", "password": "Hangwani@23"}'
    ```
    (Note: For PowerShell, use `Invoke-WebRequest -Uri ... -Method POST -Headers @{"Content-Type"="application/json"} -Body '{"username"="Eben", "password"="Hangwani@23"}'`) Replace Eben's credentials with others to test login for different users.

*   **Access Protected Endpoint (using an obtained token):**
    ```bash
    curl -X GET http://127.0.0.1:8000/api/me/ \
      -H "Authorization: Bearer <your_access_token>"
    ```
    (Note: For PowerShell, use `Invoke-WebRequest -Uri ... -Method GET -Headers @{"Authorization"="Bearer <your_access_token>"}`) Replace `<your_access_token>` with the token obtained from the `/api/token/` endpoint.

*   **Create Resource (as Admin):**
    ```bash
    curl -X POST http://127.0.0.1:8000/api/resources/ \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer <admin_access_token>" \
      -d '{"name": "New Resource from cURL", "description": "Created via command line"}'
    ```

## Automated Tests

Automated API tests are included in `api/tests.py` using Django REST Framework's `APITestCase`. These tests cover the core authentication flows and verify that the role-based permissions on the resource endpoints are being correctly applied for Admin, Manager, and User roles.

To run the tests:

```bash
python manage.py test api
```

All tests should pass, indicating that the core functionality is working as designed.

## Code Structure and Best Practices

The project follows a standard Django project structure, with a core project (`core`) and a main application (`api`) handling the API logic. A separate `home` app was created for the home page.

*   `api/models.py`: Defines the custom `User` model and the `Resource` model.
*   `api/serializers.py`: Handles serialization/deserialization for the models.
*   `api/permissions.py`: Contains custom permission classes for RBAC.
*   `api/views.py`: Implements the API view logic (registration, user info, resource management).
*   `api/urls.py`: Defines URL patterns for the API endpoints.
*   `api/tests.py`: Contains automated API tests.
*   `core/settings.py`: Project-level settings, including app registration, database config, JWT settings, and Swagger config.
*   `core/urls.py`: Main URL routing, including paths for admin, api, swagger, redoc, and home.
*   `home/`: App for the home page.
*   `requirements.txt`: Lists project dependencies.
*   `README.md`: This file, providing project overview and instructions.
*   `Django REST API Interview.postman_collection.json`: Exported Postman collection.

The code aims for clarity, modularity, and follows common Django and DRF patterns.
