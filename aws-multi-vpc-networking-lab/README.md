# AWS Multi-VPC Networking Lab

This project demonstrates a full hands-on AWS networking environment that simulates a real-world multi-VPC production architecture.  
It includes VPC design, routing, peering, NAT, ALB, private application hosting, IAM roles, VPC endpoints, and secure access patterns.

---

## 🚀 Architecture Summary

### **VPC 1 — App VPC (10.10.0.0/16)**
Holds all application-related resources:

- **Public Subnets**  
  - Bastion Host (Public EC2)  
  - NAT Gateway  
  - Application Load Balancer (Internet-facing)

- **Private Subnets**  
  - Private App EC2 (no Public IP)  
  - Application served via ALB only  
  - IAM role for S3 access  
  - VPC S3 Gateway Endpoint  

- **Flow Logs** → CloudWatch

---

### **VPC 2 — Shared Services VPC (10.20.0.0/16)**

Contains:
- Private shared EC2 instance
- Route table set for peering and future monitoring/jump-host workloads
- Connected to App VPC via VPC Peering

---

## 🔗 Connectivity Overview

- SSH access → via Bastion Host only  
- ALB → forwards HTTP traffic to Private App EC2  
- Private EC2 → Internet via NAT Gateway  
- App VPC ↔ Shared VPC → via VPC Peering  
- Private EC2 → S3 via VPC Endpoint (no Internet required)  
- CloudWatch Flow Logs used to trace ACCEPT/REJECT traffic

---

## 🧩 Networking Components

### **Security Groups**
- Bastion SG → allows SSH from my IP  
- App SG → allows HTTP from ALB SG, SSH from Bastion SG  
- Shared SG → allows internal traffic from App VPC CIDR

### **Route Tables**
- Public RT → IGW + Peering route  
- Private RT → NAT + Peering + S3 Endpoint  
- Shared RT → Peering route to App VPC

### **VPC Endpoints**
- S3 Gateway Endpoint → used by private EC2 without Internet

---

## 🧪 Skills Demonstrated

- VPC design and multi-VPC architecture  
- Subnetting, routing, CIDRs  
- Public vs private networking  
- NAT Gateway vs Internet Gateway  
- Application Load Balancer  
- VPC Peering routing  
- IAM roles for EC2 (S3 full access without credentials)  
- VPC Endpoints (private access to AWS services)  
- CloudWatch Flow Logs  
- Bastion Host SSH pattern  
- Private application hosting over ALB  

---

## 🗺️ Architecture Diagram

(Import the `.drawio` file below)

---

## 📦 How to Reproduce

1. Create two VPCs with distinct CIDRs  
2. Create public + private subnets in multiple AZs  
3. Attach IGW to App VPC  
4. Deploy Bastion EC2 in public subnet  
5. Deploy Private App EC2 in private subnet  
6. Create ALB in public subnets  
7. Configure SGs for Bastion, ALB, App  
8. Add NAT Gateway  
9. Add S3 Gateway Endpoint  
10. Create VPC Peering + update both route tables  
11. Enable Flow Logs  
12. Test connectivity (SSH + curl + S3 access)  

---

## 🎯 Conclusion

This project gave me practical experience in real AWS networking, secure architecture patterns, and multi-VPC connectivity — all critical foundations for DevOps and cloud engineering.

