API_HOST=$(kubectl get service fund-transfer -n vinobank --output jsonpath='{.status.loadBalancer.ingress[0].hostname}')

if [ "$API_HOST" = "" ]; then
   echo Cannot get hostname from service
   exit 1
fi

if [ "$1" = "ui" ]; then
    MODE=""
else 
    MODE="--headless"
fi

echo $API_HOST
locust $MODE --host http://${API_HOST}:8080 --user 1
