# Wochenplan Production Readiness Roadmap

This document outlines the steps taken to make the Wochenplan application production-ready.

## Setup and Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/wochenplan.git
    cd wochenplan
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up the environment variables:**
    -   Copy the `.env.example` file to `.env`:
        ```bash
        cp .env.example .env
        ```
    -   Edit the `.env` file and add the required environment variables:
        -   `SECRET_KEY`: A strong, random secret key.
        -   `DATABASE_URI`: The URI for the database.
        -   `POLLINATIONS_API_KEY`: Your API key for Pollinations.

5.  **Run the database migrations:**
    ```bash
    flask db upgrade
    ```

6.  **Seed the database with initial data:**
    ```bash
    python seed.py
    ```

## Running the Application

-   **Development:**
    ```bash
    flask run
    ```

-   **Production:**
    ```bash
    export FLASK_ENV=production
    gunicorn -w 4 -b 0.0.0.0:$PORT run:app
    ```

## Testing

-   Run the tests with the following command:
    ```bash
    python -m unittest discover -s tests
    ```

## Linting and Static Analysis

-   Run `flake8` and `bandit` to check for code quality and security issues:
    ```bash
    flake8 .
    bandit -r .
    ```
