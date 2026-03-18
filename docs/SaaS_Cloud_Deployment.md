# SaaS Cloud Deployment Guide: Agricultural AI Platform

## 1. AWS Infrastructure (Recommended)

### 🚀 Compute: AWS EC2 (t3.medium or larger)
- Runs the **Docker Engine** housing our API and Nginx.
- Use **AWS Target Group** and **Application Load Balancer (ALB)** for auto-scaling and SSL termination.

### 🗄️ Database: AWS RDS (PostgreSQL)
- **Do not** run your database inside Docker in production.
- Use a Managed RDS instance for automated backups, high availability (Multi-AZ), and better performance.
- Update your `DATABASE_URL` in `.env` to point to the RDS endpoint.

### 🖼️ Storage: AWS S3
- Store large assets: Pest detection images, harvested CSV data, and model binary files (`.h5`, `.pkl`).
- Benefits: Infinite scalability and high durability.

---

## 2. Platform Folder Structure

```text
/                      # Root Directory
├── flask_api/         # Core API Service
│   ├── app/           # Flask Logic
│   ├── nginx/         # Nginx Proxy Configuration
│   ├── Dockerfile     # Image Build Instructions
│   └── requirements.txt
├── .github/           # Automation
│   └── workflows/     # CI/CD (GitHub Actions)
├── docker-compose.yml # Dev/Local Orchestration
└── .env               # Secrets (Never commit to Git!)
```

---

## 3. Production Deployment Steps

### Step 1: Environment Setup
Clone the repo to your EC2 instance and create a production `.env` file:
```bash
DB_USER=agro_admin
DB_PASSWORD=secure_rds_password
DB_NAME=agro_prod
SECRET_KEY=$(python3 -c 'import os; print(os.urandom(24).hex())')
JWT_SECRET_KEY=$(python3 -c 'import os; print(os.urandom(24).hex())')
```

### Step 2: Build & Launch
Run the platform using Docker Compose:
```bash
docker-compose up -d --build
```

### Step 3: SSL Setup (HTTPS)
Use **Certbot (Let's Encrypt)** on your Nginx container to secure communications:
```bash
docker exec -it agro_nginx certbot --nginx -d yourdomain.com
```

---

## 4. Scaling Strategy

1. **Horizontal Scaling**: Launch multiple EC2 instances running the API Docker container behind the AWS ALB.
2. **Caching**: Integrate **Redis** (AWS ElastiCache) for faster JWT verification and API response caching.
3. **Database Level**: Use **Read Replicas** in AWS RDS to handle high fetch volumes for historcal crop data.

---
*Architected for: Unlimited Scaling*
