#!/bin/bash


echo " Installing MySQL Operator CRDs"
kubectl apply -f https://raw.githubusercontent.com/mysql/mysql-operator/trunk/deploy/deploy-crds.yaml

echo " Install MySQL Operator"
kubectl apply -f https://raw.githubusercontent.com/mysql/mysql-operator/trunk/deploy/deploy-operator.yaml

echo " Creating Secret "
kubectl apply -f ~/project/mysql/secret.yaml

echo "Waiting for Operator to be ready "
sleep 10

echo " Creating InnoDB Cluster "
kubectl apply -f ~/project/mysql/mysql-cluster.yaml

echo "Done!"
