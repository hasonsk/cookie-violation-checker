**1. Local Development (with Python environment)**
To set up and run the server locally, follow these steps:

*   **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```
*   **Run the FastAPI application:**
    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
    ```
    *Note: Ensure you have a `.env` file in your project root with necessary environment variables (e.g., `PORT`, `DB_NAME`, `MONGODB_PWD`). You can refer to `.env.example` for required variables.*

**2. Local Development (with Ngrok for public access)**

If you want to expose your local server to the internet (e.g., for testing webhooks or sharing with others), you can use Ngrok.
*   **Ensure Ngrok is installed and authenticated:**
    If you haven't already, install Ngrok (e.g., `sudo snap install ngrok` on Ubuntu) and add your authtoken:
    ```bash
    ngrok config add-authtoken YOUR_NGROK_AUTHTOKEN
    ```
    (Replace `YOUR_NGROK_AUTHTOKEN` with your actual token from [https://dashboard.ngrok.com/get-started/your-authtoken](https://dashboard.ngrok.com/get-started/your-authtoken))
*   **Run the FastAPI application (in a separate terminal):**
    ```bash
    uvicorn src.main:app --host 0.0.0.0 --port 8000
    ```
*   **Expose the local server with Ngrok (in another terminal):**
    ```bash
    ngrok http 8000
    ```
    Ngrok will provide a public URL (e.g., `https://xxxx-xx-xx-xx-xx.ngrok-free.app`) that forwards to your local server.

**3. Dockerized Deployment**

For production or consistent environments, it's recommended to use Docker.

*   **Build the Docker image:**
    ```bash
    docker build -t your-dockerhub-username/cookie-violation-checker-backend:latest .
    ```
    (Replace `your-dockerhub-username` with your actual Docker Hub username.)
*   **Run the Docker container:**
    ```bash
    docker run -d -p 8000:8000 --name cookie-checker-backend your-dockerhub-username/cookie-violation-checker-backend:latest
    ```
    (This runs the container in detached mode (`-d`) and maps port 8000 from the container to port 8000 on your host machine.)

    *Note: You might need to pass environment variables to the Docker container using `-e KEY=VALUE` flags in the `docker run` command, especially for database credentials.*

**4. CI/CD with GitHub Actions (Automated Deployment to Docker Hub)**

I have already set up a GitHub Actions workflow (`.github/workflows/main_ci_cd.yml`) that automates the build, test, and push to Docker Hub process.

*   **Prerequisites:**
    *   Your code is hosted on GitHub.
    *   You have a Docker Hub account.
    *   You have added `DOCKER_USERNAME` and `DOCKER_PASSWORD` as GitHub Secrets in your repository settings (Settings > Secrets and variables > Actions).
*   **Triggering the pipeline:**
    *   Pushing changes to the `main` branch.
    *   Creating a pull request targeting the `main` branch.

This setup ensures that your server can be run and deployed efficiently in various scenarios.
