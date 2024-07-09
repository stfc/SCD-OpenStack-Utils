**Project Title:** End-end deployment of a Large Language Model web application

**Project Overview:**

Create a web application that allows users to send questions to a LLM backend and receive a response. The page will display the user's question, response and the response time.

**Functional Requirements:**

1. User Input:
    * A text input field for users to enter questions.
    * A submit button to send the question to the backend.
2. LLM Backend:
    * Intergrate with an Ollama LLM API instance using basic auth or tokens.
    * Send streamed/completed responses to the users session.
3. Response Display:
    * Display the users question.
    * Display the LLM response either streamed or complete.
4. Response Time Measurment:
    * Measure and display the round trip time (RTT) and generation time.
5. Instructions for self-hosting:
    * Provide simple setup instructions for a user to host their own LLM.

**Non-Functional Requirements (Priority):**

1. Performance (Medium):
    * Ensure the webpage responds in a timely mannor. Think complete/streamed responses.
2. Security (High):
    * Implement basic auth or API tokens for authentication with the backend.
    * Set up HTTPS using Let's Encrypt to encrypt traffic to the backend.
3. Usability (Low):
    * Design an intuitive interface for users to submit questions and view responses.

**Technical Requirements:**

1. Frontend:
        * Build the webpage using HTML, CSS and JavaScript.
        * Use native JavaScript APIs to make HTTP requests to the backend.
2. Backend:
        * Use the Ollama LLM API with authentication for receiving user questions and sending responses.
        * (To be investigated) Use a database to store authentication information.
3. Infrastructure:
        * Use Terraform to provision multiple VM instances and networking.
        * Configure machines/containers using Ansible playbooks to ensure consistency in deployment.
        * Run the web server on multiple VM instances, each with its own Docker container.
        * Use an Apache container to host the website within each Web VM.
        * Set up a separate VM instance (with or without Docker) to run HAProxy and Let's Encrypt services.
        * Configure HAProxy to load balance traffic across the multiple web server instances.
        * Host the Ollama service directly on a separate GPU VM.
      
**Useful Resources:**

1. [HTML, CSS, JS resources](https://developer.mozilla.org/en-US/)
2. [HTML Tutorial](https://www.w3schools.com/html/)
3. [CSS Tutorial](https://www.w3schools.com/css/)
4. [JavaScript Tutorial](https://www.w3schools.com/js/)
5. [Terraform Documentation](https://registry.terraform.io/providers/terraform-provider-openstack/openstack/latest/docs)
6. [Ansible Documentation](https://docs.ansible.com/)
7. [Docker Documnetation](https://docs.docker.com/)
8. [Ollama Documentation](https://github.com/ollama/ollama) 
