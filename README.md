# Task Manager DevOps

Production-style DevOps portfolio project built with FastAPI, PostgreSQL, Docker, Kubernetes, Helm, Terraform, AWS EKS and GitHub Actions.

## Architecture

Developer → GitHub → GitHub Actions → GHCR → AWS EKS → Helm → FastAPI → PostgreSQL

## Local

```bash
cp .env.example .env
docker compose up -d --build
curl http://localhost:8000/health
```

Frontend: http://localhost:8000/static/index.html

## Tests

```bash
export DATABASE_URL=sqlite://
python -m pytest -v
ruff check app/ tests/
bandit -r app/ -ll
```

## Terraform

```bash
cd terraform
cp terraform.tfvars.example terraform.tfvars
terraform init
terraform fmt -recursive
terraform validate
terraform plan
terraform apply
```

Then:

```bash
aws eks update-kubeconfig --region eu-central-1 --name task-manager-eks
kubectl get nodes
```

Copy the `github_actions_role_arn` Terraform output into the GitHub Actions secret `AWS_ROLE_TO_ASSUME`.

Set GitHub Actions secret `POSTGRES_PASSWORD` to a strong database password.

## Kubernetes / Helm

PostgreSQL is deployed with a StatefulSet and a PVC backed by the AWS EBS CSI driver.

```bash
kubectl apply -f deploy/postgres/namespace.yaml
kubectl apply -f deploy/postgres/storageclass.yaml
# Create the postgres secret securely; do not commit the real password.
kubectl apply -f deploy/postgres/service.yaml
kubectl apply -f deploy/postgres/statefulset.yaml
```

Application:

```bash
helm upgrade --install task-manager ./helm/task-manager   --namespace task-manager   --create-namespace   --set image.repository=ghcr.io/11abdo1a7med-collab/task-manager-devops   --set image.tag=latest   --set secrets.databaseUrl='postgresql://taskuser:PASSWORD@postgres:5432/taskmanager'   --wait
```

## CI/CD

Pull requests run lint, tests and Bandit.

Pushes to `main` build and push the image to GHCR, authenticate to AWS with GitHub OIDC, deploy PostgreSQL, deploy the application with Helm, and verify the rollout.

Trivy is intentionally disabled for the current project phase.

## Important

- Never commit `.env`, real passwords, AWS access keys, or kubeconfig files.
- The repository's `main` branch is the project baseline.
- The old `feature/docker-setup` branch should not be merged wholesale.
