#! /bin/bash


python3.9 parameters-exec.py --experiment_num 1 --payload /home/keila/smartoceanplatform/ssp24/publisher/data \
 --publishers 1 --subscribers 1 --publishers_config /home/keila/smartoceanplatform/ssp24/publisher/configs/publisher.yml \
 --publishers_logs /home/keila/smartoceanplatform/ssp24/publisher/logs/test \
 --subscribers_logs /home/keila/smartoceanplatform/ssp24/subscriber/logs/test/ \
 --subscribers_config /home/keila/smartoceanplatform/ssp24/subscriber/configs/subscriber.yml

