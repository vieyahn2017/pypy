rm -rf microcloud
git clone http://10.0.0.252:10080/lanve/microcloud.git
sed -i 's/10.0.0.252/10.0.0.119/g' `grep 10.0.0.252 -rl /var/www/microcloud/handlers`
sed -i 's/127.0.0.1/10.0.0.119/g' `grep 127.0.0.1 -rl /var/www/microcloud/handlers`
sed -i 's/localhost/10.0.0.119/g' `grep localhost -rl /var/www/microcloud/handlers`
#sed -i '214,220d' /var/www/microcloud/handlers/Webservices/account/handler/UserHandler.py
echo 'pull done---------------------------------------------------------------------------------------------------end'
#sudo nginx -s reload
