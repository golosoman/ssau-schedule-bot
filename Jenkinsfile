pipeline {
  agent any

  options {
    timestamps()
    disableConcurrentBuilds()
  }

  parameters {
    choice(
      name: 'PIPELINE_JOB',
      choices: [
        'deploy',
        'db-history',
        'db-current',
        'db-upgrade-head',
        'db-downgrade-1',
        'db-stamp-initial',
      ],
      description: 'Какой job выполнить в этом запуске'
    )
    choice(
      name: 'DB_MIGRATION_SERVICE',
      choices: ['worker', 'bot'],
      description: 'Какой docker-compose service использовать для миграций'
    )
    string(
      name: 'DB_STAMP_REVISION',
      defaultValue: '20260322_0001',
      description: 'Ревизия для db-stamp-initial'
    )
  }

  environment {
    APP_DIR = "/opt/apps/ssau-schedule-bot"
    APP_PARENT_DIR = "/opt/apps"
    REPO_URL = "https://github.com/golosoman/ssau-schedule-bot.git"
    DEPLOY_BRANCH = "main"
    COMPOSE_FILE = "docker-compose.yaml"
    BACKUP_DIR = "backups"
    BACKUP_KEEP = "10"
  }

  stages {
    stage('Checkout (для статуса)') {
      steps {
        checkout scm
      }
    }

    stage('Sync Repo On Host') {
      when {
        expression {
          params.PIPELINE_JOB != 'deploy' || env.BRANCH_NAME == env.DEPLOY_BRANCH
        }
      }
      steps {
        sh '''#!/usr/bin/env bash
          set -euo pipefail

          echo "Sync repo on host path: ${APP_DIR}"
          docker run --rm \
            --entrypoint /bin/sh \
            -e APP_DIR="${APP_DIR}" \
            -e REPO_URL="${REPO_URL}" \
            -e DEPLOY_BRANCH="${DEPLOY_BRANCH}" \
            -v "${APP_PARENT_DIR}:${APP_PARENT_DIR}" \
            alpine/git:latest -euxc '
              if [ ! -d "${APP_DIR}/.git" ]; then
                git clone "${REPO_URL}" "${APP_DIR}"
              fi

              cd "${APP_DIR}"
              git fetch --all --prune
              git checkout "${DEPLOY_BRANCH}"
              git reset --hard "origin/${DEPLOY_BRANCH}"
            '
        '''
      }
    }

    stage('Deploy (main only)') {
      when {
        allOf {
          branch 'main'
          expression { params.PIPELINE_JOB == 'deploy' }
        }
      }
      steps {
        sh '''#!/usr/bin/env bash
          set -euo pipefail

          JENKINS_IMAGE="$(docker inspect --format='{{.Config.Image}}' jenkins)"
          echo "Compose helper image: ${JENKINS_IMAGE}"

          docker run --rm \
            --user 0:0 \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "${APP_DIR}:${APP_DIR}" \
            -w "${APP_DIR}" \
            -e COMPOSE_FILE="${COMPOSE_FILE}" \
            -e BACKUP_DIR="${BACKUP_DIR}" \
            -e BACKUP_KEEP="${BACKUP_KEEP}" \
            "${JENKINS_IMAGE}" sh -euxc '
              docker compose -f "${COMPOSE_FILE}" stop || true

              if [ -f "data/ssau_schedule_bot.db" ]; then
                ts="$(date -u +%Y%m%dT%H%M%SZ)"
                mkdir -p "${BACKUP_DIR}"
                tar -czf "${BACKUP_DIR}/data-${ts}.tar.gz" data
                echo "Backup created: ${BACKUP_DIR}/data-${ts}.tar.gz"

                ls -1t "${BACKUP_DIR}"/data-*.tar.gz 2>/dev/null \
                  | tail -n +$((BACKUP_KEEP + 1)) \
                  | xargs -r rm -f
              else
                echo "Database file data/ssau_schedule_bot.db not found, backup skipped"
              fi

              docker compose -f "${COMPOSE_FILE}" up -d --build
              docker compose -f "${COMPOSE_FILE}" ps
            '
        '''
      }
    }

    stage('DB Migration: history') {
      when {
        expression { params.PIPELINE_JOB == 'db-history' }
      }
      steps {
        sh '''#!/usr/bin/env bash
          set -euo pipefail

          JENKINS_IMAGE="$(docker inspect --format='{{.Config.Image}}' jenkins)"
          echo "Compose helper image: ${JENKINS_IMAGE}"

          docker run --rm \
            --user 0:0 \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "${APP_DIR}:${APP_DIR}" \
            -w "${APP_DIR}" \
            -e COMPOSE_FILE="${COMPOSE_FILE}" \
            -e DB_MIGRATION_SERVICE="${DB_MIGRATION_SERVICE}" \
            "${JENKINS_IMAGE}" sh -euxc '
              docker compose -f "${COMPOSE_FILE}" run --rm --no-deps "${DB_MIGRATION_SERVICE}" alembic history
            '
        '''
      }
    }

    stage('DB Migration: current') {
      when {
        expression { params.PIPELINE_JOB == 'db-current' }
      }
      steps {
        sh '''#!/usr/bin/env bash
          set -euo pipefail

          JENKINS_IMAGE="$(docker inspect --format='{{.Config.Image}}' jenkins)"
          echo "Compose helper image: ${JENKINS_IMAGE}"

          docker run --rm \
            --user 0:0 \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "${APP_DIR}:${APP_DIR}" \
            -w "${APP_DIR}" \
            -e COMPOSE_FILE="${COMPOSE_FILE}" \
            -e DB_MIGRATION_SERVICE="${DB_MIGRATION_SERVICE}" \
            "${JENKINS_IMAGE}" sh -euxc '
              docker compose -f "${COMPOSE_FILE}" run --rm --no-deps "${DB_MIGRATION_SERVICE}" alembic current
            '
        '''
      }
    }

    stage('DB Migration: approval (write actions)') {
      when {
        expression {
          ['db-upgrade-head', 'db-downgrade-1', 'db-stamp-initial'].contains(params.PIPELINE_JOB)
        }
      }
      steps {
        input message: "Подтвердить выполнение ${params.PIPELINE_JOB} на ${env.APP_DIR}?", ok: 'Run'
      }
    }

    stage('DB Migration: upgrade head') {
      when {
        expression { params.PIPELINE_JOB == 'db-upgrade-head' }
      }
      steps {
        sh '''#!/usr/bin/env bash
          set -euo pipefail

          JENKINS_IMAGE="$(docker inspect --format='{{.Config.Image}}' jenkins)"
          echo "Compose helper image: ${JENKINS_IMAGE}"

          docker run --rm \
            --user 0:0 \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "${APP_DIR}:${APP_DIR}" \
            -w "${APP_DIR}" \
            -e COMPOSE_FILE="${COMPOSE_FILE}" \
            -e DB_MIGRATION_SERVICE="${DB_MIGRATION_SERVICE}" \
            "${JENKINS_IMAGE}" sh -euxc '
              docker compose -f "${COMPOSE_FILE}" run --rm --no-deps "${DB_MIGRATION_SERVICE}" alembic upgrade head
            '
        '''
      }
    }

    stage('DB Migration: downgrade -1') {
      when {
        expression { params.PIPELINE_JOB == 'db-downgrade-1' }
      }
      steps {
        sh '''#!/usr/bin/env bash
          set -euo pipefail

          JENKINS_IMAGE="$(docker inspect --format='{{.Config.Image}}' jenkins)"
          echo "Compose helper image: ${JENKINS_IMAGE}"

          docker run --rm \
            --user 0:0 \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "${APP_DIR}:${APP_DIR}" \
            -w "${APP_DIR}" \
            -e COMPOSE_FILE="${COMPOSE_FILE}" \
            -e DB_MIGRATION_SERVICE="${DB_MIGRATION_SERVICE}" \
            "${JENKINS_IMAGE}" sh -euxc '
              docker compose -f "${COMPOSE_FILE}" run --rm --no-deps "${DB_MIGRATION_SERVICE}" alembic downgrade -1
            '
        '''
      }
    }

    stage('DB Migration: stamp initial') {
      when {
        expression { params.PIPELINE_JOB == 'db-stamp-initial' }
      }
      steps {
        sh '''#!/usr/bin/env bash
          set -euo pipefail

          JENKINS_IMAGE="$(docker inspect --format='{{.Config.Image}}' jenkins)"
          echo "Compose helper image: ${JENKINS_IMAGE}"

          docker run --rm \
            --user 0:0 \
            -v /var/run/docker.sock:/var/run/docker.sock \
            -v "${APP_DIR}:${APP_DIR}" \
            -w "${APP_DIR}" \
            -e COMPOSE_FILE="${COMPOSE_FILE}" \
            -e DB_MIGRATION_SERVICE="${DB_MIGRATION_SERVICE}" \
            -e DB_STAMP_REVISION="${DB_STAMP_REVISION}" \
            "${JENKINS_IMAGE}" sh -euxc '
              docker compose -f "${COMPOSE_FILE}" run --rm --no-deps "${DB_MIGRATION_SERVICE}" alembic stamp "${DB_STAMP_REVISION}"
            '
        '''
      }
    }
  }
}
