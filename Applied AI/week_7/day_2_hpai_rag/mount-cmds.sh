# 1. Install GCSFuse

export GCSFUSE_REPO=gcsfuse-`lsb_release -c -s`
echo "deb https://packages.cloud.google.com/apt $GCSFUSE_REPO main" | sudo tee /etc/apt/sources.list.d/gcsfuse.list
curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
sudo apt-get update
sudo apt-get install gcsfuse

## Try the following if above fails

sudo apt-get update
sudo apt-get install -y curl gnupg lsb-release

## Add Google's GPG key
curl -fsSL https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg

## Add the repository
echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt gcsfuse-$(lsb_release -c -s) main" | sudo tee /etc/apt/sources.list.d/gcsfuse.list

## Update and install
sudo apt-get update
sudo apt-get install gcsfuse


# 2. Mount
sudo mkdir <mount-directory> # e.g., /mnt/storage-mnt/aistore
sudo gcsfuse -o allow_other --implicit-dirs --file-mode=777 --dir-mode=777 <gcs-bucket-name> <mount-directory>

## confirm mount
mount | grep gcsfuse # OR
mount | grep <mount-directory>


# 3. Auto mount on boot
## create script `mount-gcs.sh` for mountinhg
sudo nano /usr/local/bin/mount-gcs.sh 

## add the following
#!/bin/bash
/usr/bin/gcsfuse/ -o allow_other --implicit-dirs --file-mode=777 --dir-mode=777 <gcs-bucket-name> <mount-directory>

## make it executable
sudo chmod +x /usr/local/bin/mount-gcs.sh

## add to fstab
sudo nano /etc/fstab

## add the following line
gcs-bucket-name mount-directory gcsfuse rw,noauto,user,allow_other


# 4. Unmount
sudo umount <mount-directory>