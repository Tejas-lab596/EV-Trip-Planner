pipeline {
    agent any

    environment {
        DOCKER_COMPOSE = "/usr/local/bin/docker-compose"
    }

    stages {
        stage('Checkout Code') {
            steps {
                git branch: 'main', url: 'https://github.com/<yourusername>/ev-trip-planner.git'
            }
        }

        stage('Build Containers') {
            steps {
                sh 'sudo docker-compose build'
            }
        }

        stage('Deploy Containers') {
            steps {
                sh 'sudo docker-compose down'
                sh 'sudo docker-compose up -d'
            }
        }
    }

    post {
        success {
            echo '✅ Deployment completed successfully!'
        }
        failure {
            echo '❌ Deployment failed.'
        }
    }
}
