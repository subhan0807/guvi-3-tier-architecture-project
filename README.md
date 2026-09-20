# GUVI 3-Tier AWS Architecture

## Project Overview

This project implements a 3-tier web application on AWS using a public web tier, private application tier, and private database tier.

The application provides a feedback form. Users access the application through an internet-facing Application Load Balancer. Nginx on the Web EC2 forwards API requests to an internal Application Load Balancer, which forwards them to a Flask application. Flask stores feedback in an Amazon RDS MySQL database.

## Architecture

Internet
  |
  | HTTP :80
  v
Public Application Load Balancer
  |
  | HTTP :80
  v
Web EC2 / Nginx
  |
  | HTTP/TCP :5000
  v
Internal Application Load Balancer
  |
  | HTTP/TCP :5000
  v
Flask Application EC2
  |
  | MySQL :3306
  v
Amazon RDS MySQL

## AWS Services Used

- Amazon VPC
- EC2
- Application Load Balancer
- Auto Scaling Group (Web tier bonus)
- NAT Gateway
- Internet Gateway
- Security Groups
- Amazon RDS for MySQL
- CloudWatch/EC2 health checks

## VPC and Networking

VPC:
- Name: guvi-3tier-vpc
- CIDR: 10.0.0.0/16
- Region: ap-south-1 (Mumbai)

Subnets:

Public Web:
- guvi-public-web-1a - 10.0.1.0/24
- guvi-public-web-1b - 10.0.2.0/24

Private App:
- guvi-private-app-1a - 10.0.11.0/24
- guvi-private-app-1b - 10.0.12.0/24

Private DB:
- guvi-private-db-1a - 10.0.21.0/24
- guvi-private-db-1b - 10.0.22.0/24

## Route Tables

Public Route Table:
- 10.0.0.0/16 -> local
- 0.0.0.0/0 -> Internet Gateway

Private App Route Table:
- 10.0.0.0/16 -> local
- 0.0.0.0/0 -> NAT Gateway

Private DB Route Table:
- 10.0.0.0/16 -> local

## Security Groups

### guvi-public-alb-sg
- Inbound TCP 80 from 0.0.0.0/0
- Outbound allowed

### guvi-web-sg
- SSH 22 from administrator IP
- HTTP 80 from guvi-public-alb-sg
- Outbound allowed

### guvi-internal-alb-sg
- TCP 5000 from guvi-web-sg
- Outbound allowed

### guvi-app-sg
- SSH 22 from administrator IP
- TCP 5000 from guvi-internal-alb-sg
- Outbound allowed

### guvi-db-sg
- MySQL TCP 3306 from guvi-app-sg
- Outbound allowed

## Web Tier

The Web tier uses EC2 instances running Nginx.

Nginx serves the feedback form on port 80 and forwards `/api/` requests to the internal Application Load Balancer.

## Application Tier

The application tier runs a Python Flask application on port 5000.

Health check:
- `GET /`
- Expected response: `{"status":"Flask is running"}`

Feedback endpoint:
- `POST /submit`

## Database Tier

Amazon RDS MySQL stores submitted feedback.

Database:
- feedbackdb

Table:
- feedback

Columns:
- id
- name
- email
- feedback
- created

## Nginx Reverse Proxy

The Web tier uses:

`/api/` -> Internal ALB -> Flask application

The deployed Nginx configuration uses the internal ALB DNS name. The repository contains a sanitized configuration with the DNS name replaced by `YOUR_INTERNAL_ALB_DNS`.

## Load Balancers

Public ALB:
- guvi-public-alb
- Internet-facing
- Listener: HTTP :80
- Target group: guvi-web-tg

Internal ALB:
- guvi-internal-alb
- Internal/private
- Listener: HTTP :5000
- Target group: guvi-app-tg

## Web Auto Scaling Bonus

A Web Auto Scaling Group was implemented using:
- AMI: guvi-web-ami
- Launch Template: guvi-web-launch-template
- ASG: guvi-web-asg
- Desired capacity: 2
- Minimum: 2
- Maximum: 2
- Availability Zones: ap-south-1a and ap-south-1b

The Web target group was verified with 3 healthy targets during testing, including the original Web instance and the two ASG instances.

## Database Schema

See `database/schema.sql`.

## Configuration

Do not store passwords, AWS access keys, private keys, or other secrets in this repository.

The Flask application reads database settings from environment variables:

- DB_HOST
- DB_USER
- DB_PASSWORD
- DB_NAME
- DB_PORT

Example:

```bash
export DB_HOST="your-rds-endpoint"
export DB_USER="admin"
export DB_PASSWORD="your-password"
export DB_NAME="feedbackdb"
export DB_PORT="3306"
```

## Validation

The following end-to-end flow was successfully tested:

1. User opens the Public ALB.
2. Public ALB forwards traffic to the Web tier.
3. Nginx serves the feedback form.
4. Browser sends `/api/submit`.
5. Nginx forwards the request to the Internal ALB.
6. Internal ALB forwards to Flask on port 5000.
7. Flask connects to RDS MySQL on port 3306.
8. Feedback is inserted into the `feedback` table.
9. The inserted record can be verified using:

```sql
USE feedbackdb;
SELECT * FROM feedback;
```

## Repository Structure

```text
guvi-3-tier-architecture/
├── README.md
├── web/
│   ├── index.html
│   └── nginx.conf
├── app/
│   ├── app.py
│   └── requirements.txt
└── database/
    └── schema.sql
```

## Project Result

The project demonstrates a functional AWS 3-tier architecture with separated Web, Application, and Database tiers, controlled network access using Security Groups, public and internal Application Load Balancers, Nginx reverse proxying, Flask-to-RDS connectivity, and Web-tier Auto Scaling.
