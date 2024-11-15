# EstiReq
## Transforming Requirements into Actionable Estimates.

Team leaders in software development often struggle with managing tasks and meeting tight deadlines. New requirements can appear suddenly, requiring quick and accurate time estimates, which can be difficult to achieve. The process of breaking down tasks and figuring out the time needed for each one often consumes a lot of time, slowing down progress. Miscommunication between team members and stakeholders further complicates this, as unclear instructions can lead to inefficiencies and errors. Additionally, managing task dependencies becomes a challenge, as delays in one task can hold up the rest, making it harder to allocate resources effectively.

Moreover, tight deadlines add pressure, making it challenging to maintain quality. Developers may feel rushed and may have to skip planning or thorough testing to meet deadlines, increasing the risk of bugs and unfinished features. These issues not only hinder smooth workflow but also increase the likelihood of delays and decreased product quality, causing burnout among team members. Balancing all of these aspects while keeping the project on track is a constant struggle for team leaders.

[![License](https://img.shields.io/badge/License-Apache2-blue.svg)](https://www.apache.org/licenses/LICENSE-2.0)

## Short description
The idea is to use AI to help software development teams quickly estimate the time required for tasks and provide clear, step-by-step guides for building them. This aims to reduce the time spent on planning and improve efficiency, allowing teams to focus on execution and meet tight deadlines with clearer instructions and better time management.

### What's the problem?
In current software development processes, team leaders often face challenges in managing multiple tasks and tight deadlines. New requirements can come up unexpectedly, and leaders manually need to estimate how much time each task will take and provide clear instructions on how to build them. This process is usually slow and takes a lot of time, which can delay progress and affect the team’s ability to focus on actual work.

Challenges:

1. Slow Time Estimates: Estimating how long tasks will take is a time-consuming process, which can delay the project.
2. Unclear Instructions: It’s difficult to quickly create clear and actionable steps for developers, leading to confusion and mistakes.
3. Changing Requirements: New tasks or changes often come up suddenly, making it hard to keep everything organized and on schedule.
4. Less Focus on Development: A lot of time is spent on planning and estimating, leaving less time for the actual work.

This project aims to solve these problems by using AI to quickly estimate time and generate clear instructions, allowing teams to focus more on development and stay on track.

### Solution

The solution is an AI-powered tool designed to help development teams by providing quick time estimates and detailed implementation guides for new tasks. Instead of spending hours figuring out how long a task will take, the AI analyzes the requirements and gives an accurate estimate in no time. This helps project managers make better decisions and avoid delays.

In addition, the AI generates step-by-step implementation guides, making it easier for junior developers to understand and execute tasks. It provides clear instructions, code snippets, and best practices, so junior developers can work more independently. By automating these processes, the team can focus more on building the product and less on planning, keeping the project on track and improving efficiency.

### The idea

The idea is to create an AI-powered tool that provides quick time estimates and detailed implementation guides for new tasks, helping teams stay on track and improve efficiency. It also assists junior developers by offering clear instructions and code snippets for task execution.

## Demo video

https://www.youtube.com/watch?v=M6QRExVh4BM

1. Analyzes project requirements (user stories).
2. Compares them with similar past tasks.
3. Provides accurate time estimates for each task.
4. Generates a detailed step-by-step implementation guide.
5. Offers clear instructions, especially for junior developers.
6. Helps teams plan better and work more efficiently.

## What Next ?

The future scope of the solution includes enhancing AI models for more accurate task estimation and analysis, enabling automated task prioritization to help project managers make better decisions. Expanding integration with more project management tools like Jira and Trello will streamline workflows,  Additionally, a user feedback loop will help the AI learn and improve over time, and implementing voice and natural language input will make the system more accessible and user-friendly.

## Model API Endpoint

curl -X POST -F "file=@/path/to/srs.pdf" -F "mode=estimate/guide" [http://localhost:5000/analyze](https://esti-req-gen-ai-model-git-suneetha123-dev.apps.cluster.intel.sandbox1234.opentlc.com/analyze)

## Getting started

## Setup

This code works on Python3+ versions.

## Clone the repository

## With Docker:

$ git clone 

$ WebApp/

## Install Docker
https://docs.docker.com/engine/install/ubuntu/

## Build docker image

$ docker build -t estireq_docker .

Note: ensure in app.py port is mentioned as 8080

$ docker run -it -p 8080:8080 estireq_docker

In Browser run with 127.0.0.1:8080

## To push:

$docker login

  Username: XXXX

  Password: XXXX

$ docker tag estireq_docker estireq/estireq_docker:1.0.0

$ docker push estireq/estireq_docker:1.0.0

## Without Docker:

## Install the required libraries

$ pip3 install -r requirements.txt

## Clone the repository

$ git clone 

$ EstiReq-GenAI-Model/

## Run app.py

$ python3 app.py

or

$ python -m flask run

In Browser run with 127.0.0.1:5000

## Authors
- **Suneetha Jonadula** - _Lead Developer_

## License

This project is licensed under the Apache 2 License - see the [LICENSE](LICENSE) file for details.

