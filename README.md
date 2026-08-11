# Django Blog REST API

## Overview
This project is a Django REST API for managing blog posts and comments. It uses Django, Django REST Framework, SQLite3, JWT authentication, and django-filter for search and filtering.

## Features
- JWT authentication with SimpleJWT
- Post CRUD via ModelViewSet
- Author-based permissions
- Comment creation and deletion
- Filtering by author
- Search by title and content
- Pagination with 10 results per page
- SQLite database
- API tests
- Swagger/OpenAPI documentation

## Tech Stack
- Python
- Django
- Django REST Framework
- SQLite3
- djangorestframework-simplejwt
- django-filter

## Project Structure

```text
WinLogics/
├── .gitignore
├── README.md
├── requirements.txt
├── manage.py
├── db.sqlite3
├── config/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── blog/
│   ├── migrations/
│   │   ├── __init__.py
│   │   └── 0001_initial.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── test_auth.py
│   │   ├── test_posts.py
│   │   └── test_comments.py
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── models.py
│   ├── serializers.py
│   ├── permissions.py
│   ├── pagination.py
│   ├── urls.py
│   └── views.py
└── postman/
    └── Django-Blog-API.postman_collection.json
```

## Installation

```bash
python -m venv .venv
```

### Windows

```powershell
.\.venv\Scripts\activate
pip install -r requirements.txt
```

## Database
This project uses SQLite3. After running migrations, Django creates the database file `db.sqlite3` in the project root.

## Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

## Superuser

```bash
python manage.py createsuperuser
```

## Running the Server

```bash
python manage.py runserver
```

## API Documentation
Open the Swagger UI at:

```text
http://127.0.0.1:8000/swagger/
```

## Authentication
JWT is used for protected endpoints via bearer tokens.

Example header:

```http
Authorization: Bearer <access_token>
```

## API Endpoints

| Method | Endpoint | Auth | Description |
| --- | --- | --- | --- |
| POST | /api/auth/register/ | No | Register a new user |
| POST | /api/auth/login/ | No | Login and receive JWT tokens |
| POST | /api/auth/token/refresh/ | No | Refresh access token |
| GET | /api/posts/ | Optional | List posts |
| POST | /api/posts/ | Required | Create a post |
| GET | /api/posts/{id}/ | Optional | Retrieve a post |
| PUT | /api/posts/{id}/ | Author only | Update a post |
| PATCH | /api/posts/{id}/ | Author only | Partially update a post |
| DELETE | /api/posts/{id}/ | Author only | Delete a post |
| GET | /api/posts/{post_id}/comments/ | Optional | List comments for a post |
| POST | /api/posts/{post_id}/comments/ | Required | Create a comment |
| DELETE | /api/comments/{comment_id}/ | Author only | Delete a comment |

## Filtering

```text
/api/posts/?author=1
```

## Searching

```text
/api/posts/?search=django
```

## Pagination

```text
/api/posts/?page=2
```

## Testing

```bash
python manage.py test
```

## Postman
Import the Postman collection from:

```text
postman/Django-Blog-API.postman_collection.json
```

## Permissions
- Anonymous users can read posts and comments.
- Anonymous users cannot create posts or comments.
- Authenticated users can create posts/comments.
- Only the author can update or delete their own post.
- Only the author can delete their own comment.
- Other users cannot modify or delete someone else’s content.

## Future Improvements
Possible future enhancements include:
- article categories and tags
- user profile endpoints
- email verification
- soft delete support
- richer comment moderation
- better API rate limiting
- deployment configuration

