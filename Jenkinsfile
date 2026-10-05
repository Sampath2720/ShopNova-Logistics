pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        timestamps()
    }

    environment {
        IMAGE_NAME = 'shopnova-logistics'
        IMAGE_TAG = 'v1'
        CONTAINER_NAME = 'shopnova-app'
        UAT_PORT = '7070'
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
                    rm -rf .jenkins-venv
                    python3 -m venv .jenkins-venv
                    . .jenkins-venv/bin/activate
                    pip install -r requirements.txt
                '''
            }
        }

        stage('Run Tests') {
            steps {
                sh '''
                    . .jenkins-venv/bin/activate
                    pytest -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                '''
            }
        }

        stage('Deploy to UAT') {
            steps {
                sh '''
                    docker rm -f ${CONTAINER_NAME} || true
                    docker run -d \
                      --name ${CONTAINER_NAME} \
                      --restart unless-stopped \
                      -p ${UAT_PORT}:7070 \
                      -e APP_ENV=UAT \
                      -e APP_VERSION=${BUILD_NUMBER} \
                      ${IMAGE_NAME}:${IMAGE_TAG}
                '''
            }
        }

        stage('UAT Health Validation') {
            steps {
                sh '''
                    sleep 5
                    curl --fail --silent --show-error http://localhost:${UAT_PORT}/health
                    echo
                    curl --fail --silent --show-error http://localhost:${UAT_PORT}/ready
                    echo
                '''
            }
        }
    }

    post {
        success {
            echo 'ShopNova UAT deployment succeeded.'
        }
        failure {
            echo 'ShopNova pipeline failed.'
        }
    }
}
