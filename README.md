
# To set up an Nginx server for hosting Grandstream firmware updates, follow these steps:

##Update the package list:
```bash
sudo apt update
```
Install Nginx:
```bash
sudo apt install nginx
```
Create directory:
```bash
/var/www/grandstream-firmware and /var/www/grandstream-firmware/gs
```
Change  Nginx configuration file:
```bash
sudo nano /etc/nginx/sites-available/default
```
Сhange the file configuration to the following form, replacing your_server_domain_or_IP with the domain name or IP address of your server:
```bash
server {
    listen 80;
    server_name your_server_domain_or_IP;

    root /var/www/grandstream-firmware;
    index index.html;

    location / {
        try_files $uri $uri/ =404;
    }
}
```
Save the file and exit the editor.
Test the Nginx configuration for syntax errors:
```bash
sudo nginx -t
```
If the configuration is correct, reload Nginx:
```
sudo systemctl reload nginx
```
Now, you can upload the Grandstream firmware files to the /var/www/grandstream-firmware/gs directory on your server. The files will be accessible via http://your_server_domain_or_IP/gs
You can also use the following scripts to automatically download and extract the firmware:
To download all firmware:
```bash
python3 Download_firmware_Grandstream.py
```
To extract all firmware:
```bash
python3 Extract_firmware_Grandstream.py
```


