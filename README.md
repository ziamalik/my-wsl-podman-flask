# my-wsl-podman-flask

This guide will walk you through installing Podman on your Fedora WSL distribution, creating a simple Python Flask web application, containerizing it with Podman, and accessing it from your Windows host browser.

**Prerequisites:**

* Fedora installed and running on WSL.
* You are comfortable running commands in the Linux terminal.

---

## Step 1: Install Podman on Fedora WSL

First, let's update your Fedora system and install Podman.

1.  **Open your Fedora WSL terminal.**

2.  **Update package repositories and upgrade existing packages:**
    ```bash
    sudo dnf update -y
    ```

3.  **Install Podman:**
    ```bash
    sudo dnf install podman -y
    ```

4.  **Verify Podman installation:**
    ```bash
    podman --version
    ```
    You should see the installed Podman version.

    *Note: Podman on WSL typically runs rootless, meaning you don't need `sudo` for most Podman commands after installation, and it doesn't require a separate daemon to be running constantly like Docker often does.*

---

## Step 2: Create a Simple Python Flask App

Now, let's create a basic Flask application.

1.  **Create a project directory for your Flask app inside your Fedora WSL environment.** For example, in your home directory:
    ```bash
    mkdir ~/my_flask_app
    cd ~/my_flask_app
    ```

2.  **Create the Flask application file (`app.py`):**
    Create a new file named `app.py` using a text editor like `nano` or `vim`:
    ```bash
    nano app.py
    ```
    Paste the following Python code into the file:
    ```python
    from flask import Flask

    app = Flask(__name__)

    @app.route('/')
    def hello_world():
        return 'Hello, World from Flask in a Podman container!'

    if __name__ == '__main__':
        # Listen on all network interfaces within the container
        # and use port 5000 (or any port you prefer)
        app.run(host='0.0.0.0', port=5000)
    ```
    Save and close the file (Ctrl+X, then Y, then Enter in `nano`).

3.  **Create a `requirements.txt` file:**
    This file will list the Python dependencies for your application.
    ```bash
    nano requirements.txt
    ```
    Add the following line:
    ```
    Flask>=2.0
    ```
    Save and close the file.

Your project directory (`~/my_flask_app`) should now contain:
* `app.py`
* `requirements.txt`

---

## Step 3: Create a Containerfile

A `Containerfile` (similar to a `Dockerfile`) contains instructions to build your container image.

1.  **In your project directory (`~/my_flask_app`), create a file named `Containerfile`:**
    ```bash
    nano Containerfile
    ```
    Paste the following content:
    ```dockerfile
    # Use an official Python runtime as a parent image
    FROM python:3.9-slim

    # Set the working directory in the container
    WORKDIR /app

    # Copy the requirements file into the container at /app
    COPY requirements.txt .

    # Install any needed packages specified in requirements.txt
    RUN pip install --no-cache-dir -r requirements.txt

    # Copy the current directory contents into the container at /app
    COPY . .

    # Make port 5000 available to the world outside this container
    EXPOSE 5000

    # Define environment variable
    ENV FLASK_APP=app.py
    ENV FLASK_RUN_HOST=0.0.0.0

    # Run app.py when the container launches
    CMD ["flask", "run"]
    ```
    Save and close the file.

    **Explanation of the Containerfile:**
    * `FROM python:3.9-slim`: Uses a lightweight Python 3.9 image as the base.
    * `WORKDIR /app`: Sets the working directory inside the container to `/app`.
    * `COPY requirements.txt .`: Copies your `requirements.txt` into `/app`.
    * `RUN pip install --no-cache-dir -r requirements.txt`: Installs Flask.
    * `COPY . .`: Copies the rest of your application (like `app.py`) into `/app`.
    * `EXPOSE 5000`: Informs Podman that the container will listen on port 5000. This is documentation; the actual port mapping happens during `podman run`.
    * `ENV FLASK_APP=app.py` and `ENV FLASK_RUN_HOST=0.0.0.0`: Sets environment variables for Flask.
    * `CMD ["flask", "run"]`: Specifies the command to run when the container starts. This uses Flask's built-in development server.

---

## Step 4: Build and Run the Container with Podman

Now, let's build the image and run the container.

1.  **Navigate to your project directory (`~/my_flask_app`) in your Fedora WSL terminal if you aren't already there.**

2.  **Build the container image using Podman:**
    ```bash
    podman build -t my-flask-app .
    ```
    * `-t my-flask-app`: Tags the image with the name `my-flask-app`.
    * `.`: Specifies that the build context (where `Containerfile` and app files are located) is the current directory.
    This might take a few moments the first time as it downloads the base Python image.

3.  **Run the Podman container:**
    ```bash
    podman run -d -p 5000:5000 --name flask_container my-flask-app
    ```
    * `-d`: Runs the container in detached mode (in the background).
    * `-p 5000:5000`: Maps port 5000 on your Windows host to port 5000 in the container. This is crucial for accessing the app from your Windows browser. The format is `hostPort:containerPort`.
    * `--name flask_container`: Assigns a name to your running container for easier management.
    * `my-flask-app`: The name of the image to run.

4.  **Check if the container is running:**
    ```bash
    podman ps
    ```
    You should see `flask_container` listed with a status indicating it's running.

5.  **View container logs (optional, for troubleshooting):**
    ```bash
    podman logs flask_container
    ```
    You should see output from the Flask development server, indicating it's running and listening on `http://0.0.0.0:5000/`.

---

## Step 5: Accessing the App from Windows Browser

With the container running and the port mapped, you should be able to access your Flask application from any web browser on your Windows host.

1.  **Open your web browser (Chrome, Edge, Firefox, etc.) on Windows.**
2.  **Navigate to:**
    ```
    http://localhost:5000
    ```

You should see the message: "Hello, World from Flask in a Podman container!"

**WSL Networking Notes:**
Recent versions of WSL2 have excellent networking integration, and `localhost` forwarding usually works seamlessly. If for some reason `localhost` doesn't work, you might need to find the IP address of your WSL instance (e.g., using `ip addr show eth0` inside your Fedora WSL terminal) and use that IP address instead of `localhost` in your Windows browser. However, `localhost` is the standard and preferred method.

---

## Step 6: Managing Your Container

Here are some basic commands to manage your container:

* **Stop the container:**
    ```bash
    podman stop flask_container
    ```

* **Start the container again:**
    ```bash
    podman start flask_container
    ```

* **Remove the container (must be stopped first):**
    ```bash
    podman rm flask_container
    ```

* **List all containers (including stopped ones):**
    ```bash
    podman ps -a
    ```

* **Remove the container image:**
    (Only do this if you no longer need the image or want to rebuild it fresh)
    ```bash
    podman rmi my-flask-app
    ```

---

Congratulations! You've successfully installed Podman on Fedora WSL, created a Flask app, containerized it, and accessed it from your Windows host. This setup provides a powerful environment for developing and testing containerized applications.
