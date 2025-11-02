pipeline {
  agent any

  environment {
    DOCKER_COMPOSE = 'docker compose'
    // A second safeguard in case someone removes `name:` from compose:
    COMPOSE_PROJECT_NAME = 'evtrip'

    DB_HOST     = credentials('rds-host')
    DB_PORT     = '3306'
    DB_USER     = credentials('rds-user')
    DB_PASSWORD = credentials('rds-password')
    DB_NAME     = credentials('rds-dbname')
    SECRET_KEY  = credentials('app-secret')
  }

  options { timestamps() }

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
        sh "${DOCKER_COMPOSE} build --pull"
      }
    }

    stage('Deploy (Compose up)') {
      steps {
        // Write runtime env for backend
        sh '''
          mkdir -p backend
          cat > backend/.env <<EOF
DB_HOST=${DB_HOST}
DB_PORT=${DB_PORT}
DB_USER=${DB_USER}
DB_PASSWORD=${DB_PASSWORD}
DB_NAME=${DB_NAME}
SECRET_KEY=${SECRET_KEY}
EOF
        '''
        // Make deploy idempotent: stop old stack of the same project
        sh "${DOCKER_COMPOSE} down --remove-orphans || true"
        // Bring up fresh
        sh "${DOCKER_COMPOSE} up -d --remove-orphans --force-recreate"
      }
    }

    stage('Smoke check') {
      steps {
        // Project name is fixed, container will be 'evtrip-backend-1'
        sh 'docker exec $(docker ps --filter "name=evtrip-backend" --format "{{.ID}}") sh -lc "curl -fsS http://localhost:5000/health"'
      }
    }
  }

  post {
    success { echo '✅ Deployment completed successfully!' }
    failure { echo '❌ Deployment failed.' }
    always  {
      sh 'docker ps --format "table {{.Names}}\\t{{.Status}}\\t{{.Ports}}"'
    }
  }
}
