pipeline {
    agent any

    environment {
        BRANCH = "${env.GIT_BRANCH.split('/').last()}"
        DOCKER_USER = 'surajlearn'
        IMAGE_NAME = "${DOCKER_USER}/tubedash-app"
        APP_PORT = "${BRANCH== 'main' ? '8000' : '8001' }"
        PROD_PATH = "/home/robo/production/tubedash"        
    }

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Build') {
            steps {
                script {
                    sh "docker build -t ${IMAGE_NAME}:${BRANCH} . "
                    sh "docker build -t ${IMAGE_NAME}:${BRANCH}-${env.BUILD_NUMBER} . "
                }
            }
        }

        stage('Push to Docker') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: 'docker-hub-cred', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) 
                    {
                        sh "echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin"
                        sh "docker push ${IMAGE_NAME}:${BRANCH}"
                        sh "docker push ${IMAGE_NAME}:${BRANCH}-${env.BUILD_NUMBER}"
                    }
                }
            }
        }

        stage('Deploy') {-
            steps {
                script {

                    sh "ls -R"
                    if (BRANCH == 'dev') {
                        echo "Deploying to Testing Enviroment (Local)....."
                        sh "APP_PORT=8001 docker compose up -d --pull always"
                    }
                    else if (BRANCH == 'main') {
                        echo "Deploying to Production Environment (Remote via SSH)...."
                        sshagent (['prod-server-key'])
                        {
                            sh """ ssh -o StrictHostKeyChecking=no robo@localhost 'cd ${PROD_PATH} && git pull origin main && export IMAGE_NAME=${IMAGE_NAME} && export BRANCH=${BRANCH} && APP_PORT=8000 docker compose up -d --pull always ' """
                        }
                    }
                }
            }
        }
    }
}