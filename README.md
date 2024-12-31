# Django-Channel-ChatApp
## Getting Started

### Prerequisites
- Python 
- Django
- Django Rest Framework
- Channels
- Redis
- Celery

### Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/Django-Channel-ChatApp.git
    cd Django-Channel-ChatApp
    ```

2. Create and activate a virtual environment:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Start Redis server:
    ```bash
    redis-server
    ```

5. Apply migrations:
    ```bash
    python manage.py migrate
    ```

6. Create a superuser:
    ```bash
    python manage.py createsuperuser
    ```

7. Run the development server:
    ```bash
    Terminal 1: celery -A chat_project worker -l info
    Terminal 2: celery -A chat_project beat -l info

    Terminal3: python manage.py runserver
    ```

### Usage

1. Open your web browser and go to `http://127.0.0.1:8000/`.
2. Log in with the superuser credentials.
3. Start chatting!
