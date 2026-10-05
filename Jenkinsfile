pipeline {
    agent any

    options {
        disableConcurrentBuilds()
        timestamps()
        buildDiscarder(logRotator(numToKeepStr: '10'))
    }

    environment {
        IMAGE_NAME = 'shopnova-logistics'
        IMAGE_TAG = "${BUILD_NUMBER}"
        IMAGE_ARCHIVE = 'shopnova-logistics.tar'
        KUBE_NAMESPACE = 'uat'
        KUBE_DEPLOYMENT = 'shopnova-uat'
        KUBE_CONTAINER = 'shopnova'
        UAT_PORT = '30071'
        KUBECONFIG = '/home/azureuser/.kube/config'
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
                    set -e
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
                    set -e
                    . .jenkins-venv/bin/activate
                    pytest -v
                '''
            }
        }

        stage('Docker Build') {
            steps {
                sh '''
                    set -e
                    docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .
                    docker image inspect ${IMAGE_NAME}:${IMAGE_TAG} >/dev/null
                '''
            }
        }

        stage('Import Image to K3s') {
            steps {
                sh '''
                    set -e
                    rm -f ${IMAGE_ARCHIVE}
                    docker save ${IMAGE_NAME}:${IMAGE_TAG} -o ${IMAGE_ARCHIVE}
                    sudo -n /usr/local/bin/k3s ctr images import ${IMAGE_ARCHIVE}
                    sudo -n /usr/local/bin/k3s ctr images list | grep ${IMAGE_NAME} | grep ${IMAGE_TAG}
                '''
            }
        }

        stage('Deploy to Kubernetes UAT') {
            steps {
                sh '''
                    set -e
                    kubectl -n ${KUBE_NAMESPACE} set image \
                      deployment/${KUBE_DEPLOYMENT} \
                      ${KUBE_CONTAINER}=docker.io/library/${IMAGE_NAME}:${IMAGE_TAG}

                    kubectl -n ${KUBE_NAMESPACE} set env \
                      deployment/${KUBE_DEPLOYMENT} \
                      APP_ENV=UAT-K8S \
                      APP_VERSION=${BUILD_NUMBER}

                    kubectl -n ${KUBE_NAMESPACE} rollout status \
                      deployment/${KUBE_DEPLOYMENT} \
                      --timeout=300s
                '''
            }
        }

        stage('UAT Health Validation') {
            steps {
                sh '''
                    set -e
                    sleep 5
                    curl --fail --silent --show-error \
                      http://localhost:${UAT_PORT}/health
                    echo
                    curl --fail --silent --show-error \
                      http://localhost:${UAT_PORT}/ready
                    echo
                    kubectl -n ${KUBE_NAMESPACE} get deployment,pods,service
                '''
            }
        }
    }

    post {
        success {
            echo "ShopNova Kubernetes UAT deployment ${BUILD_NUMBER} succeeded."
        }
        failure {
            echo "ShopNova Kubernetes UAT deployment ${BUILD_NUMBER} failed."
        }
        always {
            sh 'rm -f shopnova-logistics.tar || true'
        }
    }
}
