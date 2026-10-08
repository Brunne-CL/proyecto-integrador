#!/bin/bash
# Una sola vez, dentro de la EC2 Amazon Linux 2023, como ec2-user.
set -eu

sudo dnf update -y
sudo dnf install -y docker
sudo systemctl enable --now docker
sudo usermod -aG docker "$USER"

echo "Docker quedó instalado. Cierra la sesión SSH y vuelve a entrar antes del primer despliegue."
