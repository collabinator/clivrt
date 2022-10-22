# Setting up NVIDIA Riva server
This is a somewhat lengthy process that we don't currently automate due to NGC licensing and API keys.

## Prerequisites (https://docs.nvidia.com/deeplearning/riva/user-guide/docs/support-matrix.html)
* GPU with ~5600MB memory
* VRAM of 16GB+

## Simplified steps for how to setup the server to run locally.

1. You need docker installed
2. You need NVIDIA container toolkit (https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/install-guide.html#docker)
3. You need the NGC CLI tool (https://ngc.nvidia.com/setup/installers/cli)
4. You need your NGC API key configured (https://ngc.nvidia.com/setup/api-key)
5. Get the Riva quickstart from NGC (https://docs.nvidia.com/deeplearning/riva/user-guide/docs/quick-start-guide.html)
6. Edit config.sh to turn on asr and turn off services you don't want
7. bash riva_init.sh (this will take a while as it downloadds all the models)
8. bash riva_start.sh

## Using the service
Check out the protobuf interface here:
https://docs.nvidia.com/deeplearning/riva/user-guide/docs/reference/protos/protos.html#protobuf-docs-asr

See a tutrioal here:
https://github.com/nvidia-riva/python-clients/blob/main/tutorials/ASR.ipynb

Python Client repo:
https://github.com/nvidia-riva/python-clients