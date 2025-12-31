pipeline {
    agent any

    environment {
        BRANCH = "${env.GIT_BRANCH.split('/').last()}"
        DOCKER_USER = 'surajlearn'
        IMAGE_NAME = "${DOCKER_USER}/tubedash-app"
        APP_PORT = "${BRANCH == 'main' ? '8000' : '8001' }"
        DB_PORT =  "${BRANCH == 'main' ? '5431' : '5432'}"
        PROD_PATH = "/home/robo/production/tubedash" 
        REDIS_HOST = 'redis-cache'
        DATABASE_URL = "postgresql://user:password@postgres-db:5432/tubedash"
        DEPLOY_URL = "${BRANCH == 'main' ? 'http://192.168.181.182:8000' : 'http://192.168.181.182:8001'}"       
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

        stage('Deploy') {
            steps {
                script {

                    if (BRANCH == 'dev') {
                        echo "Deploying to Testing Enviroment (Local)....."
                        sh "APP_PORT=8001 DB_PORT=5432 docker compose up -d --pull always"
                    }
                    else if (BRANCH == 'main') {
                        echo "Deploying to Production Environment (Remote via SSH)...."
                        sshagent (['prod-server-key'])
                        {
                            sh """ 
                                   echo "IMAGE_NAME=${IMAGE_NAME}" > .env 
                                   echo "BRANCH=${BRANCH}" >> .env 
                                   echo "APP_PORT=${APP_PORT}" >> .env
                                   echo "DB_PORT=${DB_PORT}" >> .env
                                   echo "DATABASE_URL=${DATABASE_URL}" >> .env
                                   echo "REDIS_HOST=${REDIS_HOST}" >> .env 
                              """

                            sh "scp -o StrictHostKeyChecking=no .env robo@localhost:${PROD_PATH}/.env"   
                            sh "ssh -o StrictHostKeyChecking=no robo@localhost 'cd ${PROD_PATH} && git pull origin main && docker compose up -d --pull always '"
                        }
                    }
                }
            }
        }
    }

    post { 
        success {
            emailext (
                subject: "Build Success: ${currentBuild.fullDisplayName}",
                body: """ 
                     Build Status: SUCCESS
                     Branch: ${BRANCH}
                     Access your App here: ${DEPLOY_URL}
                     Build URL: ${env.BUILD_URL}
                """,
                to: 'surajlearninig@gmail.com'
            )
        }
        failure {
             emailext (
                subject: "Build Failed: ${currentBuild.fullDisplayName}",
                body: """
                     Build Status: FAILED
                     Branch: ${BRANCH}
                     Check logs here: ${env.BUILD_URL}
                """,
                to: 'surajlearninig@gmail.com'
            )
        }
    }
}