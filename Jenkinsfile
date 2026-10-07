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

        KUBECONFIG = '/var/jenkins_home/.kube/config'

        UAT_NAMESPACE = 'uat'
        UAT_DEPLOYMENT = 'shopnova-uat'
        UAT_CONTAINER = 'shopnova'
        UAT_PORT = '30071'

        PROD_HOST = '172.198.162.209'
        PROD_USER = 'azureuser'
        PROD_NAMESPACE = 'prod'
        PROD_DEPLOYMENT = 'shopnova-prod'
        PROD_CONTAINER = 'shopnova'
        PROD_PORT = '30070'
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

                    python -m pip install --timeout 120 --retries 10 --disable-pip-version-check -r requirements.txt
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

                    docker build \
                      -t ${IMAGE_NAME}:${IMAGE_TAG} \
                      .

                    docker image inspect \
                      ${IMAGE_NAME}:${IMAGE_TAG} \
                      > /dev/null
                '''
            }
        }

        stage('Import Image to UAT K3s') {
            steps {
                sh '''
                    set -e

                    rm -f ${IMAGE_ARCHIVE}

                    docker save \
                      ${IMAGE_NAME}:${IMAGE_TAG} \
                      -o ${IMAGE_ARCHIVE}

                    /usr/local/bin/k3s ctr images import \
                      ${IMAGE_ARCHIVE}
                '''
            }
        }

        stage('Deploy to Kubernetes UAT') {
            steps {
                sh '''
                    set -e

                    /usr/local/bin/k3s kubectl -n ${UAT_NAMESPACE} set image \
                      deployment/${UAT_DEPLOYMENT} \
                      ${UAT_CONTAINER}=docker.io/library/${IMAGE_NAME}:${IMAGE_TAG}

                    /usr/local/bin/k3s kubectl -n ${UAT_NAMESPACE} set env \
                      deployment/${UAT_DEPLOYMENT} \
                      APP_ENV=UAT-K8S \
                      APP_VERSION=${BUILD_NUMBER}

                    /usr/local/bin/k3s kubectl -n ${UAT_NAMESPACE} rollout status \
                      deployment/${UAT_DEPLOYMENT} \
                      --timeout=300s
                '''
            }
        }

        stage('Validate UAT') {
            steps {
                sh '''
                    set -e

                    sleep 5

                    echo "Checking UAT health endpoint..."

                    curl --fail \
                      --silent \
                      --show-error \
                      http://shopenow:${UAT_PORT}/health

                    echo ""

                    echo "Checking UAT readiness endpoint..."

                    curl --fail \
                      --silent \
                      --show-error \
                      http://localhost:${UAT_PORT}/ready

                    echo ""

                    /usr/local/bin/k3s kubectl -n ${UAT_NAMESPACE} \
                      get deployment,pods,service
                '''
            }
        }

        stage('Approve Production Deployment') {
            steps {
                timeout(time: 30, unit: 'MINUTES') {
                    input(
                        message: "UAT Build ${BUILD_NUMBER} is healthy. Deploy this build to Production?",
                        ok: 'Deploy to PROD'
                    )
                }
            }
        }

        stage('Verify PROD Connection') {
            steps {
                sh '''
                    set -e

                    ssh \
                      -o BatchMode=yes \
                      -o StrictHostKeyChecking=accept-new \
                      ${PROD_USER}@${PROD_HOST} \
                      hostname
                '''
            }
        }

        stage('Transfer Image to PROD') {
            steps {
                sh '''
                    set -e

                    scp \
                      -o BatchMode=yes \
                      -o StrictHostKeyChecking=accept-new \
                      ${IMAGE_ARCHIVE} \
                      ${PROD_USER}@${PROD_HOST}:/tmp/${IMAGE_ARCHIVE}
                '''
            }
        }

        stage('Deploy to Kubernetes PROD') {
            steps {
                sh '''
                    set -e

                    ssh \
                      -o BatchMode=yes \
                      -o StrictHostKeyChecking=accept-new \
                      ${PROD_USER}@${PROD_HOST} \
                      "/usr/local/bin/k3s ctr images import /tmp/${IMAGE_ARCHIVE} && \
                       /usr/local/bin/k3s kubectl -n ${PROD_NAMESPACE} set image \
                       deployment/${PROD_DEPLOYMENT} \
                       ${PROD_CONTAINER}=docker.io/library/${IMAGE_NAME}:${IMAGE_TAG} && \
                       /usr/local/bin/k3s kubectl -n ${PROD_NAMESPACE} set env \
                       deployment/${PROD_DEPLOYMENT} \
                       APP_ENV=PROD \
                       APP_VERSION=${BUILD_NUMBER} && \
                       /usr/local/bin/k3s kubectl -n ${PROD_NAMESPACE} rollout status \
                       deployment/${PROD_DEPLOYMENT} \
                       --timeout=300s && \
                       rm -f /tmp/${IMAGE_ARCHIVE}"
                '''
            }
        }

        stage('Validate PROD') {
            steps {
                sh '''
                    set -e

                    sleep 5

                    ssh \
                      -o BatchMode=yes \
                      -o StrictHostKeyChecking=accept-new \
                      ${PROD_USER}@${PROD_HOST} \
                      "echo 'Checking PROD health endpoint...' && \
                       curl --fail --silent --show-error \
                       http://shopnova-prod:${PROD_PORT}/health && \
                       echo && \
                       echo 'Checking PROD readiness endpoint...' && \
                       curl --fail --silent --show-error \
                       http://localhost:${PROD_PORT}/ready && \
                       echo && \
                       /usr/local/bin/k3s kubectl \
                       -n ${PROD_NAMESPACE} \
                       get deployment,pods,service"
                '''
            }
        }
    }

    post {
        success {
            echo "ShopNova Build ${BUILD_NUMBER} deployed successfully to UAT and PROD."
        }

        failure {
            echo "ShopNova Build ${BUILD_NUMBER} failed. Review the failed stage."
        }

        aborted {
            echo "ShopNova Build ${BUILD_NUMBER} was not promoted to PROD."
        }

        always {
            sh 'rm -f shopnova-logistics.tar || true'
        }
    }
}
