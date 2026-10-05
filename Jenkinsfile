pipeline {
    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Install Dependencies') {
            steps {
                sh '''
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
                docker build -t shopnova-logistics:v1 .
                '''
            }
        }

    }
}
