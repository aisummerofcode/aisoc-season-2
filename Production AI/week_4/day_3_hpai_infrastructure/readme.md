# High-Performance AI Engineering - Compute Infrastructure

## Accessing your GCP VM Instance via VS Code

1. **Install Prerequisites**:
   - Ensure you have [Visual Studio Code](https://code.visualstudio.com/) installed on your local machine.
   - In the `Extensions` tab on VS Code, search for and install the `Remote - SSH` extension for VS Code.

2. **Set Up SSH Key Pair**:
   - Open Git Bash or terminal and run the following command to generate an SSH key pair on your local machine (if you don’t already have one):
     ```bash
     ssh-keygen -t rsa -b 4096 -C "your_email@example.com"
     ```
   - 
   - Add the public key (`~/.ssh/id_rsa.pub`) as a separate key to the GCP VM's SSH keys via GCP Console. If you do not have access or authorization, work with your Cloud Admin to set this up for you.

3. **Configure SSH in VS Code**:
   - Open VS Code and use the Command Palette (`Ctrl+Shift+P`).
   - Add your VM as an SSH host:
     ```bash
     ssh username@your_vm_external_ip
     ```
   - Save this configuration in the `~/.ssh/config` file.

4. **Connect to the VM**:
   - Use the Command Palette (`Ctrl+Shift+P`) and select `Remote-SSH: Connect to Host...`
   - Choose your VM from the list to connect.
