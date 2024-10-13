
# MyApp - Game Store Application

This project is a Python-based web application that allows users to browse and purchase games. The app can be run using Docker Compose, Docker, or a Python virtual environment. This guide provides detailed instructions for setting up and running the application in various environments.

## Prerequisites

Before running the project, ensure you have the following installed on your machine:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [Python 3.11](https://www.python.org/downloads/) (for running with virtual environments)
- [pip](https://pip.pypa.io/en/stable/installation/) (for installing Python packages)

## Running the Application

### Option 1: Using Docker Compose

The easiest way to run the application is with Docker Compose.

1. **Build and Start the Application:**

   Run the following command to build and start the app:

   ```bash
   docker-compose up --build
   ```

   This will build the Docker image and start the application on port `5000`.

2. **Access the Application:**

   Once the app is running, open your browser and navigate to:

   ```
   http://localhost:5000
   ```

3. **Stopping the Application:**

   To stop the application, press `CTRL + C` or run:

   ```bash
   docker-compose down
   ```

### Option 2: Using Docker

You can also run the application directly using Docker without Compose.

1. **Build the Docker Image:**

   Run the following command to build the Docker image:

   ```bash
   docker build -t myapp .
   ```

2. **Run the Docker Container:**

   After building the image, run the container with the following command:

   ```bash
   docker run -p 5000:5000 --name myapp-container myapp
   ```

3. **Access the Application:**

   Open your browser and go to:

   ```html
   http://localhost:5000
   ```

4. **Stopping the Container:**

   To stop the container, press `CTRL + C` or run:

   ```bash
   docker stop myapp-container
   ```

### Option 3: Running with Virtual Environment (venv)

If you prefer not to use Docker, you can run the application in a Python virtual environment.

1. **Extract the Repository:**

   Extract the repo

2. **Create and Activate a Virtual Environment:**

   Create a virtual environment with the following commands:

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Linux/Mac
   ```

3. **Install Dependencies:**

   Install the required dependencies from the `requirements.txt` file:

   ```bash
   pip install -r requirements.txt
   ```

4. **Export the PYTHONPATH:**

   Since the `frontend` folder contains the main Python application, you need to set the `PYTHONPATH` to ensure Python can find the module.

   On Linux/Mac:

   ```bash
   export PYTHONPATH=$PYTHONPATH:./frontend
   ```

   On Windows (PowerShell):

   ```powershell
   $env:PYTHONPATH = "$env:PYTHONPATH;./frontend"
   ```

5. **Run the Application:**

   Start the application by running the following command:

   ```bash
   python run.py
   ```

6. **Access the Application:**

   Navigate to:

   ```
   http://localhost:5000
   ```

7. **Deactivate the Virtual Environment:**

   When you're done, deactivate the virtual environment by running:

   ```bash
   deactivate
   ```

## Application Details

- **Port**: The application runs on port `5000`.
- **Dependencies**: The required dependencies are listed in `requirements.txt` and installed during the setup process.
- **Main Application File**: The entry point of the application is `frontend/main.py`.

## Common Issues

- **Port Already in Use**: If port `5000` is already in use, change the port in both the `docker-compose.yml` and `frontend/main.py`.
- **PYTHONPATH Not Set**: If you encounter `ModuleNotFoundError`, ensure that the `PYTHONPATH` is properly set as shown above.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.