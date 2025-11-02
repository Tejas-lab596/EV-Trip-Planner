pipeline {
  agent any

  environment {
    DOCKER_COMPOSE = 'docker compose'      // Compose V2

    // Pull from Jenkins Credentials by ID (must exist)
    DB_HOST     = credentials('rds-host')       // Secret text
    DB_PORT     = '3306'
    DB_USER     = credentials('rds-user')       // Secret text
    DB_PASSWORD = credentials('rds-password')   // Secret text
    DB_NAME     = credentials('rds-dbname')     // Secret text
    SECRET_KEY  = credentials('app-secret')     // Secret text
  }

  options {
    timestamps()
    ansiColor('xterm')
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Prepare Docker') {
      steps {
        sh 'docker version'
        sh 'docker compose version || true'
        sh 'id -nG'
      }
    }

    stage('Build images') {
      steps {
        // If compose is at repo root, remove dir('EV-Trip-Planner')
        dir('EV-Trip-Planner') {
          sh "${DOCKER_COMPOSE} build --pull"
        }
      }
    }

    stage('Deploy (Compose up)') {
      steps {
        dir('EV-Trip-Planner') {
          sh '''
cat > backend/.env <<EOF
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=${DB_NAME}
SECRET_KEY=${SECRET_KEY}
EOF
'''
          sh "${DOCKER_COMPOSE} up -d --remove-orphans"
        }
      }
    }
  }

  post {
    success { echo 'Deployment completed successfully!' }
    failure { echo 'Deployment failed.' }
    always  { sh 'docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"' }
  }
}
