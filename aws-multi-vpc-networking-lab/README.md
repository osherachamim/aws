# AWS Multi-VPC Networking Lab

This project demonstrates a real-world AWS networking environment that simulates multi-VPC production architecture.  
It includes VPC design, routing, peering, NAT, ALB, IAM roles, VPC endpoints, and secure access patterns across isolated networks.

---
## 🗺️ Architecture Diagram
(Import the `.drawio` file into draw.io)
---
## 🚀 Architecture Summary

### **VPC 1 — App VPC (10.10.0.0/16)**
Contains all application-related components:

#### Public Subnets
- Bastion Host (Public EC2)
- NAT Gateway
- Application Load Balancer (Internet-facing)

#### Private Subnets
- Private App EC2 (no Public IP)
- Application traffic served via ALB only
- IAM role allowing S3 access (no credentials needed)
- S3 Gateway VPC Endpoint for internal AWS communication

#### Additional
- Flow Logs → CloudWatch Logs

---

### **VPC 2 — Shared Services VPC (10.20.0.0/16)**

Includes:
- Shared Private EC2 instance
- Security group allowing only VPC-internal/peering traffic
- Route table configured for VPC Peering

Used for shared workloads, testing private routing, and cross-VPC communication.

---

## 🔗 Connectivity Overview

- SSH access → Bastion Host only  
- ALB (public) → forwards HTTP traffic to App EC2 (private)  
- Private EC2 → Internet via NAT Gateway  
- Private EC2 → S3 via S3 Gateway Endpoint (no Internet required)  
- VPC Peering → App VPC ↔ Shared VPC  
- CloudWatch Flow Logs → Observe ACCEPT/REJECT network traffic  

---

## 🧩 Networking Components

### **Security Groups**
- **Bastion SG** → SSH allowed from my IP  
- **App SG** → HTTP allowed from ALB SG, SSH allowed from Bastion SG  
- **Shared SG** → Allows internal traffic from App VPC CIDR

---

### **Route Tables**
- **Public RT (App VPC)**  
  - `0.0.0.0/0` → IGW  
  - `10.20.0.0/16` → Peering Connection  

- **Private RT (App VPC)**  
  - `0.0.0.0/0` → NAT Gateway  
  - `10.20.0.0/16` → Peering Connection  
  - `pl-xxxx` → S3 Gateway Endpoint  

- **Shared VPC RT**  
  - `10.10.0.0/16` → Peering Connection  

---

## 🔍 NAT Gateway vs S3 VPC Endpoint (Important Clarification)

The private EC2 instance uses **two different outbound paths**:

### **1) NAT Gateway — for public Internet**
Used ONLY for:
- `yum update`
- Installing packages
- Curl to external sites
- Any outbound public IP communication

This is traditional Internet access from a private subnet.

---

### **2) S3 Gateway VPC Endpoint — for AWS internal traffic**
Used for:
- Accessing S3 buckets  
- Listing / downloading / uploading objects  
- IAM role authentication (instance metadata + STS)

Advantages:
- No Internet required  
- Does NOT use the NAT Gateway  
- Private, secure, cheaper, faster  

**In this project:**  
S3 access is done **exclusively via the VPC Endpoint**, not through the NAT.

---

## 🧪 Skills Demonstrated

- VPC design, multi-VPC architecture  
- Subnetting and CIDR planning  
- Public vs private subnet separation  
- NAT Gateway vs Internet Gateway  
- Application Load Balancer (ALB)  
- EC2 IAM roles for secure S3 access  
- VPC Peering setup and routing  
- Using VPC S3 Gateway Endpoints  
- CloudWatch Flow Logs analysis  
- Bastion Host SSH access pattern  
- Private app hosting behind ALB  

---

## 📦 Steps to Reproduce

1. Create two VPCs with non-overlapping CIDRs  
2. Create public + private subnets in App VPC  
3. Attach Internet Gateway  
4. Deploy Bastion EC2 in public subnet  
5. Deploy Private App EC2 in private subnet  
6. Create ALB → target group → App EC2  
7. Configure SGs for Bastion, ALB, App  
8. Create NAT Gateway in public subnet  
9. Create S3 Gateway VPC Endpoint  
10. Create VPC Peering between VPCs  
11. Update route tables on both sides  
12. Enable VPC Flow Logs  
13. Test connectivity (SSH, curl, S3 access, peering ping)  

---

## 🎯 Conclusion

This project demonstrates real AWS production networking patterns using isolated VPCs, private workloads, secure access design, and cross-VPC communication.  
It reflects best practices for DevOps, Cloud Engineering, and preparation for AWS certification exams.
