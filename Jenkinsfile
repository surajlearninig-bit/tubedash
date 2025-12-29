pipeline {
    agent any

    environment {
        DOCKER_USER = 'surajlearn'
        IMAGE_NAME = "${DOCKER_USER}/tubedash-app"
        APP_PORT = "${env.BRANCH_NAME == 'main' ? '8000' : '8001' }"
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
                    sh "docker build -t ${IMAGE_NAME}:${env.BRANCH_NAME}"
                    sh "docker build -t ${IMAGE_NAME}:${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
                }
            }
        }

        stage('Push to Docker') {
            steps {
                script {
                    withCredentials([usernamePassword(credentialsID: 'docker-hub-creds', passwordVariable: 'DOCKER_PASS', usernameVariable: 'DOCKER_USER')]) 
                    {
                        sh "echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin"
                        sh "docker push ${IMAGE_NAME}:${env.BRANCH_NAME}"
                        sh "docker push ${IMAGE_NAME}:${env.BRANCH_NAME}-${env.BUILD_NUMBER}"
                    }
                }
            }
        }

        stage('Deploy') {
            steps {
                script {
                    if (env.BRANCH_NAME == 'dev') {
                        echo "Deploying to Testing Enviroment (Local)....."
                        sh "docker compose up -d --pull always"
                    }
                    else if (env.BRANCH_NAME == 'main') {
                        echo "Deploying to Production Environment (Remote via SSH)...."
                        sshagent (['prod-server-key'])
                        {
                            sh """ ssh -o StrictHostKeyChecking=no robo@localhost 'cd ${PROD_PATH} && git pull origin main && docker compose up -d --pull always ' """
                        }
                    }
                }
            }
        }
    }
}